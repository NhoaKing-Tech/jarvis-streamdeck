
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
# DeviceManager imports StreamDeck classes: StreamDeck, StreamDeckMini, StreamDeckXL (my deck)
from StreamDeck.ImageHelpers import PILHelper # Functions from PILHelper from the original repo
from PIL import Image, ImageDraw, ImageFont # PIL modules
import webbrowser
from urllib.parse import urlparse
import textwrap

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

# -------------------- Key Rendering ----------------- #
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
        key_image = PILHelper.create_key_image(deck, background=color) # from the PILHelper.py from the original repo
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
    deck.set_key_image(key, PILHelper.to_native_key_format(deck, key_image)) # set_key_image comes from StreamDeck.py from the original repo
    # to_native_key_format comes from PILHelper.py from the original repo

# ------------------ Functions for key actions ----------------- #
def type_text(text):
    """
    Function to type text using ydotool. Includes "--" to handle if text starts with "-"
    I could use now xdotool instead of ydotool after switching to X11. But I already 
    have ydotool installed because I was running on Wayland previously. 
    It seems to still be working fine.
    If I get issues later with it, I will switch to xdotool.
    Returns a callable function for use in layout definitions.
    """
    return lambda: (
        subprocess.Popen(["/home/nhoaking/ydotool/build/ydotool", "type", "--", text])
    )

def insert_snippet(snippet_name):
    """
    Function to insert desired code snippet or boilerplate.
    Similar to type_text but for code snippets stored as txt files.
    """
    snippet_path = os.path.join(SNIPPETS_DIR, snippet_name + ".txt")
    if not os.path.exists(snippet_path):
        print(f"Snippet {snippet_name} not found at {snippet_path}") # print not shown if running from service
        return lambda: None
    with open(snippet_path, "r") as f:
        snippet = f.read()
    return lambda: (
        subprocess.Popen(["/home/nhoaking/ydotool/build/ydotool", "type", "--", snippet])
    )

def hot_keys(*keys):
    """
    Function to simulate hotkeys (press and release of keys) using ydotool
    """
    seq = []
    for key in keys:
        seq.append(f"{KEYCODES[key]}:1") # press
    for key in reversed(keys):
        seq.append(f"{KEYCODES[key]}:0") # release, essential to release in reverse order and avoid sticky keys. This was my first bug when I started using ydotool >.<
    subprocess.Popen(["/home/nhoaking/ydotool/build/ydotool", "key"] + seq)

def open_vscode(project_path): 
    """
    Open VSCode with a specified project and terminal toggle after 2 seconds.
    To control the terminal directory and environment,
    I set up a .vscode/settings.json file in each project.
    I could have used a function instead of a lambda, but I decided to stick to the 
    lambda method for consistency with other actions.
    """
    return lambda: (
        subprocess.Popen(["code", project_path]),
        time.sleep(2),
        hot_keys("CTRL", "GRAVE")
    )

def open_obsidian(vault_path):
    """
    Open Obsidian to my Zenith vault. 
    Obsidian supports command line argument to open specific vaults
    """
    return lambda: (
        subprocess.Popen(["obsidian", vault_path])
    )
    
def open_spotify():
    """
    Open Spotify if not running, otherwise toggle play/pause.
    I do this with playerctl which is a command line utility to control media players.
    Since this function takes no parameters, it does not need to be wrapped in a lambda
    as the previous functions.
    """
    not_open = subprocess.run(["pgrep", "-x", "spotify"], capture_output=True)
    if not_open.returncode == 0:
        # Spotify is running, then the button runs either play or pause
        subprocess.Popen(["playerctl", "--player=spotify", "play-pause"])
    else:
        # Spotify not running, the starts the app.
        subprocess.Popen(["spotify"])

def open_terminal_env():
    subprocess.Popen([os.path.join(BASHSCRIPTS_DIR, "open_jarvisbusybee_env_T.sh")])
    #subprocess.Popen(["/home/nhoaking/Zenith/jarvis-streamdeck/jarvis/assets/bash_scripts/open_jarvisbusybee_env_T.sh"])

