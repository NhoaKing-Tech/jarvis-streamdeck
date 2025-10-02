---
title: logic
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-21
---

# logic

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

## Functions

- [[#switch_layout|switch_layout()]]
- [[#key_change|key_change()]]
- [[#wrapper|wrapper()]]

## switch_layout

```python
def switch_layout():
```

Create a function that switches to the specified StreamDeck layout.

This function implements the Factory Pattern - it returns a callable that,
when executed, will switch the StreamDeck to display the specified layout.
This deferred execution approach is essential for layout definitions.

**Args:**
    layout_name (str): Name of the layout to switch to (e.g., "main", "python_layout")

**Returns:**
    callable: Function that executes the layout switch when called

DESIGN PATTERN: Factory Function with Closure
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

## key_change

```python
def key_change():
```

Event handler for StreamDeck key press and release events.

This function is registered as a callback with the StreamDeck library and
gets called automatically whenever any key is pressed or released.
It serves as the main entry point for all user interactions.

**Args:**
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

## wrapper

```python
def wrapper():
```

Inner function that performs the actual layout switch.

This function is returned by switch_layout() and called when
the corresponding StreamDeck key is pressed.

## Additional Code Context

Other contextual comments from the codebase:

- **Line 28:** CIRCULAR IMPORT ANALYSIS:
- **Line 29:** This module imports from render, and render imports from logic (for switch_layout)
- **Line 30:** This creates a circular dependency:
- **Line 31:** logic.py -> render.py -> logic.py
- **Line 33:** WHY THIS WORKS:
- **Line 34:** - Python handles circular imports if done at module level
- **Line 35:** - render.py imports switch_layout function, which is defined after this import
- **Line 36:** - Functions are only called at runtime, not import time
- **Line 37:** - No circular execution during module initialization
- **Line 39:** ALTERNATIVES TO AVOID CIRCULAR IMPORTS:
- **Line 40:** 1. Move switch_layout to separate module (utils.py)
- **Line 41:** 2. Use late imports (import inside functions)
- **Line 42:** 3. Restructure modules to eliminate circular dependency
- ... and 106 more contextual comments
