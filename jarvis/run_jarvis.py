
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
from render.render import render_keys, initialize_render

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
FONT_DIR = os.path.join(os.path.dirname(__file__), "jarvisassets", "font", "Roboto-Regular.ttf")
ICONS_DIR = os.path.join(os.path.dirname(__file__), "jarvisassets", "jarvisicons")
SNIPPETS_DIR = os.path.join(os.path.dirname(__file__), "jarvisassets", "snippets")
BASHSCRIPTS_DIR = os.path.join(os.path.dirname(__file__), "jarvisassets", "bash_scripts")

# Dictionary to hold different layouts
layouts = {}

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
    
def release_all_keys():
    """
    In case of sticky keys, this function releases all keys. 
    It is called when the script exits or crashes. Second bug I found with ydotool >.<
    """
    releases = [f"{code}:0" for code in KEYCODES.values()]
    subprocess.Popen(
        [YDOTOOL_PATH, "key"] + releases
    )

def switch_layout(layout_name):
    """
    I created this function as a function that returns a wrapper function (accomplishes the same as a lambda function
    declared inline when building the layout dictionary, but cleaner and easier to read).
    When I call this function with a layout_name, it doesn't immediately switch the deck layout. Instead, 
    I return a nested function (wrapper) that, when called later, will switch to the specified layout in layout_name. 
    This is useful in my StreamDeck layout because I can call switch_layout('home') during layout definition, 
    and it returns a function that can be executed when the button is pressed. 
    This eliminates the need for me to write lambda expressions in my layout dictionaries, keeping the code cleaner.
    The wrapper function uses the global current_layout variable to track state and
    calls render_layout to actually display the new deck layout.
    """
    def wrapper():
        global current_layout
        current_layout = layout_name
        render_layout(layouts[layout_name])
    return wrapper

# Not used, found a better way with the switch_layout function above
def switch_layout_lambda_in_layout(layout_name):
    """
    I designed this function first to be called directly when I want to switch deck layouts.
    Unlike the switch_layout function above, this one switches to the specified deck layout right away
    when called, since it takes an argument (layout_name). Therefore I needed to write a lambda expression when using
    it in my layout dictionaries, like: lambda: switch_layout_lambda_in_layout('main'). 
    At the beginning, I had lambda expressions in my layout definitions, but I wanted to avoid that for cleaner code. 
    It also makes easier to build the dictionary, as I could have forgotten to add the lambda in some places. ._.
    
    """
    global current_layout
    current_layout = layout_name
    render_layout(layouts[layout_name])

def render_layout(layout):
    """
    Render all keys for the given layout.

    Arguments:
    layout: dictionary defining the layout
    """
    if not deck or not deck.is_open(): # exits if deck is not initialized before the loop to render keys
        return
    deck.reset()  # clear old icons
    deck.set_brightness(50) # set brightness to 50% (0-100) # from StreamDeck.py from the original repo
    for key, config in layout.items(): 
        # This loop is a dictionary unpacking
        # config is label, icon, color, labelcolor, action...
        # The layout.items() method returns pairs (tuples) of 
        # (key, configs) for each item in the dictionary. Python
        # unpacks each tuple into two variables: key and its configuration.
        render_keys(
            deck,
            key,
            config.get("label"), # text label to display on the key (if specified)
            config.get("icon"), # icon filename to display on the key (if specified)
            config.get("color"), # the background color of the key (if specified)
            config.get("labelcolor") # the color of the text label (if specified)
        )

