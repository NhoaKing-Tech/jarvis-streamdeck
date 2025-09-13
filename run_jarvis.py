
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
from StreamDeck.ImageHelpers import PILHelper
from PIL import Image, ImageDraw, ImageFont
import webbrowser
from urllib.parse import urlparse
import textwrap

# Directories for assets: code snippets and icons to display in the keys of the steamdeck
FONT_DIR = os.path.join(os.path.dirname(__file__), "jarvisassets", "font", "Roboto-Regular.ttf")
ICONS_DIR = os.path.join(os.path.dirname(__file__), "jarvisassets", "jarvisicons")
SNIPPETS_DIR = os.path.join(os.path.dirname(__file__), "jarvisassets", "snippets")

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

APP_CONFIG = {
    'nautilus': {
        'process_name': 'nautilus',
        'dbus_dest': 'org.gnome.Nautilus',
        'dbus_path': '/org/gnome/Nautilus',
        'command': ['nautilus'],
        'type': 'file_manager'
    },
    'obsidian': {
        'process_name': 'obsidian',
        'command': ['obsidian'],
        'type': 'application'
    },
    'chrome': {
        'process_name': 'chrome',
        'command': ['google-chrome'],
        'type': 'browser'
    }
}

def insert_snippet(snippet_name):
    """
    Function to open desired snippet and type the content calling type_text function.
    """
    snippet_path = os.path.join(SNIPPETS_DIR, snippet_name + ".txt")
    if not os.path.exists(snippet_path):
        print(f"Snippet {snippet_name} not found at {snippet_path}")
        return  
    with open(snippet_path, "r") as f:
        content = f.read()
    type_text(content)

def hot_keys(*keys):
    """
    Function to simulate hotkeys (press and release of keys) using ydotool
    """
    seq = []
    for key in keys:
        seq.append(f"{KEYCODES[key]}:1")
    for key in reversed(keys):
        seq.append(f"{KEYCODES[key]}:0")
    subprocess.Popen(["/home/nhoaking/ydotool/build/ydotool", "key"] + seq)

def type_text(text):
    """
    Function to type text using ydotool. Includes "--" to handle if text starts with "-" 
    """
    subprocess.Popen(
        ["/home/nhoaking/ydotool/build/ydotool", "type", "--", text]
    )