def open_terminal():
    """
    The linux shortcut to open a new terminal window
    """
    hot_keys("CTRL", "ALT", "T")

def open_github():
    """
    Open my GitHub profile default web browser, in my case Chrome.
    I could have used webbrowser.open() but I prefer xdg-open for better compatibility.
    I wanted to also check if the browseer had already a tab with the url open, and if so, just focus that tab instead of opening a new one. I looked into the Chrome DevTools Protocol (CDP) which allows controlling Chrome/Chromium browsers via command line. It seemes too complex for this simple task, so I decided to just open a new tab with xdg-open instead. Furthermore, there seems to be some significant security risks. Since I am no expert in this, better to
    completely avoid it. Therefore, devTools approach will be discared entirely.
    """
    subprocess.Popen(["xdg-open", "https://github.com/NhoaKing-Tech"])

def open_youtube():
    """
    Open youtube in default web browser, in my case Chrome.
    """
    subprocess.Popen(["xdg-open", "https://www.youtube.com/"])

def open_freecodecamp():
    """
    Open freecodecamp website in default web browser, in my case Chrome.
    """
    subprocess.Popen(["xdg-open", "https://www.freecodecamp.org/"])

def open_chat():
    """
    Open ChatGPT in default web browser, in my case Chrome.
    """
    subprocess.Popen(["xdg-open", "https://chatgpt.com/"])

def open_claude():
    """
    Open Claude in default web browser, in my case Chrome.
    """
    subprocess.Popen(["xdg-open", "https://claude.ai/"])

# Microphone control and state check functions
def toggle_output_mute():
    """
    Function to toggle system audio output mute using amixer
    """
    subprocess.Popen(["amixer", "set", "Master", "toggle"])

def is_mic_muted():
    """
    Function to check microophone mute status using amixer
    """
    result = subprocess.run(
        ["amixer", "get", "Capture"],
        capture_output=True,
        text=True
    )
    return "[off]" in result.stdout  # True if mic muted

def toggle_mic(deck, key):
    """
    Function to toggle microphone mute and update the StreamDeck button icon.
    Returns a lambda function for use in layout definitions.
    """
    return lambda: (
        subprocess.run(["amixer", "set", "Capture", "toggle"]),
        render_keys(deck, key,
                   label="OFF" if is_mic_muted() else "ON",
                   icon="mic-off.png" if is_mic_muted() else "mic-on.png")
    )

# ------------------ Wrapper funtions to simplify action definitions in keys
def type_message():
    type_text("Hello World! :)")

def copy():
    """
    Super simple example for using hotkeys function
    """
    hot_keys("CTRL", "C")