def create_layouts(deck):
    """
    Create all layout definitions after deck is initialized.
    This ensures deck is available for functions that need it.
    """
    # 0,     1,    2,   3,     4,    5,    6,    7
    # 8,     9,   10,   11,   12,   13,   14,   15
    # 16,   17,   18,   19,   20,   21,   22,   23
    # 24,   25,   26,   27,   28,   29,   30,   31

    # Main layout
    layouts["main"] = {
        0: {"icon": "spotify.png", "action": actions.open_spotify},
        1: {"icon": "obsidian.png", "action": actions.open_obsidian(OBSIDIAN_VAULT)},
        8: {"icon": "chatgpt.png", "action": actions.open_chat},
        9: {"icon": "claude.png", "action": actions.open_claude},
        16: {"icon": "freecodecamp.png", "action": actions.open_freecodecamp},


        2: {"icon": "jarviscode.png", "action": actions.open_vscode(str(PROJECTS_DIR / 'jarvis-streamdeck'))},
        3: {"icon": "busybeecode.png", "action": actions.open_vscode(str(PROJECTS_DIR / 'busybee'))},
        10: {"icon": "python.png", "action": switch_layout("python")},
        18: {"icon": "github.png", "color": "#2f3036", "action": actions.open_github},
        19: {"icon": "git_layout.png", "color": "#2f3036", "action": switch_layout("git")},

        4: {"icon": "terminal.png", "action": actions.open_terminal},
        5: {"icon": "terminalenv.png", "action": actions.open_terminal_env},
        12: {"icon": "terminal_layout.png", "action": switch_layout("terminal_layout")},
        13: {"icon": "conda_layout.png", "action": switch_layout("conda_layout")},

        6: {"icon": "busybee.png", "action": switch_layout("busybee")}, #icon <a href="https://www.flaticon.com/free-icons/bee" title="bee icons">Bee icons created by Indielogy - Flaticon</a>

        7: {"icon": "nautilus.png", "action": lambda: actions.nautilus_path(str(PROJECTS_DIR / 'busybee'))}, # <a href="https://www.flaticon.com/free-icons/files-and-folders" title="files and folders icons">Files and folders icons created by juicy_fish - Flaticon</a>
        #9: {"label": "Text", "color": "pink", "action": type_message},
        #10: {"label": "Copy", "color": "blue", "action": copy},
        #11: {"label": "Paste", "color": "pink", "action": paste},
        #12: {"label": "Hola", "color": "blue", "action": type_hola},
        #13: {"label": "More", "color": "purple", "action": lambda: switch_layout("terminal")},
        #14: {"icon": "shine.png", "action": open_shine},

        31: {"icon": "mic-fill.png", "action": actions.toggle_mic(deck, 31)},
    }

    # Terminal layout
    layouts["terminal"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")}, #<div> Icons made by <a href="https://www.flaticon.com/authors/radhe-icon" title="Radhe Icon"> Radhe Icon </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
        1: {"label": "Run LS", "color": "pink", "action": actions.type_text("ls\n")},
        2: {"label": "Simple Snippet", "color": "cyan", "action": actions.insert_snippet("hello")},
        3: {"label": "Python Boilerplate", "color": "orange", "action": actions.insert_snippet("python_boilerplate")},
    }

    layouts["busybee"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")},
        1: {"label": "Run LS", "color": "pink", "action": actions.type_text("ls\n")},
        2: {"label": "Simple Snippet", "color": "cyan", "action": actions.insert_snippet("hello")},
        3: {"label": "Python Boilerplate", "color": "orange", "action": actions.insert_snippet("python_boilerplate")},
    }

    layouts["python"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")},
        1: {"label": "Run LS", "color": "pink", "action": actions.type_text("ls\n")},
        2: {"label": "Simple Snippet", "color": "cyan", "action": actions.insert_snippet("hello")},
        3: {"label": "Python Boilerplate", "color": "orange", "action": actions.insert_snippet("python_boilerplate")},
    }

    layouts["git"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")},
        1: {"label": "Run LS", "color": "pink", "action": actions.type_text("ls\n")},
        2: {"label": "Simple Snippet", "color": "cyan", "action": actions.insert_snippet("hello")},
        3: {"label": "Python Boilerplate", "color": "orange", "action": actions.insert_snippet("python_boilerplate")},
    }

    layouts["terminal_layout"] = { #<div> Icons made by <a href="https://www.flaticon.com/authors/icon-hubs" title="Icon Hubs"> Icon Hubs </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")},
        1: {"label": "Run LS", "color": "pink", "action": actions.type_text("ls\n")},
        2: {"label": "Simple Snippet", "color": "blue", "action": actions.insert_snippet("hello")},
        3: {"label": "Python Boilerplate", "color": "orange", "action": actions.insert_snippet("python_boilerplate")},
    }

    layouts["conda_layout"] = { #<div> Icons made by <a href="https://www.flaticon.com/authors/muhammad-ali" title="Muhammad Ali"> Muhammad Ali </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")},
        1: {"label": "List environments", "labelcolor": "#ff008c", "color": "#1c2e1c", "action": actions.type_text("conda env list\n")},
        2: {"label": "List installed packages", "color": "#1c2e1c", "action": actions.type_text("conda list\n")},
        3: {"label": "List package", "color": "#1c2e1c", "action": actions.type_text("conda list <package>")},
        4: {"label": "Python version", "color": "#1c2e1c", "action": actions.type_text("python --version\n")},
        5: {"label": "Activate env", "color": "#1c2e1c", "action": actions.type_text("conda activate <env>")},
    }

# -------------------- Avoid sticky keys, reset deck and close it
clean_stickykeys = False # Flag to prevent multiple cleans of sticky keys. Set to false initially because clean up is not yet performed.
def cleanup(deck=None):
    global clean_stickykeys
    if clean_stickykeys:
        return
    clean_stickykeys = True # the flag changes to true as all keys have been released.
    try:
        print("\nCleaning up...")
        release_all_keys()
        if deck and deck.is_open():
            deck.reset()
            deck.close()
    except Exception as e:
        print(f"(cleanup ignored error: {e})")

def safe_exit(deck=None):
    cleanup(deck)
    sys.exit(0)

def key_change(deck, key, state):
    """
    Event handler for deck key presses
    Arguments:
    deck: the stream deck
    key: what key was pressed. In my case from 0 to 31 (the stream deck XL from elgato has 32 keys)
    state: true if key is pressed, and false when it is release.
    """
    if state and key in layouts[current_layout]:
        # when a key is pressed and the key exists in the current layout
        try:
            # executes the action assigned to the key
            layouts[current_layout][key]["action"]()
        except:
            pass # ignore silently

def main():
    """
    Main function that starts the stream deck and runs the configuration.
    """
    global deck, current_layout

    actions.initialize_actions(YDOTOOL_PATH,
           SNIPPETS_DIR, BASHSCRIPTS_DIR, KEYCODES)
    initialize_render(FONT_DIR, ICONS_DIR)
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

    current_layout = "main" # the first layout to display is always the main layout

    deck.open()
    deck.reset()

    # Create all layout definitions now that deck is initialized
    create_layouts(deck)

    # Render buttons of the current layout. At initialization it is main
    render_layout(layouts[current_layout])

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