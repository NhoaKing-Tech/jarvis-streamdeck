"""
-- GENERAL INFORMATION --
AUTHOR: NhoaKing
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: logic.py
-- DESCRIPTION -- 
UI logic for StreamDeck event handling and layout management.

This module serves as the "controller" layer in the Model-View-Controller pattern:
- Model: Layout definitions and application state
- View: StreamDeck key rendering and visual feedback
- Controller: This module - handles user input and coordinates state changes

Responsibilities:
- Process StreamDeck key press/release events
- Manage layout switching and state transitions
- Coordinate between user actions and visual updates
- Maintain global UI state (current layout, deck reference)

The module uses global state variables because StreamDeck callback functions
have fixed signatures and cannot receive additional parameters. This is a
common pattern in event-driven GUI programming.
"""

from jarvis.ui.render import render_layout
from typing import Optional, Dict, Any, Callable

# CIRCULAR IMPORT ANALYSIS:
# This module imports from render, and render imports from logic (for switch_layout)
# This creates a circular dependency:
# logic.py -> render.py -> logic.py
#
# WHY THIS WORKS:
# - Python handles circular imports if done at module level
# - render.py imports switch_layout function, which is defined after this import
# - Functions are only called at runtime, not import time
# - No circular execution during module initialization
#
# ALTERNATIVES TO AVOID CIRCULAR IMPORTS:
# 1. Move switch_layout to separate module (utils.py)
# 2. Use late imports (import inside functions)
# 3. Restructure modules to eliminate circular dependency
# 4. Pass layout data as parameters to render_layout function
#
# Current structure is acceptable because:
# - Imports are clean and obvious
# - No runtime issues or import errors
# - Functions are cohesive within their modules

# Global configuration variables - set by config.initialization.init_module()
# These are initialized to None and set during application startup via centralized initialization

# Current active layout name (e.g., "main", "python_layout", "git_layout")
current_layout: Optional[str] = None  # String identifier for the currently displayed layout

# Dictionary containing all layout definitions
# Structure: {layout_name: {key_number: {"icon": "file.png", "action": function, ...}}}
layouts: Optional[Dict[str, Dict[int, Dict[str, Any]]]] = None  # Will be populated with layout configurations

# Reference to the StreamDeck hardware device object
deck: Optional[Any] = None  # Will hold the StreamDeck instance for key updates and rendering

# DESIGN PATTERN: Module-level Configuration with General Initialization
# =======================================================================
# This module now uses the general init_module() function from config.initialization
# instead of having its own initialization function. This reduces code duplication
# and provides a consistent initialization pattern across all jarvis modules.
#
# INITIALIZATION:
# The config.initialization.init_module() function sets the global variables
# (deck, layouts, current_layout) by calling setattr(module, key, value) for each configuration parameter.

# GLOBAL STATE JUSTIFICATION:
# StreamDeck library uses callback functions with fixed signatures:
# def key_callback(deck, key, state) - cannot pass additional parameters
#
# Therefore, we need global state accessible from callback functions.
# Alternative approaches considered:
# 1. Class-based approach: More OOP but adds complexity for this use case
# 2. Closure with state: Would require restructuring callback registration
# 3. Module-level state: Current approach - simple and effective
#
# THREAD SAFETY:
# StreamDeck callbacks may run on separate threads, but in practice:
# - Key events are sequential (can't press two keys simultaneously)
# - Layout switching is atomic (single assignment)
# - No complex shared state manipulation
# So thread safety is not a concern for this application

def switch_layout(layout_name: str) -> Callable[[], None]:
    """Create a function that switches to the specified StreamDeck layout.

    This function uses a Closure Pattern - it returns a callable that,
    when executed, will switch the StreamDeck to display the specified layout.
    This deferred execution approach is essential for layout definitions.

    Args:
        layout_name (str): Name of the layout to switch to (e.g., "main", "python_layout")

    Returns:
        callable: Function that executes the layout switch when called

    DESIGN PATTERN: Closure with Deferred Execution
    This pattern is used because:
    1. DEFERRED EXECUTION: Layout definitions need callable references, not immediate execution
    2. PARAMETER BINDING: Captures layout_name in closure for later use
    3. CLEAN SYNTAX: Avoids lambda expressions in layout dictionaries
    4. REUSABILITY: Same function can create switchers for different layouts

    USAGE IN LAYOUT DEFINITIONS:
    Instead of:
        0: {"icon": "back.png", "action": lambda: switch_to_main()}
    We can write:
        0: {"icon": "back.png", "action": switch_layout("main")}

    The switch_layout() call happens during layout creation (returns a function),
    but the actual switching happens when the key is pressed (function is called).

    CLOSURE EXPLANATION:
    The returned wrapper function "closes over" the layout_name parameter,
    meaning it remembers the value even after switch_layout() has returned.
    This is a powerful feature of Python functions.
    """
    def wrapper():
        """Inner function that performs the actual layout switch.

        This function is returned by switch_layout() and called when
        the corresponding StreamDeck key is pressed.
        """
        global current_layout

        # Validate that we have layouts available and the target layout exists
        if layouts and layout_name in layouts:
            # Update global state to track new current layout
            current_layout = layout_name

            # Render the new layout to the StreamDeck hardware
            # This updates all 32 keys with new icons, labels, and actions
            render_layout(deck, layouts[layout_name])

            # PERFORMANCE NOTE:
            # render_layout() is fast (~10-50ms) because it only updates changed keys
            # Full layout switch is much faster than individual key updates

        else:
            # Handle error case: layout not found
            # In production, could log error or show error message on StreamDeck
            # For now, silently ignore invalid layout switches
            pass

    # Return the wrapper function for later execution
    return wrapper

    # ALTERNATIVE IMPLEMENTATIONS CONSIDERED:
    # 1. Immediate execution: switch_layout_now(layout_name)
    #    - Simpler but doesn't work with layout definitions
    # 2. Lambda expressions: lambda: switch_to_layout(layout_name)
    #    - More concise but less readable in complex layouts
    # 3. Class-based callbacks: LayoutSwitcher(layout_name)
    #    - More OOP but overkill for this simple use case
    #
    # Closure pattern chosen for balance of simplicity and functionality