# TO DO: Generalize the next function to work with other applications and to handle positioning and sizing of windows.
def nautilus_path(target_dir):
    """
    I want this function to open file manager windows or raise them if there is 
    already one open with my target directory. Instead of always opening a new Nautilus window, 
    I will first check if there is already one open with my target directory. 
    If there is, I will just bring it to the front (raise it).
    This prevents window clutter and gives me a better user experience. :)
    """

    # I need to convert the target directory to an absolute path because:
    # 1. Relative paths like "../folder" or "./folder" can be ambiguous
    # 2. os.path.abspath() converts these to full paths like "/home/user/folder"
    # 3. This ensures I am comparing the same format when checking window titles later
    # 4. It also resolves any symbolic links to their actual paths
    #    (Symbolic links are like shortcuts - they point to another file/directory.
    #     os.path.abspath() follows the shortcut to get the real location)
    target_dir = os.path.abspath(target_dir)

    # STEP 1: I need to check if Nautilus is already open with my target directory

    # wmctrl is a command-line tool that lets me interact with X11 windows in Linux
    # The "-lx" flags mean:
    # -l: list all windows
    # -x: include the WM_CLASS property (this helps me identify the application type)
    #
    # subprocess.check_output() runs this command and captures its text output
    # text=True ensures I get a string back instead of bytes
    wmctrl_output = subprocess.check_output(["wmctrl", "-lx"], text=True)

    # The wmctrl output looks like this (one line per window):
    # 0x02400003  0 org.gnome.Nautilus.org.gnome.Nautilus desktop file-browser - /home/user/Documents
    # 0x02600004  0 firefox.Firefox          desktop Firefox
    #
    # Each line contains: window_id, desktop_number, WM_CLASS, hostname, window_title
    # I need to parse each line to extract the information I need
    for line in wmctrl_output.splitlines():
        # I only care about Nautilus windows, so I check if "org.gnome.Nautilus"
        # is in the line. This is the WM_CLASS identifier for Nautilus windows.
        if "org.gnome.Nautilus" in line:

            # Now I need to extract the window ID and title from this line
            # line.split() breaks the line into parts separated by whitespace
            # The window ID is always the first part (index 0)
            # Example: "0x02400003" from the line above
            win_id = line.split()[0]

            # The window title starts from the 4th element (index 3) onwards
            # I use " ".join() to put the title back together with spaces
            # because the title might contain spaces that were split apart
            # Example: from "desktop file-browser - /home/user/Documents"
            # I want "file-browser - /home/user/Documents"
            window_title = " ".join(line.split()[3:])

            # Now I need to check if this Nautilus window is showing my target directory
            # There are different ways the directory might appear in the window title:

            # First, I get just the folder name (last part of the path)
            # os.path.basename("/home/user/Documents") returns "Documents"
            # This helps me match windows that might not show the full path
            folder_name = os.path.basename(target_dir)

            # I check three conditions to see if this window matches my target:
            if (target_dir in window_title or          # Full path is in title
                folder_name in window_title or        # Just folder name is in title
                window_title.endswith(folder_name)):  # Title ends with folder name

                # I found a matching window! Instead of opening a new one,
                # I will bring this existing window to the front (raise it)
                # print(f"Raising existing Nautilus window for {target_dir}")

                # wmctrl can also control windows, not just list them
                # -i: "use window ID" - I am giving it a window ID number (0x02400003)
                # instead of a window title/name (more reliable than titles)
                # -a: "activate window" - bring the window to front and give it focus
                # (like clicking on it in the taskbar)
                # win_id: the window ID I extracted earlier (like 0x02400003)
                subprocess.run(["wmctrl", "-i", "-a", win_id])

                # I found and raised the window, so I am done - return early
                # This prevents the function from continuing to Step 2
                return

    # STEP 2: If I get here, it means I did not find any existing Nautilus window
    # with my target directory, so I need to open a new one

    # print(f"Opening new Nautilus at {target_dir}")

    # subprocess.Popen() starts a new process without waiting for it to finish
    # This is perfect for GUI applications because:
    # 1. I don't want my Python script to hang waiting for Nautilus to close
    # 2. The user should be able to use Nautilus independently
    # 3. My script can continue with other tasks
    #
    # I pass the target directory as an argument to nautilus so it opens there
    subprocess.Popen(["nautilus", target_dir])
    
