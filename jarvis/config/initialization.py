"""
-- GENERAL INFORMATION --
AUTHOR: NhoaKing
PROJECT: jarvis-streamdeck
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

AUTHOR: NhoaKing
"""

from pathlib import Path
from typing import Dict, Optional, Any

# Import the modules that need initialization
from jarvis.actions import actions
import jarvis.ui.render as render_module
import jarvis.core.logic as logic_module
import jarvis.core.lifecycle as lifecycle_module

# Linux input event keycode mapping for ydotool
# These are the raw Linux input event keycodes that ydotool uses to simulate key presses
# They correspond to the scancodes defined in /usr/include/linux/input-event-codes.h
#
# TECHNICAL EXPLANATION:
# - ydotool sends input events directly to the Linux kernel's input subsystem
# - These are NOT ASCII codes or virtual key codes - they're hardware scancodes
# - The mapping is consistent across all Linux systems regardless of keyboard layout
# - Each key press sends two events: keycode:1 (press) and keycode:0 (release)
#
# PERFORMANCE OPTIMIZATION: We define this as a constant dictionary rather than
# computing keycodes dynamically because:
# 1. Lookup is O(1) constant time
# 2. No repeated computation during hotkey operations
# 3. Makes the mapping explicit and debuggable
KEYCODES: Dict[str, int] = {
    # Letter keys (QWERTY layout positions, not alphabetical)
    "A": 30, "B": 48, "C": 46, "D": 32, "E": 18,
    "F": 33, "G": 34, "H": 35, "I": 23, "J": 36,
    "K": 37, "L": 38, "M": 50, "N": 49, "O": 24,
    "P": 25, "Q": 16, "R": 19, "S": 31, "T": 20,
    "U": 22, "V": 47, "W": 17, "X": 45, "Y": 21,
    "Z": 44,

    # Number row keys (1-9, 0)
    "1": 2, "2": 3, "3": 4, "4": 5, "5": 6,
    "6": 7, "7": 8, "8": 9, "9": 10, "0": 11,

    # Function keys (F1-F12)
    "F1": 59, "F2": 60, "F3": 61, "F4": 62,
    "F5": 63, "F6": 64, "F7": 65, "F8": 66,
    "F9": 67, "F10": 68, "F11": 87, "F12": 88,

    # Modifier keys (both left and right variants)
    "CTRL": 29, "SHIFT": 42, "ALT": 56,           # Left-side modifiers
    "RIGHTCTRL": 97, "RIGHTSHIFT": 54, "RIGHTALT": 100,  # Right-side modifiers
    "SUPER": 125,  # Super/Windows/Cmd key

    # Special keys
    "ESC": 1, "TAB": 15, "CAPSLOCK": 58,
    "SPACE": 57, "ENTER": 28, "BACKSPACE": 14,

    # Navigation keys (arrow keys and related)
    "UP": 103, "DOWN": 108, "LEFT": 105, "RIGHT": 106,
    "HOME": 102, "END": 107, "PAGEUP": 104, "PAGEDOWN": 109,
    "INSERT": 110, "DELETE": 111,

    # Symbol/punctuation keys
    "MINUS": 12, "EQUAL": 13,                    # - and = keys
    "LEFTBRACE": 26, "RIGHTBRACE": 27,          # [ and ] keys
    "BACKSLASH": 43, "SEMICOLON": 39,           # \ and ; keys
    "APOSTROPHE": 40, "GRAVE": 41,              # ' and ` keys
    "COMMA": 51, "DOT": 52, "SLASH": 53,        # , . and / keys
}

def init_module(module: Any, **config) -> None:
    """General-purpose module initialization function.

    This function provides a standardized way to initialize any jarvis module
    by setting its global configuration variables. This eliminates the need
    for separate initialization functions in each module.

    Args:
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

    Note:
        Modules must define their global variables (initialized to None) before
        calling this function. The function will only set attributes that already
        exist in the module's namespace via hasattr() check.
    """
    for key, value in config.items():
        if hasattr(module, key):
            setattr(module, key, value)
        else:
            # Optional: warn about unrecognized config keys
            pass

def init_jarvis(
    # Core system paths
    ydotool_path: str,

    # Project and user paths
    projects_dir: Path,
    snippets_dir: Path,
    bashscripts_dir: Path,
    user_home: Optional[Path] = None,

    # UI assets
    font_dir: Optional[Path] = None,
    icons_dir: Optional[Path] = None,

    # User data
    obsidian_vaults: Optional[Dict[str, str]] = None,
    keyring_pw: Optional[str] = None,

    # StreamDeck state (for logic module)
    deck: Optional[Any] = None,
    layouts: Optional[Dict[str, Dict[int, Dict[str, Any]]]] = None,
    current_layout: Optional[str] = None
) -> None:
    """Initialize all jarvis modules with consolidated configuration.

    This function centralizes the initialization of all jarvis modules, providing
    a single point of configuration and setup. It uses the general init_module
    function to reduce code duplication.

    Args:
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

    Note:
        This function must be called before any other jarvis modules are used,
        typically during application startup in core.application.
    """

    # Validate required parameters
    if not ydotool_path:
        raise ValueError("ydotool_path is required for jarvis initialization")
    if not projects_dir:
        raise ValueError("projects_dir is required for jarvis initialization")
    if not snippets_dir:
        raise ValueError("snippets_dir is required for jarvis initialization")
    if not bashscripts_dir:
        raise ValueError("bashscripts_dir is required for jarvis initialization")

    # Set defaults for optional parameters
    obsidian_vaults = obsidian_vaults or {}
    keyring_pw = keyring_pw or ""

    # Initialize each module using the general init_module function
    # Order matters: actions first (core functionality), then render/logic (UI), then lifecycle (cleanup)

    # 1. Initialize actions module - provides core functionality for key press handlers
    init_module(
        actions,
        YDOTOOL_PATH=ydotool_path,
        SNIPPETS_DIR=snippets_dir,
        BASHSCRIPTS_DIR=bashscripts_dir,
        PROJECTS_DIR=projects_dir,
        KEYCODES=KEYCODES,
        KEYRING_PW=keyring_pw
    )

    # 2. Initialize render module - handles UI rendering and layout management
    # Only initialize if font_dir and icons_dir are provided
    if font_dir and icons_dir:
        init_module(
            render_module,
            FONT_DIR=font_dir,
            ICONS_DIR=icons_dir,
            USER_HOME=user_home,
            PROJECTS_DIR=projects_dir,
            OBSIDIAN_VAULTS=obsidian_vaults,
            KEYRING_PW=keyring_pw
        )

    # 3. Initialize logic module - handles UI state management and event handling
    # Only initialize if deck and layouts are provided
    if deck and layouts:
        init_module(
            logic_module,
            deck=deck,
            layouts=layouts,
            current_layout=current_layout or "main"
        )

    # 4. Initialize lifecycle module - handles cleanup and resource management
    init_module(
        lifecycle_module,
        YDOTOOL_PATH=ydotool_path,
        KEYCODES=KEYCODES
    )

def get_keycodes() -> Dict[str, int]:
    """Get the keycode mapping dictionary.

    This function provides access to the KEYCODES dictionary for modules
    that need to reference keycodes but don't need full initialization.

    Returns:
        dict: Mapping of key names to Linux input event codes

    Usage:
        from config.initialization import get_keycodes
        keycodes = get_keycodes()
        ctrl_keycode = keycodes["CTRL"]
    """
    return KEYCODES.copy()  # Return a copy to prevent external modification