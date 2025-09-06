import subprocess, atexit, time, os
import signal
import sys
from StreamDeck.DeviceManager import DeviceManager # Class DeviceManager from the original repo
from StreamDeck.ImageHelpers import PILHelper
from PIL import Image, ImageDraw, ImageFont
from functools import partial

# Dictionary to hold different grids
grids = {}

# --- Keycodes & helpers ---
KEYCODES = {
    # Letters
    "A": 30, "B": 48, "C": 46, "D": 32, "E": 18,
    "F": 33, "G": 34, "H": 35, "I": 23, "J": 36,
    "K": 37, "L": 38, "M": 50, "N": 49, "O": 24,
    "P": 25, "Q": 16, "R": 19, "S": 31, "T": 20,
    "U": 22, "V": 47, "W": 17, "X": 45, "Y": 21,
    "Z": 44,
    # Numbers (top row)
    "1": 2, "2": 3, "3": 4, "4": 5, "5": 6,
    "6": 7, "7": 8, "8": 9, "9": 10, "0": 11,
    # Function keys
    "F1": 59, "F2": 60, "F3": 61, "F4": 62,
    "F5": 63, "F6": 64, "F7": 65, "F8": 66,
    "F9": 67, "F10": 68, "F11": 87, "F12": 88,
    # Modifiers
    "CTRL": 29, "SHIFT": 42, "ALT": 56,
    "RIGHTCTRL": 97, "RIGHTSHIFT": 54, "RIGHTALT": 100,
    "SUPER": 125,
    # Special keys
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
    # Numpad
    "NUMLOCK": 69, "KPSLASH": 98, "KPASTERISK": 55, "KPMINUS": 74,
    "KPPLUS": 78, "KPENTER": 96, "KPDOT": 83,
    "KP0": 82, "KP1": 79, "KP2": 80, "KP3": 81, "KP4": 75,
    "KP5": 76, "KP6": 77, "KP7": 71, "KP8": 72, "KP9": 73,
}

SNIPPETS_DIR = os.path.join(os.path.dirname(__file__), "snippets")
ICONS_DIR = os.path.join(os.path.dirname(__file__), "jarvisicons")

def insert_snippet(snippet_name):
    snippet_path = os.path.join(SNIPPETS_DIR, snippet_name + ".txt")
    if not os.path.exists(snippet_path):
        print(f"Snippet {snippet_name} not found at {snippet_path}")
        return
    
    with open(snippet_path, "r") as f:
        content = f.read()

    # Type text into active window
    type_text(content)

def hot_keys(*keys):
    seq = []
    for key in keys:
        seq.append(f"{KEYCODES[key]}:1")
    for key in reversed(keys):
        seq.append(f"{KEYCODES[key]}:0")
    subprocess.Popen(["/home/nhoaking/ydotool/build/ydotool", "key"] + seq)

def type_text(text):
    subprocess.Popen(
        ["/home/nhoaking/ydotool/build/ydotool", "type", "--", text]
    )

def paint_button(deck, key, label=None, icon=None, color="blue"):
    # If an icon is provided, try to load it
    if icon:
        icon_path = os.path.join(ICONS_DIR, icon)
        if os.path.exists(icon_path):
            icon_img = Image.open(icon_path)
            margins = (10, 10, 10, 10) if not label else (0, 0, 20, 0)
            key_image = PILHelper.create_scaled_key_image(
                deck, icon_img, margins=margins, background="black"
            )
        else:
            print(f"Warning: icon {icon_path} not found, falling back to color")
            key_image = PILHelper.create_key_image(deck, background=color)
    else:
        # Just a background if no icon
        key_image = PILHelper.create_key_image(deck, background=color)

    # Draw label if provided
    if label:
        draw = ImageDraw.Draw(key_image)
        try:
            font_path = os.path.join(os.path.dirname(__file__), "jarvisassets", "Roboto-Regular.ttf")
            font = ImageFont.truetype(font_path, 16)  # adjust size here
        except OSError:
            print("Could not load RobotoMono, using default font.")
            font = ImageFont.load_default()

        # Center text at bottom
        draw.text(
            (key_image.width / 2, key_image.height - 5),
            text=label,
            font=font,
            anchor="ms",  # middle-south
            fill="white"
        )

    # Push to deck
    deck.set_key_image(key, PILHelper.to_native_key_format(deck, key_image))