def release_all_keys():
    """
    In case of sticky keys, this function releases all keys. 
    It is called when the script exits or crashes. Second bug I found with ydotool >.<
    """
    releases = [f"{code}:0" for code in KEYCODES.values()]
    subprocess.Popen(
        ["/home/nhoaking/ydotool/build/ydotool", "key"] + releases
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

    Parameters:
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
        0: {"label": "Spotify for debugging", "icon": "spotify.png", "action": open_spotify},
        1: {"icon": "obsidian.png", "action": open_obsidian("/home/nhoaking/Zenith/zenith-cs-journey")},
        8: {"icon": "chatgpt.png", "action": open_chat},
        9: {"icon": "claude.png", "action": open_claude},

        2: {"icon": "jarviscode.png", "action": open_vscode("/home/nhoaking/Zenith/jarvis-streamdeck")},
        3: {"icon": "busybeecode.png", "action": open_vscode("/home/nhoaking/Zenith/busybee")},
        10: {"icon": "python.png", "action": switch_layout("python")},
        18: {"icon": "github.png", "color": "#2f3036", "action": open_github},
        19: {"icon": "git_layout.png", "color": "#2f3036", "action": switch_layout("git")},

        4: {"icon": "terminal.png", "action": open_terminal},
        5: {"icon": "terminalenv.png", "action": open_terminal_env},
        12: {"icon": "terminal_layout.png", "action": switch_layout("terminal_layout")},
        13: {"icon": "conda_layout.png", "action": switch_layout("conda_layout")},

        6: {"icon": "busybee.png", "action": switch_layout("busybee")}, #icon <a href="https://www.flaticon.com/free-icons/bee" title="bee icons">Bee icons created by Indielogy - Flaticon</a>

        7: {"icon": "nautilus.png", "action": lambda: nautilus_path("/home/nhoaking/Zenith/busybee")}, # <a href="https://www.flaticon.com/free-icons/files-and-folders" title="files and folders icons">Files and folders icons created by juicy_fish - Flaticon</a>
        #9: {"label": "Text", "color": "pink", "action": type_message},
        #10: {"label": "Copy", "color": "blue", "action": copy},
        #11: {"label": "Paste", "color": "pink", "action": paste},
        #12: {"label": "Hola", "color": "blue", "action": type_hola},
        #13: {"label": "More", "color": "purple", "action": lambda: switch_layout("terminal")},
        #14: {"icon": "shine.png", "action": open_shine},

        31: {"icon": "mic-fill.png", "action": toggle_mic(deck, 31)},
    }

    # Terminal layout
    layouts["terminal"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")}, #<div> Icons made by <a href="https://www.flaticon.com/authors/radhe-icon" title="Radhe Icon"> Radhe Icon </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
        1: {"label": "Run LS", "color": "pink", "action": type_text("ls\n")},
        2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet("hello")},
        3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet("python_boilerplate")},
    }

    layouts["busybee"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")},
        1: {"label": "Run LS", "color": "pink", "action": type_text("ls\n")},
        2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet("hello")},
        3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet("python_boilerplate")},
    }

    layouts["python"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")},
        1: {"label": "Run LS", "color": "pink", "action": type_text("ls\n")},
        2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet("hello")},
        3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet("python_boilerplate")},
    }

    layouts["git"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")},
        1: {"label": "Run LS", "color": "pink", "action": type_text("ls\n")},
        2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet("hello")},
        3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet("python_boilerplate")},
    }

    layouts["terminal_layout"] = { #<div> Icons made by <a href="https://www.flaticon.com/authors/icon-hubs" title="Icon Hubs"> Icon Hubs </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")},
        1: {"label": "Run LS", "color": "pink", "action": type_text("ls\n")},
        2: {"label": "Simple Snippet", "color": "blue", "action": insert_snippet("hello")},
        3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet("python_boilerplate")},
    }

    layouts["conda_layout"] = { #<div> Icons made by <a href="https://www.flaticon.com/authors/muhammad-ali" title="Muhammad Ali"> Muhammad Ali </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")},
        1: {"label": "List environments", "labelcolor": "#ff008c", "color": "#1c2e1c", "action": type_text("conda env list\n")},
        2: {"label": "List installed packages", "color": "#1c2e1c", "action": type_text("conda list\n")},
        3: {"label": "List package", "color": "#1c2e1c", "action": type_text("conda list <package>")},
        4: {"label": "Python version", "color": "#1c2e1c", "action": type_text("python --version\n")},
        5: {"label": "Activate env", "color": "#1c2e1c", "action": type_text("conda activate <env>")},
    }

# --- Avoid sticky keys, reset deck and close it ---
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
    Parameters:
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

    # --- Main with retry loop ---
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
