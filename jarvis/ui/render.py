"""
Rendering functions for StreamDeck keys.
This module handles the visual appearance of StreamDeck buttons.
"""

import os
from StreamDeck.ImageHelpers import PILHelper # Functions from PILHelper from the original repo
from PIL import Image, ImageDraw, ImageFont # PIL modules
import textwrap

# Directories for assets - will be set by importing modules
FONT_DIR = None
ICONS_DIR = None

def initialize_render(font_dir, icons_dir):
    """Initialize the render module with required directories."""
    global FONT_DIR, ICONS_DIR
    FONT_DIR = font_dir
    ICONS_DIR = icons_dir

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