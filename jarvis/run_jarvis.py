"""
NAME: run_jarvis.py
DESCRIPTION: Python script to run my stream deck XL with custom icons and actions.
AUTHOR: NhoaKing
FINISH DATE: September 14th 2025 (Sunday)
NOTE: IMPORTANT TO EXECUTE THIS SCRIPT FROM LINUX TERMINAL, AND NOT FROM THE VSCODE TERMINAL, AS THE SYSTEM CALLS (ydotool, wmctrl, etc.) ARE NOT WORKING PROPERLY WHEN EXECUTED FROM VSCODE TERMINAL. IF WHEN TESTED FROM LINUX TERMINAL THE SCRIPT WORKS AS EXPECTED, THEN IT WILL WORK THE SAME WHEN EXECUTED FROM THE SYSTEM SERVICE.
"""

# Standard library imports for system operations and process management
import atexit      # Registers cleanup functions to run when Python interpreter exits
import time        # Provides time-related functions like sleep() for delays
import os          # Operating system interface for environment variables and file paths
import signal      # Handles Unix signals like SIGINT (Ctrl+C) for graceful shutdown
import sys         # System-specific parameters and functions, used for sys.exit()
from typing import Dict, Any

# Third-party StreamDeck library imports
# NOTE: This imports from the original Elgato StreamDeck repository in ../src/
# The StreamDeck library provides hardware abstraction for StreamDeck devices
from StreamDeck.DeviceManager import DeviceManager  # Factory class to discover and enumerate StreamDeck devices
# DeviceManager.enumerate() returns a list of connected StreamDeck objects
# Each StreamDeck object provides methods like: open(), close(), reset(), set_key_image(), set_key_callback()
# StreamDeck variants supported: StreamDeck (15 keys), StreamDeckMini (6 keys), StreamDeckXL (32 keys)

# Python standard library for modern path handling
from pathlib import Path  # Object-oriented filesystem paths, more robust than os.path

# Local jarvis module imports - these are our custom modules
from actions import actions                                      # Action functions triggered by key presses
from ui.render import initialize_render, create_layouts, render_layout  # Visual rendering and layout management
from ui.logic import initialize_logic, key_change               # Event handling and layout switching logic
from ui.lifecycle import initialize_lifecycle, cleanup, safe_exit       # Resource cleanup and graceful shutdown

# IMPORT STRATEGY EXPLANATION:
# We use relative imports (from actions import actions) instead of absolute imports
# because jarvis is a self-contained package. This approach has several advantages:
# 1. PORTABILITY: Code works regardless of where jarvis directory is placed
# 2. NO PYTHON PATH ISSUES: Doesn't require adding jarvis to sys.path or PYTHONPATH
# 3. CLEAR DEPENDENCIES: Makes it obvious which modules belong to jarvis vs external libraries
# 4. PACKAGE ISOLATION: Prevents naming conflicts with system-wide Python packages
#
# Alternative import strategies we could use but don't:
# - Absolute imports (import jarvis.actions.actions): Requires jarvis to be in PYTHONPATH
# - Star imports (from actions import *): Makes namespace pollution and unclear dependencies
# - Direct file imports (exec(open('actions.py').read())): Fragile and bypasses Python's import system

def load_config() -> None:
    """Load environment variables from config.env file into os.environ.

    This function implements a simple .env file parser that reads environment
    variables from a config.env file and loads them into the current process
    environment. This approach allows for runtime configuration without
    hardcoding paths or credentials in the source code.

    Process:
        1. Reads the config.env file line by line
        2. Skips empty lines and comments (lines starting with #)
        3. Parses KEY=VALUE pairs and adds them to environment variables
        4. Gracefully handles missing config files

    Performance:
        This function is called once at startup, so the file I/O overhead is
        negligible. We could cache the results, but since this runs only once,
        caching would add complexity without meaningful benefit.

    Note:
        The config.env file should be located in the same directory as this script.
        Each line should follow the format: KEY=VALUE
    """
    # Use pathlib for robust path handling - __file__ is the absolute path to this script
    config_path = Path(__file__).parent / "config.env"  # Looks for config.env in same directory as this script

    # Check if config file exists before trying to read it
    # This prevents FileNotFoundError and allows jarvis to run with default values
    if config_path.exists():
        # Open file with default UTF-8 encoding (Python 3 default)
        with open(config_path) as f:
            # Process each line in the config file
            for line in f:
                line = line.strip()  # Remove leading/trailing whitespace and newlines

                # Skip empty lines and comment lines (starting with #)
                # Also ensure line contains = sign for KEY=VALUE format
                if line and not line.startswith('#') and '=' in line:
                    # Split on first = only (in case value contains = characters)
                    # Example: "DATABASE_URL=postgres://user:pass=123@host/db"
                    key, value = line.split('=', 1)

                    # Strip whitespace from key and value, then add to environment
                    # os.environ is a dict-like object that interfaces with system environment
                    os.environ[key.strip()] = value.strip()

