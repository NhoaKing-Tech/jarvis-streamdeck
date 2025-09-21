"""
NAME: reset_jarvis.py
DESCRIPTION: Stream Deck Reset Script
AUTHOR: NhoaKing (pseudonym for privacy)
START DATE: September 4th 2025
VERSION: 1.0
This script resets the deck to a clean state.
With this script I can reset the deck if jarvis crashes or becomes unresponsive.
It also works when jarvis.service is stopped with the terminal.
It handles cleanup of both software state and hardware resources without requiring the main
application to be running.

Functions:
- Release any stuck keyboard keys via ydotool
- Reset the stream deck to original state
- Clear application state and hardware connections
- Recover from most error conditions

Usage:
From the jarvis-env run: python reset_jarvis.py

Design:
This script is designed to be completely independent of the main jarvis
application and can recover from most error states, including situations
where the main application has crashed or become unresponsive.

When to Use:
- Keys appear "stuck" after jarvis crash (though this should not happen as this is handled in run_jarvis.py)
- StreamDeck shows incorrect/frozen display (this happens when the jarvis.service is stopped through the terminal)
- System becomes unresponsive
- Before troubleshooting jarvis problems
"""

import sys
import subprocess
import os
from StreamDeck.DeviceManager import DeviceManager
from pathlib import Path
from typing import Dict

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

def load_config() -> None:
    """Load configuration from config.env file for reset operations.

    This function reads the same configuration file used by the main jarvis
    application to ensure reset operations use the correct tool paths and
    settings.

    Uses the same configuration loading logic as the main application
    to maintain consistency in tool paths and settings.
    """
    config_path = Path(__file__).parent / "config.env"
    if config_path.exists():
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load configuration immediately when module is imported
# This ensures configuration is available for all reset operations, only ydotool path is needed here
load_config()

# Uses same configuration approach as main jarvis application
YDOTOOL_PATH: str = os.getenv('YDOTOOL_PATH', 'ydotool')  # Path to ydotool for key release operations

def release_all_keys() -> None:
    """Release all potentially stuck keyboard keys.

    This function sends key release events for common keys that might be
    stuck in pressed state after a jarvis crash or unexpected exit.

    Keys Released:
    Common modifier and control keys that could cause system issues
    if left in pressed state.

    Note:
    Uses ydotool to send low-level key release events. Safe to call
    even if keys are not actually stuck.
    """
    releases = [f"{code}:0" for code in KEYCODES.values()]
    subprocess.run(
        [YDOTOOL_PATH, "key"] + releases,
        check=False
    )

def reset_streamdeck() -> None:
    """Reset all connected StreamDeck devices to blank state.

    This function discovers all connected StreamDeck devices and resets
    them to a clean state with no icons or text displayed.

    Process:
    1. Discover the connected stream deck devices
    2. Open connection to my device (I only have one)
    3. Reset device display (clear all keys)
    4. Close connection cleanly

    Error Handling:
    Handles individual device errors gracefully, attempting to reset
    as many devices as possible even if some fail.

    Note:
    Reports success/failure.
    """
    decks = DeviceManager().enumerate()
    if not decks:
        print("No stream decks found.")
        return # Early exit if no devices found

    try:
        deck = decks[0] # Assume only one device for simplicity
        deck.open()
        deck.reset()
        deck.close()
        print(f"Reset stream deck: {deck.id()}")
    except Exception as e:
        print(f"Could not reset stream deck: {e}")

if __name__ == "__main__":
    """Main execution block for emergency reset operations.

    Performs complete reset sequence:
    1. Release any stuck keyboard keys
    2. Reset the stream deck
    3. Exit with success status

    Note:
    This block only executes when the script is run directly from the jarvis environment.
    """
    print("Releasing any stuck keys...")
    release_all_keys()

    print("Resetting stream deck...")
    reset_streamdeck()

    print("Done.")
    sys.exit(0)
