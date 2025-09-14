"""
Rendering functions for StreamDeck keys.
This module handles the visual appearance of StreamDeck buttons and layout management.
"""

import os
from StreamDeck.ImageHelpers import PILHelper # Functions from PILHelper from the original repo
from PIL import Image, ImageDraw, ImageFont # PIL modules
import textwrap
from actions import actions

# Directories for assets - will be set by importing modules
FONT_DIR = None
ICONS_DIR = None

# Configuration paths - will be set by importing modules
USER_HOME = None
PROJECTS_DIR = None
OBSIDIAN_VAULT = None

def initialize_render(font_dir, icons_dir, user_home=None, projects_dir=None, obsidian_vault=None):
    """Initialize the render module with required directories and paths."""
    global FONT_DIR, ICONS_DIR, USER_HOME, PROJECTS_DIR, OBSIDIAN_VAULT
    FONT_DIR = font_dir
    ICONS_DIR = icons_dir
    USER_HOME = user_home
    PROJECTS_DIR = projects_dir
    OBSIDIAN_VAULT = obsidian_vault

def render_keys(deck, key, label=None, icon=None, color="black", labelcolor="white"):
    """
    Function to handle the visual appearance of StreamDeck buttons or keys.
    I can display either an icon, text, or both on each key. It handles the four main cases:
    1. Icon and label: icon at top, label at bottom (it truncates if too long)
    2. Only label: centered text, wrapped to multiple lines if needed
    3. Only icon: maximized icon space
    4. Neither icon nor label: solid color (default red to indicate error)

    Arguments:
    deck: stream deck device
    key: key index (0-31 for my stream deck XL)
    label: text to display (none if no label is desired)
    icon: filename of icon to display (must be in ICONS_DIR)
    color: background color when no icon is used. Default is black.
    label_color: color for the text or label. Default is white.
    """

    if FONT_DIR is None or ICONS_DIR is None:
        raise RuntimeError("Render module not initialized. Call initialize_render() first.")

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

def render_layout(deck, layout):
    """
    Render all keys for the given layout.

    Arguments:
    deck: the stream deck device
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
    # Import here to avoid circular imports
    from .logic import switch_layout

    if PROJECTS_DIR is None:
        raise RuntimeError("Render module not initialized with required paths. Call initialize_render() first.")

    # Ensure PROJECTS_DIR is a Path object for safe operations
    from pathlib import Path
    projects_path = PROJECTS_DIR if hasattr(PROJECTS_DIR, '__truediv__') else Path(PROJECTS_DIR)

    # 0,     1,    2,   3,     4,    5,    6,    7
    # 8,     9,   10,   11,   12,   13,   14,   15
    # 16,   17,   18,   19,   20,   21,   22,   23
    # 24,   25,   26,   27,   28,   29,   30,   31

    layouts = {}

    # Main layout
    layouts["main"] = {
        0: {"icon": "spotify.png", "action": actions.open_spotify},
        1: {"icon": "obsidian.png", "action": actions.open_obsidian(OBSIDIAN_VAULT)},
        8: {"icon": "chatgpt.png", "action": actions.open_chat},
        9: {"icon": "claude.png", "action": actions.open_claude},
        16: {"icon": "freecodecamp.png", "action": actions.open_freecodecamp},


        2: {"icon": "jarviscode.png", "action": actions.open_vscode(str(projects_path / 'jarvis-streamdeck'))},
        3: {"icon": "busybeecode.png", "action": actions.open_vscode(str(projects_path / 'busybee'))},
        10: {"icon": "python.png", "action": switch_layout("python")},
        18: {"icon": "github.png", "color": "#2f3036", "action": actions.open_github},
        19: {"icon": "git_layout.png", "color": "#2f3036", "action": switch_layout("git")},

        4: {"icon": "terminal.png", "action": actions.open_terminal},
        5: {"icon": "terminalenv.png", "action": actions.open_terminal_env},
        12: {"icon": "terminal_layout.png", "action": switch_layout("terminal_layout")},
        13: {"icon": "conda_layout.png", "action": switch_layout("conda_layout")},

        6: {"icon": "busybee.png", "action": switch_layout("busybee")}, #icon <a href="https://www.flaticon.com/free-icons/bee" title="bee icons">Bee icons created by Indielogy - Flaticon</a>

        7: {"icon": "nautilus.png", "action": lambda: actions.nautilus_path(str(projects_path / 'busybee'))}, # <a href="https://www.flaticon.com/free-icons/files-and-folders" title="files and folders icons">Files and folders icons created by juicy_fish - Flaticon</a>
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

    return layouts