# Load configuration immediately when module is imported
# This ensures all configuration is available before any other code runs
load_config()

# Configuration constants - these can be customized via environment variables in config.env
# Using environment variables instead of hardcoded paths makes jarvis portable across different systems
# Get current user's home directory using pathlib (more robust than os.path.expanduser('~'))
USER_HOME: Path = Path.home()  # Returns Path object like /home/username or /Users/username

# Tool path configuration with fallback to system PATH
# ydotool is used for sending keyboard/mouse input to applications
# PERFORMANCE NOTE: We store the path once rather than calling os.getenv() repeatedly
YDOTOOL_PATH: str = os.getenv('YDOTOOL_PATH', 'ydotool')  # Defaults to 'ydotool' which relies on system PATH

# Projects directory configuration with intelligent default
# This is where the user's code projects are stored
PROJECTS_DIR: Path = Path(os.getenv('PROJECTS_DIR', USER_HOME / 'Zenith'))  # Defaults to ~/Zenith
# We convert to Path object for consistent path handling throughout the application

# Dynamic Obsidian vault configuration loading
# This allows for multiple Obsidian vaults to be configured via environment variables
# Pattern: OBSIDIAN_VAULT_<NAME>=<PATH> becomes OBSIDIAN_VAULTS[<name>] = <PATH>
OBSIDIAN_VAULTS: Dict[str, str] = {}  # Dictionary to store vault_name -> vault_path mappings

# Iterate through all environment variables to find Obsidian vault configurations
for key, value in os.environ.items():
    # Look for environment variables that follow the OBSIDIAN_VAULT_ prefix pattern
    if key.startswith('OBSIDIAN_VAULT_'):
        # Extract vault name from environment variable name
        # Example: OBSIDIAN_VAULT_JOURNAL -> vault_name = 'journal'
        vault_name = key.replace('OBSIDIAN_VAULT_', '').lower()  # Convert to lowercase for consistency

        # Store the vault path in our configuration dictionary
        OBSIDIAN_VAULTS[vault_name] = value

# PERFORMANCE OPTIMIZATION: This loop runs once at startup and processes only
# environment variables, which is very fast. The alternative would be to call
# os.getenv() for each known vault name, but this dynamic approach is more flexible

# Load password for keyring/password manager from environment
# This allows jarvis to type passwords securely without hardcoding them
# SECURITY NOTE: Environment variables are more secure than hardcoded passwords
# but still visible to other processes. For production use, consider using
# a proper secrets management system or encrypted password manager integration
KEYRING_PW: str = os.getenv('KEYRING_PW', '')  # Defaults to empty string if not configured

# Asset directory configuration
# These directories contain resources used by jarvis: fonts, icons, code snippets, and scripts
# We use os.path.join() for cross-platform compatibility (works on Windows, macOS, Linux)

# Font file path for StreamDeck key text rendering
# We use Roboto-Regular.ttf for clean, readable text on small StreamDeck keys
FONT_DIR: str = os.path.join(os.path.dirname(__file__), "assets", "font", "Roboto-Regular.ttf")

# Directory containing custom icons for StreamDeck keys
# Icons should be PNG format, ideally 96x96 pixels for StreamDeck XL
ICONS_DIR: str = os.path.join(os.path.dirname(__file__), "assets", "jarvisicons")

# Directory containing code snippets that can be inserted via StreamDeck
# Snippets are stored as .txt files and can contain boilerplate code, templates, etc.
SNIPPETS_DIR: str = os.path.join(os.path.dirname(__file__), "assets", "snippets")

# Directory containing bash scripts that can be executed via StreamDeck
# These scripts handle complex workflows like git operations, environment setup, etc.
BASHSCRIPTS_DIR: str = os.path.join(os.path.dirname(__file__), "assets", "bash_scripts")