# --- Actions ---
def open_vscode_mamba():
    project_path = "/home/nhoaking/Zenith/Mamba"
    subprocess.Popen([
        "code", project_path,
    ])
    time.sleep(2)
    hot_keys("CTRL", "SHIFT", "GRAVE")

def open_vscode_jarvis():
    project_path = "/home/nhoaking/Zenith/Jarvis/jarvis-streamdeck"
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


def open_terminal():
    subprocess.Popen(["/home/nhoaking/Zenith/Jarvis/jarvis-streamdeck/test/open_jarvismamba_env_T.sh"])

def open_terminal_default():
    hot_keys("CTRL", "ALT", "T")

def open_github():
    subprocess.Popen(["xdg-open", "https://github.com/NhoaKing-Tech"])

def open_chat():
    subprocess.Popen(["xdg-open", "https://chatgpt.com/g/g-p-68b9273a9e488191b335ed4477655eeb-zenith/project"])

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
        paint_button(deck, key, label="Mic", icon="mic-off.png", color="red")
    else:
        paint_button(deck, key, label="Mic", icon="mic-on.png", color="green")

def type_message():
    type_text("Hello from StreamDeck!")

def insert_snippet_action(snippet_name):
    return lambda: insert_snippet(snippet_name)

def copy():
    hot_keys("CTRL", "C")

def paste():
    hot_keys("CTRL", "V")

def open_firefox():
    subprocess.Popen(["firefox"])

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
    render_page(grids[page_name])

def render_page(page):
    if deck and deck.is_open():
        deck.reset()  # clear old icons
        deck.set_brightness(50)
    for key, props in page.items():
        paint_button(
            deck,
            key,
            props.get("label"),
            props.get("icon"),
            props.get("color", "black")
        )

current_page = "main"

# Main page layout
grids["main"] = {
    0: {"color": "purple", "icon": "spoti.png", "action": open_spotify},
    1: {"icon": "chat.png", "action": open_chat},
    2: {"icon": "github.png", "action": open_github},
    3: {"icon": "jarvis.png", "action": open_vscode_jarvis},
    4: {"icon": "mamba.png", "action": open_vscode_mamba},
    5: {"icon": "terminalJM.png", "action": open_terminal},
    6: {"icon": "defaultTerminal.png", "action": open_terminal_default},
    7: {"label": "Text", "color": "pink", "action": type_message},
    8: {"label": "Copy", "color": "blue", "action": copy},
    9: {"label": "Paste", "color": "yellow", "action": paste},
    10: {"label": "Firefox", "color": "orange", "action": open_firefox},
    11: {"label": "Hola", "color": "blue", "action": type_hola},
    12: {"label": "More", "color": "purple", "action": lambda: switch_page("terminal")},
    30: {"icon": "mic-fill.png", "color": "green", "action": lambda: toggle_mic(deck, 31)},
}

# Terminal page layout
grids["terminal"] = {
    0: {"label": "Go Back", "icon": "back.png", "color": "grey", "action": lambda: switch_page("main")},
    1: {"label": "Run LS", "color": "pink", "action": lambda: type_text("ls\n")},
    2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet_action("hello")},
    3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet_action("python_boilerplate")},
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
    if state and key in grids[current_page]:
        try:
            grids[current_page][key]["action"]()
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
render_page(grids[current_page])

# Register key handler
deck.set_key_callback(key_change)

# Handle exit signals
signal.signal(signal.SIGINT, lambda s, f: safe_exit(deck))
atexit.register(cleanup, deck)

print("Stream Deck active. Press CTRL+C to quit.")
signal.pause()