def key_change(_deck_instance: Any, key: int, state: bool) -> None:
    """Event handler for StreamDeck key press and release events.

    This function is registered as a callback with the StreamDeck library and
    gets called automatically whenever any key is pressed or released.
    It serves as the main entry point for all user interactions.

    Args:
        deck_instance: StreamDeck device object (provided by library)
        key (int): Key number that was pressed (0-31 for StreamDeck XL)
        state (bool): True for key press, False for key release

    CALLBACK REGISTRATION:
    This function is registered with: deck.set_key_callback(key_change)
    The StreamDeck library calls it on a separate thread for each key event.

    EVENT FILTERING:
    - Only processes key PRESS events (state=True), ignores releases
    - Only processes keys that exist in the current layout
    - Validates that all required state is available

    ERROR HANDLING:
    Uses broad exception handling because:
    - Action functions come from user-defined layout configurations
    - Some actions might fail due to external factors (missing files, network issues)
    - StreamDeck should remain responsive even if individual actions fail
    - Silent failure prevents error dialogs from disrupting workflow

    PERFORMANCE CONSIDERATIONS:
    - Key event processing should be fast (<10ms) for responsive UI
    - Action execution happens on callback thread, not main thread
    - Heavy operations (file I/O, network) are handled by action functions
    """
    # VALIDATION: Only process key press events (ignore releases)
    # Key releases (state=False) are not used for actions in this application
    if not state:
        return

    # VALIDATION: Ensure all required state is available
    # Check for:
    # - layouts: Layout definitions have been loaded
    # - current_layout: A layout is currently active
    # - key in layout: The pressed key is defined in current layout
    if not (layouts and current_layout and key in layouts[current_layout]):
        return  # Ignore undefined keys or uninitialized state

    # EXECUTE KEY ACTION
    try:
        # Retrieve the action function for this key from current layout
        key_config = layouts[current_layout][key]
        action_function = key_config["action"]

        # Execute the action function
        # This might be:
        # - Application launcher: open_vscode("/path/to/project")
        # - Layout switcher: switch_layout("python_layout")
        # - Text typer: type_text("Hello World")
        # - System control: toggle_mic(deck, key)
        action_function()

        # ACTION EXECUTION NOTES:
        # - Actions run on the StreamDeck callback thread
        # - Non-blocking actions (subprocess.Popen) return immediately
        # - Blocking actions (subprocess.run) will delay next key presses
        # - Most actions are designed to be non-blocking for responsiveness

    except Exception:
        # BROAD EXCEPTION HANDLING:
        # Catch all exceptions to prevent StreamDeck becoming unresponsive
        # In production environment, could:
        # - Log error details for debugging
        # - Show error indicator on StreamDeck
        # - Send error to monitoring system

        # For now, fail silently to maintain user experience
        # The alternative would be showing error dialogs which would
        # interrupt the user's workflow
        pass

        # DEBUGGING AID:
        # Uncomment for development/debugging:
        # print(f"Error executing action for key {key}: {e}")
        # import traceback
        # traceback.print_exc()

    # THREADING CONSIDERATIONS:
    # This function runs on StreamDeck library's callback thread, not main thread
    # Most actions spawn separate processes (subprocess.Popen) so they don't block
    # Some actions update StreamDeck state (toggle_mic) which is thread-safe
    # Layout switches modify global state but are atomic operations

    # PERFORMANCE OPTIMIZATION OPPORTUNITIES:
    # - Cache frequently used action functions
    # - Debounce rapid key presses
    # - Preload action dependencies
    # - Use async/await for I/O bound actions
    # However, current performance is adequate for typical usage patterns