# Button rendering function.
def render_keys(deck, key, label=None, icon=None, color="black", labelcolor="white"):
    """
    My function to handle the visual appearance of StreamDeck buttons or keys.
    I can display either an icon, text, or both on each key. It handles the four main cases:
    1. Icon and label: icon at top, label at bottom (it truncates if too long)
    2. Only label: centered text, wrapped to multiple lines if needed
    3. Only icon: maximized icon space
    4. Neither icon nor label: solid color (default red to indicate error)
    
    Parameters:
    deck: stream deck device
    key: key index (0-31 for my stream deck XL)
    label: text to display (none if no label is desired)
    icon: filename of icon to display (must be in ICONS_DIR)
    color: background color when no icon is used. Default is black.
    label_color: color for the text or label. Default is white.
    """
    
    # I load my custom font, with fallback to system default if it fails
    try:
        font = ImageFont.truetype(FONT_DIR, 16) # I am using 16 for my 96x96 keys.
    except OSError:
        print("Could not load your custom font, check the font path and the font format (it must be .ttf).")
        font = ImageFont.load_default()
    
    # Case 1: Both icon and label
    if label and icon:
        icon_path = os.path.join(ICONS_DIR, icon)
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path)
            # Give more bottom margin for text space
            key_image = PILHelper.create_scaled_key_image(deck, icon_img, margins=(10, 0, 30, 0), background=color) #use the specified background color, or black by default if not specified
        else:
            # Icon file not found, fallback to red background for debugging
            print(f"Warning: icon {icon_path} not found, falling back to color red")
            key_image = PILHelper.create_key_image(deck, background="red")
        
        # Draw the icon with the margins as specified above to allow text/label space
        draw = ImageDraw.Draw(key_image)
        
        # To include a clean label, I calculate how many characters fit in one line
        sample_bbox = font.getbbox("a")
        avg_char_width = sample_bbox[2] - sample_bbox[0]
        chars_per_line = max(1, int(key_image.width // avg_char_width))
        
        # Truncate text if too long for one liner
        if len(label) > chars_per_line:
            display_text = label[:chars_per_line-3] + "..."
        else:
            display_text = label
        
        # Position text at bottom center
        text_y = key_image.height - 20  # 20 pixels from bottom. Where the text starts.
        draw.text(
            (key_image.width // 2, text_y),
            text=display_text,
            font=font,
            anchor="mt",  # middle-top. It positions the top of the text at the calculated. 
            # The anchor point defines which part of the text gets positioned at the coordinates specified. Since text_y is calculated as 20 pixels from the bottom, we want the top of the text to be positioned at that point, so the text extends downward from there.
            fill=labelcolor # white text color per default (can be changed if needed)
        )
    
    # Case 2: Only label (no icon)
    elif label:
        key_image = PILHelper.create_key_image(deck, background=color)
        draw = ImageDraw.Draw(key_image)
        
        # This is used to estimate character width for text wrapping. Not very important to be super accurate, since the text will be wrapped anyway.
        sample_bbox = font.getbbox("a") # To measure font metrics. Get average character width
        # getbbox() returns a bounding box (rectangle coordinates) that would completely contain the given text when rendered. The return value is a tuple: (left, top, right, bottom) in pixels.
        avg_char_width = sample_bbox[2] - sample_bbox[0]
        chars_per_line = max(1, int(key_image.width // avg_char_width))
        
        # Wrap text to multiple lines
        wrapped_lines = textwrap.wrap(label, width=chars_per_line)
        
        # This is used to estimate character height for vertical centering
        line_bbox = font.getbbox("Ay")
        #Why "Ay" specifically:
        # This is a smart choice of characters to measure:
        #"A" - A tall uppercase letter that reaches the full height (ascender)
        #"y" - A lowercase letter with a descender (the part that hangs below the baseline)
        #Together, "Ay" gives you the maximum possible height any normal text could have in that font - from the top of tall letters to the bottom of letters with tails.
        ## If getbbox("Ay") returns (0, -2, 15, 18), then:
        #left = 0    # leftmost pixel of the text
        #top = -2    # topmost pixel (negative because it's above baseline)
        #right = 15  # rightmost pixel  
        #bottom = 18 # bottommost pixel (includes descender for 'y')
        line_height = line_bbox[3] - line_bbox[1]
        total_text_height = len(wrapped_lines) * line_height
        
        # Center text vertically
        start_y = (key_image.height - total_text_height) // 2
        
        # Draw each line
        for i, line in enumerate(wrapped_lines):
            y_pos = start_y + (i * line_height)
            # anchor="mt": position the top of each text line at y_pos
            # This ensures consistent line spacing as each line flows downward
            draw.text(
                (key_image.width // 2, y_pos),  # x=center, y=calculated position
                text=line,
                font=font,
                anchor="mt",  # middle-top: center horizontally, position top edge at y coordinate
                fill=labelcolor # white text color per default (can be changed if needed)
            )
    
    # Case 3: Only icon (no label)
    elif icon:
        icon_path = os.path.join(ICONS_DIR, icon)
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path)
            # No margins needed, maximize icon space
            key_image = PILHelper.create_scaled_key_image(deck, icon_img, margins=(0, 0, 0, 0), background=color)
        else:
            print(f"Warning: icon {icon_path} not found, falling back to color red")
            key_image = PILHelper.create_key_image(deck, background="red")
    
    # Case 4: Neither icon nor label, just color. Default to red to indicate a problem, signaling that nothing has been set for this key.
    else:
        key_image = PILHelper.create_key_image(deck, background=color if color else "red")
    
    # Set the key image on the deck
    deck.set_key_image(key, PILHelper.to_native_key_format(deck, key_image))

def open_or_raise_nautilus(target_dir):
    target_dir = os.path.abspath(target_dir)

    # Step 1: Check if a Nautilus window with this directory exists
    wmctrl_output = subprocess.check_output(["wmctrl", "-lx"], text=True)

    for line in wmctrl_output.splitlines():
        if "org.gnome.Nautilus" in line:
            win_id = line.split()[0]
            window_title = " ".join(line.split()[3:])

            # Check if the target directory path is contained in the window title
            # or if the folder name matches (for better compatibility)
            folder_name = os.path.basename(target_dir)
            if (target_dir in window_title or
                folder_name in window_title or
                window_title.endswith(folder_name)):

                print(f"Raising existing Nautilus window for {target_dir}")
                subprocess.run(["wmctrl", "-i", "-a", win_id])
                return

    # Step 2: Otherwise, open a new Nautilus window
    print(f"Opening new Nautilus at {target_dir}")
    subprocess.Popen(["nautilus", target_dir])

# --- Actions ---
def open_vscode_busybee():
    project_path = "/home/nhoaking/Zenith/busybee"
    subprocess.Popen([
        "code", project_path,
    ])
    time.sleep(2)
    hot_keys("CTRL", "SHIFT", "GRAVE")


def open_obsidian():
    subprocess.Popen(["obsidian"])

def open_vscode_jarvis():
    project_path = "/home/nhoaking/Zenith/jarvis-streamdeck"
    subprocess.Popen([
        "code", project_path,
    ])
    time.sleep(2)
    hot_keys("CTRL", "GRAVE")
    
def open_spotify():
    not_open = subprocess.run(["pgrep", "-x", "spotify"], capture_output=True)
    if not_open.returncode == 0:
        # Spotify is running, then the button runs either play or pause
        subprocess.Popen(["playerctl", "--player=spotify", "play-pause"])
    else:
        # Spotify not running, the starts the app.
        subprocess.Popen(["spotify"])

#def open_nautilus():
#    subprocess.Popen(["nautilus", "/home/nhoaking"])

def open_terminal_env():
    subprocess.Popen(["/home/nhoaking/Zenith/jarvis-streamdeck/test/open_jarvisbusybee_env_T.sh"])

def open_terminal():
    hot_keys("CTRL", "ALT", "T")

def open_github():
    subprocess.Popen(["xdg-open", "https://github.com/NhoaKing-Tech"])

def open_shine():
    subprocess.Popen(["xdg-open", "https://www.youtube.com/watch?v=x53OGmkT-eM&list=RDx53OGmkT-eM&start_radio=1"])

def open_chat():
    subprocess.Popen(["xdg-open", "https://chatgpt.com/g/g-p-68b9273a9e488191b335ed4477655eeb-zenith/project"])

def open_claude():
    subprocess.Popen(["xdg-open", "https://claude.ai/project/01993cb6-a107-7274-8d75-4368cc08d1b1"])

def toggle_output_mute():
    subprocess.Popen(["amixer", "set", "Master", "toggle"])

def is_mic_muted():
    result = subprocess.run(
        ["amixer", "get", "Capture"],
        capture_output=True,
        text=True
    )
    return "[off]" in result.stdout  # True if mic muted


def toggle_mic(deck, key):
    # Toggle mute
    subprocess.run(["amixer", "set", "Capture", "toggle"])

    # Check new state
    muted = is_mic_muted()

    # Update button icon
    if muted:
        render_keys(deck, key, label="OFF", icon="mic-off.png")
    else:
        render_keys(deck, key, label="ON", icon="mic-on.png")

def type_message():
    type_text("Hello from StreamDeck!")

def insert_snippet_action(snippet_name):
    return lambda: insert_snippet(snippet_name)

def copy():
    hot_keys("CTRL", "C")

def paste():
    hot_keys("CTRL", "V")

def type_hola():
    type_text("Hola!")

def release_all_keys():
    releases = [f"{code}:0" for code in KEYCODES.values()]
    subprocess.Popen(
        ["/home/nhoaking/ydotool/build/ydotool", "key"] + releases
    )

def switch_page(page_name):
    global current_page
    current_page = page_name
    render_page(layouts[page_name])

def render_page(page):
    if deck and deck.is_open():
        deck.reset()  # clear old icons
        deck.set_brightness(50)
    for key, props in page.items():
        render_keys(
            deck,
            key,
            props.get("label"),
            props.get("icon"),
            props.get("color"),
            props.get("labelcolor")
        )

current_page = "main"

# 0,     1,    2,   3,     4,    5,    6,    7
# 8,     9,   10,   11,   12,   13,   14,   15
# 16,   17,   18,   19,   20,   21,   22,   23
# 24,   25,   26,   27,   28,   29,   30,   31

# Main page layout
layouts["main"] = {
    0: {"label": "Spotify for debugging", "icon": "spotify.png", "action": open_spotify},
    1: {"icon": "obsidian.png", "action": open_obsidian},
    8: {"icon": "chatgpt.png", "action": open_chat},
    9: {"icon": "claude.png", "action": open_claude},
    
    2: {"icon": "jarviscode.png", "action": open_vscode_jarvis},
    3: {"icon": "busybeecode.png", "action": open_vscode_busybee},
    10: {"icon": "python.png", "action": lambda: switch_page("python")},
    18: {"icon": "github.png", "color": "#2f3036", "action": open_github},
    19: {"icon": "git_layout.png", "color": "#2f3036", "action": lambda: switch_page("git")},

    4: {"icon": "terminal.png", "action": open_terminal},
    5: {"icon": "terminalenv.png", "action": open_terminal_env},
    12: {"icon": "terminal_layout.png", "action": lambda: switch_page("terminal_layout")},
    13: {"icon": "conda_layout.png", "action": lambda: switch_page("conda_layout")}, 

    6: {"icon": "busybee.png", "action": lambda: switch_page("busybee")}, #icon <a href="https://www.flaticon.com/free-icons/bee" title="bee icons">Bee icons created by Indielogy - Flaticon</a>
    
    
    
    
    7: {"icon": "nautilus.png", "action": lambda: open_or_raise_nautilus("/home/nhoaking/Zenith/busybee")}, # <a href="https://www.flaticon.com/free-icons/files-and-folders" title="files and folders icons">Files and folders icons created by juicy_fish - Flaticon</a>
    #9: {"label": "Text", "color": "pink", "action": type_message},
    #10: {"label": "Copy", "color": "blue", "action": copy},
    #11: {"label": "Paste", "color": "pink", "action": paste},
    #12: {"label": "Hola", "color": "blue", "action": type_hola},
    #13: {"label": "More", "color": "purple", "action": lambda: switch_page("terminal")},
    #14: {"icon": "shine.png", "action": open_shine},
    
    31: {"icon": "mic-fill.png", "action": lambda: toggle_mic(deck, 31)},
}

# Terminal page layout
layouts["terminal"] = {
    0: {"icon": "back.png", "color": "white", "action": lambda: switch_page("main")}, #<div> Icons made by <a href="https://www.flaticon.com/authors/radhe-icon" title="Radhe Icon"> Radhe Icon </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
    1: {"label": "Run LS", "color": "pink", "action": lambda: type_text("ls\n")},
    2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet_action("hello")},
    3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet_action("python_boilerplate")},
}

layouts["busybee"] = {
    0: {"icon": "back.png", "color": "white", "action": lambda: switch_page("main")},
    1: {"label": "Run LS", "color": "pink", "action": lambda: type_text("ls\n")},
    2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet_action("hello")},
    3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet_action("python_boilerplate")},
}

layouts["python"] = {
    0: {"icon": "back.png", "color": "white", "action": lambda: switch_page("main")},
    1: {"label": "Run LS", "color": "pink", "action": lambda: type_text("ls\n")},
    2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet_action("hello")},
    3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet_action("python_boilerplate")},
}