# DESIGN DECISION: We use relative paths from the script location rather than
# absolute paths or environment variables. This keeps the assets bundled with
# the code and makes jarvis self-contained and portable.

# Global layout management variables
# These variables track the current state of the StreamDeck interface

# Dictionary to store all layout definitions
# Each layout is a dictionary mapping key numbers (0-31) to key configurations
# Example: layouts["main"][0] = {"icon": "spotify.png", "action": open_spotify}
layouts: Dict[str, Dict[int, Dict[str, Any]]] = {}  # Will be populated by create_layouts() after deck initialization

# Track which layout is currently displayed on the StreamDeck
# This variable is modified by the switch_layout() function in ui.logic
current_layout: str = "main"  # Start with the main layout as default

# PERFORMANCE CONSIDERATION: We use a global variable instead of passing layout
# state around because StreamDeck key callbacks need access to this information
# and the callback signature is fixed by the StreamDeck library

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
#
# WHY NOT USE ALTERNATIVES:
# - xdotool: Only works on X11, doesn't work on Wayland
# - PyAutoGUI: Higher level but less precise, may have timing issues
# - Direct X11/Wayland libraries: More complex and display-server specific
# - ydotool: Works on both X11 and Wayland, precise low-level control

def main() -> None:
    """Main entry point for the jarvis StreamDeck application.

    This function orchestrates the entire application startup process and handles
    the complete lifecycle of the StreamDeck integration. It implements a robust
    initialization sequence with retry logic for hardware discovery.

    Process:
        1. Initializes all modules with required configuration
        2. Discovers and connects to StreamDeck hardware with retry logic
        3. Sets up UI layouts and event handling
        4. Registers signal handlers for graceful shutdown
        5. Enters the main event loop

    Retry Mechanism:
        Uses a retry mechanism to handle temporary StreamDeck disconnections,
        USB timing issues, and device driver delays. Attempts connection for
        up to 5 minutes with 5-second intervals.

    Signal Handling:
        Registers handlers for SIGINT (Ctrl+C) and sets up atexit cleanup
        to ensure proper resource cleanup on exit.

    Raises:
        SystemExit: If StreamDeck hardware cannot be found after retry attempts
    """
    # Declare global variables that will be modified in this function
    # Using globals here is necessary because StreamDeck callbacks need access to these
    global deck, current_layout, layouts

    # Initialize all jarvis modules with configuration data
    # This dependency injection pattern allows modules to be tested independently
    # and keeps configuration centralized in this main module

    # Initialize actions module with tool paths and directories
    # This provides actions.py with access to ydotool, snippet files, etc.
    actions.initialize_actions(YDOTOOL_PATH,
           SNIPPETS_DIR, BASHSCRIPTS_DIR, PROJECTS_DIR, KEYCODES, KEYRING_PW)

    # Initialize rendering module with fonts, icons, and user-specific paths
    # This provides ui/render.py with access to visual assets and configuration
    initialize_render(FONT_DIR, ICONS_DIR, USER_HOME, PROJECTS_DIR, OBSIDIAN_VAULTS, KEYRING_PW)

    # Initialize lifecycle management with cleanup tools
    # This provides ui/lifecycle.py with access to ydotool for key release
    initialize_lifecycle(YDOTOOL_PATH, KEYCODES)

    # StreamDeck Discovery and Connection with Retry Logic
    # This section implements a robust connection strategy to handle:
    # 1. StreamDeck not plugged in at startup
    # 2. USB connection issues
    # 3. Device driver delays
    # 4. Temporary hardware disconnections

    # Configuration for retry mechanism
    interval_seconds = 5  # Wait 5 seconds between connection attempts
    max_retry_minutes = 5  # Give up after 5 minutes of trying

    # Initialize deck variable - will hold the StreamDeck object once connected
    deck = None

    # Calculate maximum number of attempts based on time constraints

    max_tries = (max_retry_minutes * 60) / interval_seconds
    current_tries = 0

    # Main connection retry loop
    while current_tries < max_tries:
        # Attempt to discover connected StreamDeck devices
        # DeviceManager().enumerate() scans USB devices for Elgato StreamDecks
        # This call may take a few hundred milliseconds as it queries USB devices
        decks = DeviceManager().enumerate()  # Returns list of StreamDeck device objects

        if decks:
            # At least one StreamDeck was found - use the first one
            # NOTE: This assumes only one StreamDeck is connected. For multiple devices,
            # we would need to identify them by serial number or model
            deck = decks[0]  # Get the first (and presumably only) StreamDeck
            # Uncommented debug print: print("Found connected stream deck")
            break  # Exit the retry loop immediately upon successful discovery
        else:
            # No StreamDeck found on this attempt - wait and try again
            # Uncommented debug print: print(f"Stream deck not found, retrying in {interval_seconds} seconds...")
            time.sleep(interval_seconds)  # Non-blocking sleep - allows Ctrl+C to interrupt
            current_tries += 1  # Increment attempt counter
    else:
        # This else clause executes only if the while loop completed without breaking
        # (i.e., we exhausted all retry attempts without finding a StreamDeck)
        # Uncommented debug print: print("Stream Deck not found.")
        sys.exit(1)  # Exit with error code 1 to indicate failure

    # PERFORMANCE OPTIMIZATION OPPORTUNITY:
    # The retry loop could be improved by:
    # 1. Using exponential backoff (1s, 2s, 4s, 8s, then 5s intervals)
    # 2. Caching USB device enumeration results
    # 3. Adding signal handling to allow graceful exit during retry
    # However, given that this runs only once at startup and StreamDecks are
    # typically always connected, the current simple approach is adequate

    # StreamDeck Hardware Initialization
    # Now that we have a StreamDeck object, we need to open the USB connection
    # and prepare the device for use

    deck.open()   # Open USB communication channel to the StreamDeck device
    deck.reset()  # Clear any existing images/state from previous sessions
    # reset() turns off all key LEDs and clears any displayed images

    # UI Layout Initialization
    # Create all layout definitions now that deck hardware is available
    # Some layout functions need access to the deck object (e.g., for toggle_mic)
    layouts = create_layouts(deck)  # Returns dictionary of layout_name -> layout_config

    # Initialize UI logic module with deck and layout state
    # This sets up the global state needed for key event handling
    initialize_logic(deck, layouts, "main")  # "main" is the initial layout to display

    # Render the initial layout to the StreamDeck
    # This displays icons and sets up the visual state of all 32 keys
    render_layout(deck, layouts[current_layout])  # current_layout is "main" at startup

    # Event Handler Registration
    # Register our key_change function to be called whenever any key is pressed or released
    # The StreamDeck library will call key_change(deck, key_number, is_pressed) for each event
    deck.set_key_callback(key_change)  # key_change is imported from ui.logic module

    # Signal Handler Registration for Graceful Shutdown
    # Set up handlers to clean up resources when the program is interrupted or terminated

    # Handle Ctrl+C (SIGINT) signal with graceful shutdown
    # Lambda function ignores the signal number and frame arguments
    signal.signal(signal.SIGINT, lambda _signum, _frame: safe_exit(deck))
    # Alternative: signal.signal(signal.SIGINT, lambda *args: safe_exit(deck))

    # Register cleanup function to run automatically when Python interpreter exits
    # This handles cases where the program exits normally or due to exceptions
    atexit.register(cleanup, deck)  # cleanup function is imported from ui.lifecycle

    # Enter Main Event Loop
    # Print status message to let user know the application is running
    print("Stream deck script is running. Press CTRL+C to quit.")

    # Pause the main thread indefinitely, waiting for signals
    # signal.pause() blocks until a signal is received (like SIGINT from Ctrl+C)
    # All actual work happens in the key_change callback function on separate threads
    signal.pause()  # This is an efficient way to keep the program alive without busy-waiting

    # PERFORMANCE CONSIDERATION:
    # signal.pause() is much more efficient than alternatives like:
    # - while True: time.sleep(1)  # Uses unnecessary CPU cycles
    # - input("Press Enter to quit")  # Requires user interaction
    # - threading.Event().wait()  # More complex and unnecessary for this use case

# Python script entry point
# This ensures main() only runs when the script is executed directly,
# not when imported as a module by other Python scripts
if __name__ == "__main__":
    main()  # Start the jarvis StreamDeck application

# DESIGN PATTERN EXPLANATION:
# The if __name__ == "__main__" pattern is a Python idiom that allows a script
# to be both executable and importable:
# 1. When run directly (python run_jarvis.py), __name__ equals "__main__"
# 2. When imported (import run_jarvis), __name__ equals "run_jarvis"
# This allows other modules to import functions from this file without
# automatically starting the StreamDeck application.