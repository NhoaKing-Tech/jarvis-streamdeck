"""
SCRIPT NAME: run_jarvis.py
DESCRIPTION: Python script to run my stream deck XL with custom icons and actions.
AUTHOR: NhoaKing
FINISH DATE: September 14th 2025 (Sunday)
NOTE: IMPORTANT TO EXECUTE THIS SCRIPT FROM LINUX TERMINAL, AND NOT FROM THE VSCODE TERMINAL, AS THE DBUS CALLS ARE NOT WORKING PROPERLY WHEN EXECUTED FROM VSCODE TERMINAL. IF WHEN TESTED FROM LINUX TERMINAL THE SCRIPT WORKS AS EXPECTED, THEN IT WILL WORK THE SAME WHEN EXECUTED FROM THE SYSTEM SERVICE.
"""

import subprocess, atexit, time, os
import signal
import sys
from StreamDeck.DeviceManager import DeviceManager # Class DeviceManager from the original repo
# DeviceManager imports StreamDeck classes: StreamDeck, StreamDeckMini, StreamDeckXL -> my deck
from pathlib import Path
from actions import actions
from ui.render import initialize_render, create_layouts, render_layout
from ui.logic import initialize_logic, key_change
from ui.lifecycle import initialize_lifecycle, cleanup, safe_exit

# Load configuration from config.env file
def load_config():
    config_path = Path(__file__).parent / "config.env"
    if config_path.exists():
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_config()

# Configuration - paths that can be customized via environment variables
USER_HOME = Path.home()  # Get current user's home directory
YDOTOOL_PATH = os.getenv('YDOTOOL_PATH', 'ydotool')  # Use system ydotool by default
PROJECTS_DIR = Path(os.getenv('PROJECTS_DIR', USER_HOME / 'Zenith'))  # Configurable Zenith directory
OBSIDIAN_VAULT = os.getenv('OBSIDIAN_VAULT')

# Directories for assets: code snippets and icons to display in the keys of the steamdeck
FONT_DIR = os.path.join(os.path.dirname(__file__), "assets", "font", "Roboto-Regular.ttf")
ICONS_DIR = os.path.join(os.path.dirname(__file__), "assets", "jarvisicons")
SNIPPETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "snippets")
BASHSCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "assets", "bash_scripts")

# Dictionary to hold different layouts
layouts = {}
current_layout = "main"

# Keycode mapping for ydotool
KEYCODES = {
    # Letters
    "A": 30, "B": 48, "C": 46, "D": 32, "E": 18,
    "F": 33, "G": 34, "H": 35, "I": 23, "J": 36,
    "K": 37, "L": 38, "M": 50, "N": 49, "O": 24,
    "P": 25, "Q": 16, "R": 19, "S": 31, "T": 20,
    "U": 22, "V": 47, "W": 17, "X": 45, "Y": 21,
    "Z": 44,
    # Numbers
    "1": 2, "2": 3, "3": 4, "4": 5, "5": 6,
    "6": 7, "7": 8, "8": 9, "9": 10, "0": 11,
    # Function
    "F1": 59, "F2": 60, "F3": 61, "F4": 62,
    "F5": 63, "F6": 64, "F7": 65, "F8": 66,
    "F9": 67, "F10": 68, "F11": 87, "F12": 88,
    # Modifiers
    "CTRL": 29, "SHIFT": 42, "ALT": 56,
    "RIGHTCTRL": 97, "RIGHTSHIFT": 54, "RIGHTALT": 100,
    "SUPER": 125,
    # Special
    "ESC": 1, "TAB": 15, "CAPSLOCK": 58,
    "SPACE": 57, "ENTER": 28, "BACKSPACE": 14,
    # Navigation
    "UP": 103, "DOWN": 108, "LEFT": 105, "RIGHT": 106,
    "HOME": 102, "END": 107, "PAGEUP": 104, "PAGEDOWN": 109,
    "INSERT": 110, "DELETE": 111,
    # Symbols
    "MINUS": 12, "EQUAL": 13,
    "LEFTBRACE": 26, "RIGHTBRACE": 27,
    "BACKSLASH": 43, "SEMICOLON": 39,
    "APOSTROPHE": 40, "GRAVE": 41,
    "COMMA": 51, "DOT": 52, "SLASH": 53,
}

def main():
    """
    Main function that starts the stream deck and runs the configuration.
    """
    global deck, current_layout, layouts

    actions.initialize_actions(YDOTOOL_PATH,
           SNIPPETS_DIR, BASHSCRIPTS_DIR, PROJECTS_DIR, KEYCODES)
    initialize_render(FONT_DIR, ICONS_DIR, USER_HOME, PROJECTS_DIR, OBSIDIAN_VAULT)
    initialize_lifecycle(YDOTOOL_PATH, KEYCODES)

    # -------------------- Loop retry connection to stream deck
    interval_seconds = 5 # keep trying to locate the stream deck every 5 seconds
    max_retry_minutes = 5 # keep trying to locate the stream deck for 5 minutes

    deck = None
    max_tries = max_retry_minutes*60/max_retry_minutes   # calculates the maximimum attempts to locate the stream deck according to the time interval between attempts and the maximum time allowed to keep attempting to find the deck
    current_tries = 0
    while current_tries < max_tries:
        # loop with exit condition. It will keep trying to locate the stream deck until the current_tires reaches the max_tries (starts from 0 so it counts as the first try, until 59)
        decks = DeviceManager().enumerate() # Returns the stream decks objects
        if decks:
            deck = decks[0] # The stream deck instance, it is the first one because I only have one, the Stream Deck XL
            #print("Found connected stream deck") # Commented since it is not necessary unless for debugging
            break # if deck is found, exit early
        else:
            # since it did not find the deck on the current try, it will try again
            #print(f"Stream deck is not found, retrying in {interval_seconds} seconds...") # Commented since it is not necessary unless for debugging
            time.sleep(interval_seconds)
            current_tries += 1 # updates the current tries
    else:
        #print("Stream Deck not found.") # Commented since it is not necessary unless for debugging
        sys.exit(1)

    deck.open()
    deck.reset()

    # Create all layout definitions now that deck is initialized
    layouts = create_layouts(deck)

    # Initialize UI logic with the deck and layouts
    initialize_logic(deck, layouts, "main")

    # Render buttons of the current layout. At initialization it is main
    render_layout(deck, layouts[current_layout])

    # Register key handler
    # The function key_change is called everytime a key is pressed or released
    deck.set_key_callback(key_change) #set_key_callback

    # Handle exit signals
    signal.signal(signal.SIGINT, lambda s, f: safe_exit(deck))
    atexit.register(cleanup, deck)

    print("Stream deck script is running. Press CTRL+C to quit.")
    signal.pause()

if __name__ == "__main__":
    main()