layouts["git"] = {
    0: {"icon": "back.png", "color": "white", "action": lambda: switch_page("main")},
    1: {"label": "Run LS", "color": "pink", "action": lambda: type_text("ls\n")},
    2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet_action("hello")},
    3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet_action("python_boilerplate")},
}

layouts["terminal_layout"] = { #<div> Icons made by <a href="https://www.flaticon.com/authors/icon-hubs" title="Icon Hubs"> Icon Hubs </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
    0: {"icon": "back.png", "color": "white", "action": lambda: switch_page("main")},
    1: {"label": "Run LS", "color": "pink", "action": lambda: type_text("ls\n")},
    2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet_action("hello")},
    3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet_action("python_boilerplate")},
}

layouts["conda_layout"] = { #<div> Icons made by <a href="https://www.flaticon.com/authors/muhammad-ali" title="Muhammad Ali"> Muhammad Ali </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
    0: {"icon": "back.png", "color": "white", "action": lambda: switch_page("main")},
    1: {"label": "List environments", "labelcolor": "#ff008c", "color": "#1c2e1c", "action": lambda: type_text("conda env list\n")},
    2: {"label": "List installed packages", "color": "#1c2e1c", "action": lambda: type_text("conda list\n")},
    3: {"label": "List package", "color": "#1c2e1c", "action": lambda: type_text("conda list <package>")},
    4: {"label": "Python version", "color": "#1c2e1c", "action": lambda: type_text("python --version\n")},
    5: {"label": "Activate env", "color": "#1c2e1c", "action": lambda: type_text("conda activate <env>\n")},
}



# --- Cleanup ---
_cleaned_up = False
def cleanup(deck=None):
    global _cleaned_up
    if _cleaned_up:
        return
    _cleaned_up = True
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

# --- Event handler ---
def key_change(deck, key, state):
    if state and key in layouts[current_page]:
        try:
            layouts[current_page][key]["action"]()
        except:
            pass

# --- Main with retry loop ---
max_attempts = 60   # retry for ~5 minutes
interval = 5
attempts = 0

deck = None
while attempts < max_attempts:
    decks = DeviceManager().enumerate()
    if decks:
        deck = decks[0]
        print("Stream Deck found!")
        break
    else:
        print(f"No Stream Deck found, retrying in {interval}s...")
        time.sleep(interval)
        attempts += 1
else:
    print("Stream Deck not found. Exiting.")
    sys.exit(1)

deck.open()
deck.reset()

# Render buttons
render_page(layouts[current_page])

# Register key handler
deck.set_key_callback(key_change)

# Handle exit signals
signal.signal(signal.SIGINT, lambda s, f: safe_exit(deck))
atexit.register(cleanup, deck)

print("Stream Deck active. Press CTRL+C to quit.")
signal.pause()
