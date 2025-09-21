---
title: initialization
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-21
---

# initialization

-- GENERAL INFORMATION --
AUTHOR: NhoaKing (pseudonym for privacy)
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: initialization.py
-- DESCRIPTION --
Centralized initialization module for jarvis StreamDeck application.

This module consolidates the initialization of all jarvis modules (actions, render, lifecycle)
and contains shared configuration data like keycodes. This design provides:

1. Single source of truth for configuration
2. Simplified calling code - one function instead of multiple module-specific functions
3. Easier maintenance - add new config parameters in one location
4. Better error handling - centralized validation and error reporting
5. Reduced duplication - shared parameters and initialization logic defined once
6. General initialization pattern - all modules use the same init_module() approach

ARCHITECTURE:
- init_module(): General function that sets global variables in any module
- init_jarvis(): High-level function that initializes all modules
- KEYCODES: Centralized keycode mapping used by multiple modules
- get_keycodes(): Public API for accessing keycode mapping

USAGE:
from config.initialization import init_jarvis
init_jarvis(ydotool_path=..., projects_dir=..., ...)

This replaces the previous pattern of calling separate initialization functions
for each module (actions.initialize_actions, render.initialize_render, etc.).

AUTHOR: NhoaKing (pseudonym for privacy)

## Functions

- [[#init_module|init_module()]]
- [[#init_jarvis|init_jarvis()]]
- [[#get_keycodes|get_keycodes()]]

## init_module

```python
def init_module():
```

General-purpose module initialization function.

This function provides a standardized way to initialize any jarvis module
by setting its global configuration variables. This eliminates the need
for separate initialization functions in each module.

**Args:**
    module: The module object to initialize (e.g., actions, render, lifecycle)
    **config: Configuration key-value pairs to set as global variables

Design Benefits:
    - **Single initialization pattern**: All modules use the same approach
    - **Reduced code duplication**: No need for separate init functions per module
    - **Flexible configuration**: Any config parameter can be passed
    - **Type safety**: Modules define their own global variable types
    - **Easy to extend**: New modules follow the same pattern
    - **Consistent behavior**: Same initialization logic across all modules

Implementation:
    Uses setattr() to dynamically set module-level global variables.
    Only sets attributes that already exist in the target module (defined as globals).

Usage Examples:
    init_module(actions, YDOTOOL_PATH=path, KEYCODES=codes, ...)
    init_module(render_module, FONT_DIR=font, ICONS_DIR=icons, ...)
    init_module(lifecycle_module, YDOTOOL_PATH=path, KEYCODES=codes, ...)

**Note:**
    Modules must define their global variables (initialized to None) before
    calling this function. The function will only set attributes that already
    exist in the module's namespace via hasattr() check.

## init_jarvis

```python
def init_jarvis():
```

Initialize all jarvis modules with consolidated configuration.

This function centralizes the initialization of all jarvis modules, providing
a single point of configuration and setup. It uses the general init_module
function to reduce code duplication.

**Args:**
    ydotool_path (str): Path to ydotool executable for input simulation
    projects_dir (Path): User's main projects directory
    snippets_dir (Path): Directory containing code snippet text files
    bashscripts_dir (Path): Directory containing executable bash scripts
    user_home (Path, optional): User's home directory path
    font_dir (Path, optional): Path to font file for text rendering
    icons_dir (Path, optional): Directory containing icon files
    obsidian_vaults (dict, optional): Dictionary mapping vault names to paths
    keyring_pw (str, optional): Password for keyring/password manager access
    deck (Any, optional): StreamDeck device object for UI logic
    layouts (dict, optional): Layout definitions for UI logic
    current_layout (str, optional): Initial layout name for UI logic

Design Benefits:
    - **Single source of truth**: All configuration in one place
    - **Simplified calling**: One function call instead of multiple module-specific calls
    - **General initialization**: Uses the same init_module() pattern for all modules
    - **Better error handling**: Centralized validation and error reporting
    - **Reduced duplication**: Shared parameters and initialization logic
    - **Consistent pattern**: All modules follow the same initialization approach
    - **Easy to maintain**: Adding new modules or config parameters is straightforward

Initialization Flow:
    1. Validates required parameters
    2. Sets defaults for optional parameters
    3. Calls init_module() for each jarvis module with appropriate config
    4. Each module's global variables are set via setattr()

**Note:**
    This function must be called before any other jarvis modules are used,
    typically during application startup in core.application.

## get_keycodes

```python
def get_keycodes():
```

Get the keycode mapping dictionary.

This function provides access to the KEYCODES dictionary for modules
that need to reference keycodes but don't need full initialization.

**Returns:**
    dict: Mapping of key names to Linux input event codes

Usage:
    from config.initialization import get_keycodes
    keycodes = get_keycodes()
    ctrl_keycode = keycodes["CTRL"]

## Additional Code Context

Other contextual comments from the codebase:

- **Line 38:** Import the modules that need initialization
- **Line 44:** Linux input event keycode mapping for ydotool
- **Line 45:** These are the raw Linux input event keycodes that ydotool uses to simulate key presses
- **Line 46:** They correspond to the scancodes defined in /usr/include/linux/input-event-codes.h
- **Line 48:** TECHNICAL EXPLANATION:
- **Line 49:** - ydotool sends input events directly to the Linux kernel's input subsystem
- **Line 50:** - These are NOT ASCII codes or virtual key codes - they're hardware scancodes
- **Line 51:** - The mapping is consistent across all Linux systems regardless of keyboard layout
- **Line 52:** - Each key press sends two events: keycode:1 (press) and keycode:0 (release)
- **Line 54:** PERFORMANCE OPTIMIZATION: We define this as a constant dictionary rather than
- **Line 55:** computing keycodes dynamically because:
- **Line 56:** 1. Lookup is O(1) constant time
- **Line 57:** 2. No repeated computation during hotkey operations
- ... and 33 more contextual comments
