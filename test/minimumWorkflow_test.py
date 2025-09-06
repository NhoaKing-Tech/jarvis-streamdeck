import subprocess, atexit, time
import signal
import sys
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from PIL import Image, ImageDraw

KEYCODES = {
    # Letters
    "A": 30, "B": 48, "C": 46, "D": 32, "E": 18,
    "F": 33, "G": 34, "H": 35, "I": 23, "J": 36,
    "K": 37, "L": 38, "M": 50, "N": 49, "O": 24,
    "P": 25, "Q": 16, "R": 19, "S": 31, "T": 20,
    "U": 22, "V": 47, "W": 17, "X": 45, "Y": 21,
    "Z": 44,

    # Numbers (top row, not numpad)
    "1": 2, "2": 3, "3": 4, "4": 5, "5": 6,
    "6": 7, "7": 8, "8": 9, "9": 10, "0": 11,

    # Function keys
    "F1": 59, "F2": 60, "F3": 61, "F4": 62,
    "F5": 63, "F6": 64, "F7": 65, "F8": 66,
    "F9": 67, "F10": 68, "F11": 87, "F12": 88,

    # Modifiers
    "CTRL": 29, "SHIFT": 42, "ALT": 56,
    "RIGHTCTRL": 97, "RIGHTSHIFT": 54, "RIGHTALT": 100,
    "SUPER": 125,   # Windows / Command key

    # Special keys
    "ESC": 1, "TAB": 15, "CAPSLOCK": 58,
    "SPACE": 57, "ENTER": 28, "BACKSPACE": 14,

    # Navigation
    "UP": 103, "DOWN": 108, "LEFT": 105, "RIGHT": 106,
    "HOME": 102, "END": 107, "PAGEUP": 104, "PAGEDOWN": 109,
    "INSERT": 110, "DELETE": 111,

    # Symbols (row with numbers)
    "MINUS": 12, "EQUAL": 13,
    "LEFTBRACE": 26, "RIGHTBRACE": 27,
    "BACKSLASH": 43, "SEMICOLON": 39,
    "APOSTROPHE": 40, "GRAVE": 41,   # backtick/tilde
    "COMMA": 51, "DOT": 52, "SLASH": 53,

    # Numpad
    "NUMLOCK": 69, "KPSLASH": 98, "KPASTERISK": 55, "KPMINUS": 74,
    "KPPLUS": 78, "KPENTER": 96, "KPDOT": 83,
    "KP0": 82, "KP1": 79, "KP2": 80, "KP3": 81, "KP4": 75,
    "KP5": 76, "KP6": 77, "KP7": 71, "KP8": 72, "KP9": 73,
}

def hot_keys(*keys):
    seq = []
    for key in keys:
        seq.append(f"{KEYCODES[key]}:1")   # press
    for key in reversed(keys):
        seq.append(f"{KEYCODES[key]}:0")   # release
    subprocess.Popen(["/home/nhoaking/ydotool/build/ydotool", "key"] + seq)

def type_text(text):
    subprocess.Popen(
        ["/home/nhoaking/ydotool/build/ydotool", "type", "--", text]
    )

# --- Button Rendering ---
def paint_button(deck, key, label, color):
    image = PILHelper.create_image(deck)
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, image.width, image.height), fill=color)
    draw.text((20, 20), label, fill="white")
    deck.set_key_image(key, PILHelper.to_native_format(deck, image))

# --- Actions ---
def open_terminal():
    subprocess.Popen(["/home/nhoaking/Zenith/Jarvis/jarvis-streamdeck/test/open_jarvismamba_env_T.sh"])

def open_github():
    subprocess.Popen(["xdg-open", "https://github.com"])

def open_chat():
    subprocess.Popen(["xdg-open", "https://chatgpt.com/"])

def toggle_mute():
    subprocess.Popen(["amixer", "set", "Master", "toggle"])

def type_message():
    type_text("-Hello from StreamDeck!")

def copy():
    hot_keys("CTRL", "C")

def paste():
    hot_keys("CTRL", "V")

def firefox_with_copy():
    subprocess.Popen(["firefox"])

def release_all_keys():
    releases = [f"{code}:0" for code in KEYCODES.values()]
    subprocess.Popen(
        ["/home/nhoaking/ydotool/build/ydotool", "key"] + releases
    )

# --- Keymap ---
keymap = {
    0: {"label": "Terminal", "color": "red", "action": open_terminal},
    1: {"label": "GitHub", "color": "blue", "action": open_github},
    2: {"label": "Chat", "color": "blue", "action": open_chat},
    3: {"label": "Mute", "color": "green", "action": toggle_mute},
    4: {"label": "Text", "color": "pink", "action": type_message},
    5: {"label": "Copy", "color": "blue", "action": copy},
    6: {"label": "Paste", "color": "yellow", "action": paste},
    7: {"label": "Firefox+Copy", "color": "orange", "action": firefox_with_copy},
}

# --- Event Handler ---
def key_change(deck, key, state):
    if state and key in keymap:  # Only on press
        keymap[key]["action"]()

_cleaned_up = False

# --- Cleanup ---
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

# --- Main ---
decks = DeviceManager().enumerate()
if not decks:
    print("No Stream Decks found.")
    sys.exit(1)

deck = decks[0]
deck.open()
deck.reset()

# Render buttons from keymap
for key, props in keymap.items():
    paint_button(deck, key, props["label"], props["color"])

deck.set_key_callback(key_change)

# Handle CTRL+C gracefully
def signal_handler(_sig, _frame):
    print("\nExiting...")
    safe_exit(deck)

signal.signal(signal.SIGINT, signal_handler)

# Ensure cleanup on normal exit
atexit.register(cleanup, deck)

print("Stream Deck active. Press CTRL+C to quit.")

# Keep alive
signal.pause()