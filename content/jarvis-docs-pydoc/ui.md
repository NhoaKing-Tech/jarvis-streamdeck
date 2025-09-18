# Table of Contents

* [ui](#ui)
* [ui.logic](#ui.logic)
  * [current\_layout](#ui.logic.current_layout)
  * [layouts](#ui.logic.layouts)
  * [deck](#ui.logic.deck)
  * [initialize\_logic](#ui.logic.initialize_logic)
  * [switch\_layout](#ui.logic.switch_layout)
  * [key\_change](#ui.logic.key_change)
* [ui.render](#ui.render)
  * [initialize\_render](#ui.render.initialize_render)
  * [render\_keys](#ui.render.render_keys)
  * [render\_layout](#ui.render.render_layout)
  * [create\_layouts](#ui.render.create_layouts)
* [ui.lifecycle](#ui.lifecycle)
  * [YDOTOOL\_PATH](#ui.lifecycle.YDOTOOL_PATH)
  * [KEYCODES](#ui.lifecycle.KEYCODES)
  * [initialize\_lifecycle](#ui.lifecycle.initialize_lifecycle)
  * [release\_all\_keys](#ui.lifecycle.release_all_keys)
  * [clean\_stickykeys](#ui.lifecycle.clean_stickykeys)
  * [cleanup](#ui.lifecycle.cleanup)
  * [safe\_exit](#ui.lifecycle.safe_exit)

<a id="ui"></a>

# ui

<a id="ui.logic"></a>

# ui.logic

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

<a id="ui.logic.current_layout"></a>

#### current\_layout

String identifier for the currently displayed layout

<a id="ui.logic.layouts"></a>

#### layouts

Will be populated with layout configurations from render module

<a id="ui.logic.deck"></a>

#### deck

Will hold the StreamDeck instance for key updates and rendering

<a id="ui.logic.initialize_logic"></a>

#### initialize\_logic

```python
def initialize_logic(deck_instance, layouts_dict, initial_layout="main")
```

Initialize the UI logic module with required state from main application.

This function implements dependency injection pattern - all UI state needed
by the logic module is passed in explicitly rather than being imported or
created internally. It sets up the global state used by event handlers.

**Arguments**:

- `deck_instance` - StreamDeck device object for hardware interaction
- `layouts_dict` _dict_ - Complete layout definitions mapping layout names to key configs
- `initial_layout` _str_ - Name of the layout to display initially. Defaults to "main"
  
  Initialization Sequence:
  This function is called during application startup after:
  
  1. StreamDeck hardware is discovered and opened
  2. Layout definitions are created (in render.create_layouts())
  3. Before key event callbacks are registered
  
  State Management:
  Sets up the global state that will be used by:
  
  - key_change() event handler
  - switch_layout() layout transition function
  - Any other UI logic functions
  
  Error Handling:
  No explicit error handling because this is called once during controlled
  startup sequence. Invalid parameters would be caught immediately during
  testing. Failure here should crash the application (fail-fast principle).

<a id="ui.logic.switch_layout"></a>

#### switch\_layout

```python
def switch_layout(layout_name)
```

Create a function that switches to the specified StreamDeck layout.

This function implements the Factory Pattern - it returns a callable that,
when executed, will switch the StreamDeck to display the specified layout.
This deferred execution approach is essential for layout definitions.

**Arguments**:

- `layout_name` _str_ - Name of the layout to switch to (e.g., "main", "python_layout")
  

**Returns**:

- `callable` - Function that executes the layout switch when called
  
  DESIGN PATTERN: Factory Function with Closure
  This pattern is used because:
  1. DEFERRED EXECUTION: Layout definitions need callable references, not immediate execution
  2. PARAMETER BINDING: Captures layout_name in closure for later use
  3. CLEAN SYNTAX: Avoids lambda expressions in layout dictionaries
  4. REUSABILITY: Same function can create switchers for different layouts
  
  USAGE IN LAYOUT DEFINITIONS:
  Instead of:
- `0` - {"icon": "back.png", "action": lambda: switch_to_main()}
  We can write:
- `0` - {"icon": "back.png", "action": switch_layout("main")}
  
  The switch_layout() call happens during layout creation (returns a function),
  but the actual switching happens when the key is pressed (function is called).
  
  CLOSURE EXPLANATION:
  The returned wrapper function "closes over" the layout_name parameter,
  meaning it remembers the value even after switch_layout() has returned.
  This is a powerful feature of Python functions.

<a id="ui.logic.key_change"></a>

#### key\_change

```python
def key_change(deck_instance, key, state)
```

Event handler for StreamDeck key press and release events.

This function is registered as a callback with the StreamDeck library and
gets called automatically whenever any key is pressed or released.
It serves as the main entry point for all user interactions.

**Arguments**:

- `deck_instance` - StreamDeck device object (provided by library)
- `key` _int_ - Key number that was pressed (0-31 for StreamDeck XL)
- `state` _bool_ - True for key press, False for key release
  
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

<a id="ui.render"></a>

# ui.render

Rendering functions for StreamDeck keys.
This module handles the visual appearance of StreamDeck buttons and layout management.

<a id="ui.render.initialize_render"></a>

#### initialize\_render

```python
def initialize_render(font_dir,
                      icons_dir,
                      user_home=None,
                      projects_dir=None,
                      obsidian_vaults=None,
                      keyring_pw=None)
```

Initialize the render module with required directories and paths.

This function sets up the global configuration variables needed by the render
module to create layouts and render StreamDeck keys. It implements dependency
injection to keep configuration centralized.

**Arguments**:

- `font_dir` _str_ - Path to font file for text rendering on keys
- `icons_dir` _str_ - Directory containing icon files for StreamDeck keys
- `user_home` _Path, optional_ - User's home directory path
- `projects_dir` _Path, optional_ - User's main projects directory
- `obsidian_vaults` _dict, optional_ - Dictionary mapping vault names to paths
- `keyring_pw` _str, optional_ - Password for keyring access
  

**Notes**:

  This function must be called before any render functions are used,
  typically during application startup.

<a id="ui.render.render_keys"></a>

#### render\_keys

```python
def render_keys(deck,
                key,
                label=None,
                icon=None,
                color="black",
                labelcolor="white")
```

Render the visual appearance of a StreamDeck key with icon and/or text.

This function handles the visual rendering of StreamDeck buttons, supporting
multiple display modes: icon only, text only, icon with text, or solid color.
It automatically handles text wrapping, icon scaling, and layout positioning.

**Arguments**:

- `deck` - StreamDeck device object
- `key` _int_ - Key index (0-31 for StreamDeck XL)
- `label` _str, optional_ - Text to display on the key
- `icon` _str, optional_ - Filename of icon to display (must be in ICONS_DIR)
- `color` _str_ - Background color when no icon used. Defaults to "black"
- `labelcolor` _str_ - Text color for labels. Defaults to "white"
  
  Display Modes:
  1. **Icon and label**: Icon at top, label at bottom (truncated if too long)
  2. **Only label**: Centered text, wrapped to multiple lines if needed
  3. **Only icon**: Maximized icon space with minimal margins
  4. **Neither**: Solid color background (red if color not specified, indicates error)
  
  Text Handling:
  - Automatically calculates character width for proper text wrapping
  - Truncates long labels with "..." when combined with icons
  - Centers text both horizontally and vertically
  - Uses custom font with fallback to system default
  
  Icon Handling:
  - Scales icons to fit key dimensions with appropriate margins
  - Handles missing icon files gracefully with fallback colors
  - Supports PNG format icons optimized for 96x96 pixel keys
  

**Raises**:

- `RuntimeError` - If render module not initialized

<a id="ui.render.render_layout"></a>

#### render\_layout

```python
def render_layout(deck, layout)
```

Render all keys for the given layout configuration.

This function updates the entire StreamDeck display by rendering each key
according to its configuration in the provided layout dictionary. It first
clears the existing display, then renders each configured key.

**Arguments**:

- `deck` - StreamDeck device object
- `layout` _dict_ - Layout dictionary mapping key numbers to configurations
  
  Layout Structure:
  The layout dictionary maps key numbers (0-31) to configuration dictionaries:
    ```
    {
        0: {"icon": "spotify.png", "action": some_function},
        1: {"label": "Terminal", "color": "blue", "action": another_function},
        ...
    }
    ```
  
  Process:
  1. Validates deck is open and available
  2. Resets/clears all existing key displays
  3. Sets brightness to 100%
  4. Renders each key according to its configuration
  
  Configuration Keys:
  - **label**: Text to display on the key
  - **icon**: Icon filename (from ICONS_DIR)
  - **color**: Background color
  - **labelcolor**: Text color
  - **action**: Function to call when key is pressed (not used in rendering)
  

**Notes**:

  Only renders visual elements. Key actions are handled by the logic module.

<a id="ui.render.create_layouts"></a>

#### create\_layouts

```python
def create_layouts(deck)
```

Create all layout definitions for the StreamDeck interface.

This function generates all layout configurations used by the jarvis application.
Each layout defines the complete key mapping for a specific mode or context
(main, git tools, conda commands, etc.).

**Arguments**:

- `deck` - StreamDeck device object (needed for some dynamic key functions)
  

**Returns**:

- `dict` - Dictionary mapping layout names to layout configurations
  
  Layout Structure:
  Each layout maps key positions (0-31) to configuration dictionaries:
    ```
    {
        "main": {
            0: {"icon": "project1.png", "action": open_vscode("/path")},
            1: {"label": "Terminal", "action": hk_terminal},
            ...
        },
        "git_layout": {
            0: {"icon": "back.png", "action": switch_layout("main")},
            ...
        }
    }
    ```
  
  Available Layouts:
  - **main**: Primary interface with projects, tools, and navigation
  - **apps**: Application launchers (Spotify, YouTube, etc.)
  - **git_layout**: Git operations and code snippets
  - **python_layout**: Python development tools
  - **conda_layout**: Conda environment management commands
  - **terminal_layout**: Terminal and command-line tools
  - Language-specific layouts: html_layout, css_layout, javascript_layout
  
  Dynamic Elements:
  Some layouts include dynamic elements that depend on configuration:
  - Project paths from PROJECTS_DIR
  - Obsidian vault paths from OBSIDIAN_VAULTS
  - User-specific directories and tools
  

**Raises**:

- `RuntimeError` - If render module not initialized with required paths

<a id="ui.lifecycle"></a>

# ui.lifecycle

UI lifecycle management for StreamDeck.

This module handles resource cleanup and graceful shutdown for the jarvis application.
It ensures that system resources are properly released when the application exits,
whether through normal shutdown, interrupt signals, or unexpected crashes.

Key responsibilities:
- Release any "stuck" keyboard keys that might remain pressed
- Close StreamDeck hardware connection cleanly
- Provide graceful shutdown mechanisms
- Prevent resource leaks and hardware conflicts

This module is critical for system stability because ydotool key events
can leave the system in an unusable state if not properly cleaned up.

<a id="ui.lifecycle.YDOTOOL_PATH"></a>

#### YDOTOOL\_PATH

Will be set to system ydotool path from main configuration

<a id="ui.lifecycle.KEYCODES"></a>

#### KEYCODES

Will be set to the same keycode mapping used throughout jarvis

<a id="ui.lifecycle.initialize_lifecycle"></a>

#### initialize\_lifecycle

```python
def initialize_lifecycle(ydotool_path, keycodes)
```

Initialize the lifecycle module with required configuration.

This function sets up the module with the configuration needed for
cleanup operations. It's called once during application startup to
ensure cleanup tools are available for shutdown scenarios.

**Arguments**:

- `ydotool_path` _str_ - Path to ydotool executable for key operations
- `keycodes` _dict_ - Mapping of key names to Linux input event codes
  
  Initialization Timing:
  Called early in the startup sequence, after configuration is loaded
  but before StreamDeck operations begin. This ensures cleanup tools
  are available if needed during startup or shutdown.
  
  Error Handling:
  No validation is performed here because this is called during
  controlled startup with validated config. Invalid configuration
  would be caught during actual cleanup attempts.

<a id="ui.lifecycle.release_all_keys"></a>

#### release\_all\_keys

```python
def release_all_keys()
```

Release all keyboard keys to prevent "sticky key" problems.

This function sends key release events for all keys defined in KEYCODES
to ensure no keys remain "stuck" in the pressed state when jarvis exits.
This is essential because ydotool can leave keys in pressed state if
the application crashes or exits unexpectedly.

Sticky Key Problem:
ydotool sends low-level input events to the Linux kernel. If a key press
event is sent but the corresponding key release event is never sent
(due to application crash, kill signal, etc.), the key remains "pressed"
from the system's perspective. This can make the system unusable.

Solution Strategy:
Send release events (keycode:0) for all possible keys that jarvis might
have pressed. This is safe because:

- Releasing an already-released key has no effect
- Better to release too many keys than leave any stuck
- The overhead is minimal (small command, runs once at exit)

Called During:
- Normal application shutdown (atexit handler)
- Signal-based shutdown (SIGINT/Ctrl+C handler)
- Manual cleanup calls
- Recovery scenarios (reset_jarvis.py)

**Raises**:

- `RuntimeError` - If lifecycle module not initialized
  

**Notes**:

  Validates initialization but doesn't handle ydotool execution errors
  because this is typically called during shutdown when error handling
  options are limited.

<a id="ui.lifecycle.clean_stickykeys"></a>

#### clean\_stickykeys

Set to False initially - cleanup not yet performed

<a id="ui.lifecycle.cleanup"></a>

#### cleanup

```python
def cleanup(deck=None)
```

Perform complete application cleanup and resource release.

This function handles all necessary cleanup operations when jarvis shuts down.
It's designed to be safe to call multiple times and from different contexts
(normal exit, signal handlers, exception handlers).

**Arguments**:

- `deck` - Optional StreamDeck device object to clean up
  
  Cleanup Operations:
  1. Release any stuck keyboard keys via ydotool
  2. Reset StreamDeck display (clear all keys)
  3. Close StreamDeck hardware connection
  4. Prevent duplicate cleanup attempts
  
  Design Principles:
  - **Idempotent**: Safe to call multiple times
  - **Defensive**: Handles errors gracefully
  - **Complete**: Cleans up all acquired resources
  - **Fast**: Minimal delay during shutdown
  
  Calling Contexts:
  - Registered with atexit for normal Python shutdown
  - Called from signal handlers (Ctrl+C)
  - Called manually in exception handlers
  - Called from reset/recovery scripts
  

**Notes**:

  Uses a global flag to prevent duplicate cleanup from multiple triggers.
  Cleanup errors are reported but don't prevent other cleanup steps.

<a id="ui.lifecycle.safe_exit"></a>

#### safe\_exit

```python
def safe_exit(deck=None)
```

Perform cleanup and exit the application gracefully.

This function provides a single point for graceful application shutdown.
It ensures all cleanup operations are performed before terminating the
Python process.

**Arguments**:

- `deck` - Optional StreamDeck device object to clean up before exit
  
  Exit Code:
  Uses exit code 0 to indicate successful/intentional shutdown.
  This is important for:
  
  - System service management (systemd, etc.)
  - Process monitoring tools
  - Shell scripts that check exit codes
  - Automated restart logic
  
  Usage Contexts:
  - Signal handlers (Ctrl+C interrupt)
  - Error recovery after unrecoverable errors
  - Manual shutdown commands
  - Graceful restart scenarios
  
  Shutdown Sequence:
  1. Run complete cleanup (release keys, close hardware)
  2. Exit Python interpreter with success code
  3. OS reclaims any remaining resources
  

**Notes**:

  This function does not return - it terminates the Python process.

