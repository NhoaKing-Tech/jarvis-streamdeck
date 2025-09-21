"""
-- GENERAL INFORMATION --
AUTHOR: NhoaKing (pseudonym for privacy)
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: render.py
-- DESCRIPTION --
Rendering functions for StreamDeck keys.
This module handles the visual appearance of StreamDeck buttons and layout management.

How environment variables in config.env reach this module:
1. run_jarvis.py calls config.initialization.init_jarvis()
2. init_jarvis() uses init_module() to set global variables in this module
3. Global variables (FONT_DIR, ICONS_DIR, etc.) are used by rendering functions

This module uses the centralized initialization pattern for consistent configuration management.

Icon Attributions
HTML: <a href="https://www.flaticon.com/free-icons/html" title="html icons">Html icons created by Pixel perfect - Flaticon</a>
CSS: <a href="https://www.flaticon.com/free-icons/css" title="css icons">Css icons created by Pixel perfect - Flaticon</a>
JavaScript: <a href="https://www.flaticon.com/free-icons/javascript" title="javascript icons">Javascript icons created by Pixel perfect - Flaticon</a>
Code space project 1: <a href="https://www.flaticon.com/free-icons/code" title="code icons">Code icons created by Freepik - Flaticon</a> JARVIS
Code space project 2: <a href="https://www.flaticon.com/free-icons/code" title="code icons">Code icons created by Freepik - Flaticon</a> BUSYBEE
Code space project 3: <a href="https://www.flaticon.com/free-icons/code" title="code icons">Code icons created by Freepik - Flaticon</a> PANDORA
Code space project 4: <a href="https://www.flaticon.com/free-icons/code" title="code icons">Code icons created by Freepik - Flaticon</a> WEBSITE
Markdown project 1: <a href="https://www.flaticon.com/free-icons/markdown" title="markdown icons">Markdown icons created by brajaomar_j - Flaticon</a>
Markdown project 2: <a href="https://www.flaticon.com/free-icons/markdown" title="markdown icons">Markdown icons created by brajaomar_j - Flaticon</a>
Markdown project 3: <a href="https://www.flaticon.com/free-icons/markdown" title="markdown icons">Markdown icons created by brajaomar_j - Flaticon</a>
Markdown project 4: <a href="https://www.flaticon.com/free-icons/markdown" title="markdown icons">Markdown icons created by brajaomar_j - Flaticon</a>
Bluebumblebee (My icon for my database): <a href="https://www.flaticon.com/free-icons/bumblebee" title="bumblebee icons">Bumblebee icons created by Indielogy - Flaticon</a>
GitHub Icon: https://remixicon.com/
Conda Icon: <a href="https://www.flaticon.com/free-icons/snake" title="snake icons">Snake icons created by Freepik - Flaticon</a>
Journal1: <a href="https://www.flaticon.com/free-icons/book" title="book icons">Book icons created by Freepik - Flaticon</a>
Journal2: <a href="https://www.flaticon.com/free-icons/studying" title="studying icons">Studying icons created by Freepik - Flaticon</a>
Git Commit: <a href="https://www.flaticon.com/free-icons/commit-git" title="commit git icons">Commit git icons created by Freepik - Flaticon</a>
Git layout: <a href="https://www.flaticon.com/free-icons/git" title="git icons">Git icons created by Freepik - Flaticon</a>
Terminal <a href="https://www.flaticon.com/free-icons/terminal" title="terminal icons">Terminal icons created by Arkinasi - Flaticon</a>
apps layout: <a href="https://www.flaticon.com/free-icons/more" title="more icons">More icons created by Vector Squad - Flaticon</a>
PW: <a href="https://www.flaticon.com/free-icons/password" title="password icons">Password icons created by kostop - Flaticon</a>
Youtube icon: <a href="https://www.flaticon.com/free-icons/logo" title="logo icons">Logo icons created by Alfredo Creates - Flaticon</a>
quartz vault: <a href="https://www.flaticon.com/free-icons/markdown" title="markdown icons">Markdown icons created by brajaomar_j - Flaticon</a>
"""

import os
from StreamDeck.ImageHelpers import PILHelper # Functions from PILHelper from the original repo
from PIL import Image, ImageDraw, ImageFont # PIL modules
import textwrap
from actions import actions
from typing import Optional, Dict, Any
from pathlib import Path

# Global configuration variables - set by config.initialization.init_module()
# These are initialized to None and set during application startup via centralized initialization

# Directories for UI assets
FONT_DIR: Optional[Path] = None      # Path to font file for text rendering on keys
ICONS_DIR: Optional[Path] = None     # Directory containing icon files for StreamDeck keys

# Configuration paths and user data
USER_HOME: Optional[Path] = None     # User's home directory path
PROJECTS_DIR: Optional[Path] = None  # User's main projects directory
OBSIDIAN_VAULTS: Optional[Dict[str, str]] = None  # Dictionary mapping vault names to paths
KEYRING_PW: Optional[str] = None     # Password for keyring/password manager access

# DESIGN PATTERN: Module-level Configuration with General Initialization
# =======================================================================
# This module now uses the general init_module() function from config.initialization
# instead of having its own initialization function. This reduces code duplication
# and provides a consistent initialization pattern across all jarvis modules.
#
# INITIALIZATION:
# The config.initialization.init_module() function sets the global variables
# (FONT_DIR, ICONS_DIR, USER_HOME, PROJECTS_DIR, OBSIDIAN_VAULTS, KEYRING_PW)
# by calling setattr(module, key, value) for each configuration parameter.

def render_keys(deck: Any, key: int, label: Optional[str] = None, icon: Optional[str] = None, color: str = "black", labelcolor: str = "white") -> None:
    """Render the visual appearance of a StreamDeck key with icon and/or text.

    This function handles the visual rendering of StreamDeck buttons, supporting
    multiple display modes: icon only, text only, icon with text, or solid color.
    It automatically handles text wrapping, icon scaling, and layout positioning.

    Args:
        deck: StreamDeck device object
        key (int): Key index (0-31 for StreamDeck XL)
        label (str, optional): Text to display on the key
        icon (str, optional): Filename of icon to display (must be in ICONS_DIR)
        color (str): Background color when no icon used. Defaults to "black"
        labelcolor (str): Text color for labels. Defaults to "white"

    Display Modes:
        1. **Icon and label**: Icon at top, label at bottom (truncated if too long)
        2. **Only label**: Centered text, wrapped to multiple lines if needed
        3. **Only icon**: Maximized icon space with minimal margins
        4. **Neither**: Solid color background (red if color not specified, indicates error)

    Text Handling:
        - Automatically calculates character width for proper text wrapping
        - Truncates long labels with "..." when combined with icons
        - Centers text both horizontally and vertically
        - Uses custom font with fallback to system default

    Icon Handling:
        - Scales icons to fit key dimensions with appropriate margins
        - Handles missing icon files gracefully with fallback colors
        - Supports PNG format icons optimized for 96x96 pixel keys

    Raises:
        RuntimeError: If render module not initialized
    """

    if FONT_DIR is None or ICONS_DIR is None:
        raise RuntimeError("Render module not initialized. Call config.initialization.init_jarvis() first.")

    # I load my custom font, with fallback to system default if it fails
    try:
        font = ImageFont.truetype(FONT_DIR, 16) # I am using 16 for my 96x96 keys.
    except OSError:
        print("Could not load your custom font, check the font path and the font format (it must be .ttf).")
        font = ImageFont.load_default()

    # Case 1: Both icon and label
    if label and icon:
        icon_path = ICONS_DIR / icon
        if icon_path.exists():
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
        icon_path = ICONS_DIR / icon
        if icon_path.exists():
            icon_img = Image.open(icon_path)
            # No margins needed, maximize icon space
            key_image = PILHelper.create_scaled_key_image(deck, icon_img, margins=(5, 5, 5, 5), background=color)
        else:
            print(f"Warning: icon {icon_path} not found, falling back to color red")
            key_image = PILHelper.create_key_image(deck, background="red")

    # Case 4: Neither icon nor label, just color. Default to red to indicate a problem, signaling that nothing has been set for this key.
    else:
        key_image = PILHelper.create_key_image(deck, background=color if color else "red")

    # Set the key image on the deck
    deck.set_key_image(key, PILHelper.to_native_key_format(deck, key_image)) # set_key_image comes from StreamDeck.py from the original repo
    # to_native_key_format comes from PILHelper.py from the original repo

def render_layout(deck: Any, layout: Dict[int, Dict[str, Any]]) -> None:
    """Render all keys for the given layout configuration.

    This function updates the entire StreamDeck display by rendering each key
    according to its configuration in the provided layout dictionary. It first
    clears the existing display, then renders each configured key.

    Args:
        deck: StreamDeck device object
        layout (dict): Layout dictionary mapping key numbers to configurations

    Layout Structure:
        The layout dictionary maps key numbers (0-31) to configuration dictionaries:
        ```
        {
            0: {"icon": "spotify.png", "action": some_function},
            1: {"label": "Terminal", "color": "blue", "action": another_function},
            ...
        }
        ```

    Process:
        1. Validates deck is open and available
        2. Resets/clears all existing key displays
        3. Sets brightness to 100%
        4. Renders each key according to its configuration

    Configuration Keys:
        - **label**: Text to display on the key
        - **icon**: Icon filename (from ICONS_DIR)
        - **color**: Background color
        - **labelcolor**: Text color
        - **action**: Function to call when key is pressed (not used in rendering)

    Note:
        Only renders visual elements. Key actions are handled by the logic module.
    """
    if not deck or not deck.is_open(): # exits if deck is not initialized before the loop to render keys
        return
    deck.reset()  # clear old icons
    deck.set_brightness(100) # set brightness to 50% (0-100) # from StreamDeck.py from the original repo
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
            config.get("color", "black"), # the background color of the key (if specified)
            config.get("labelcolor", "white") # the color of the text label (if specified)
        )

def create_layouts(deck: Any) -> Dict[str, Dict[int, Dict[str, Any]]]:
    """Create all layout definitions for the StreamDeck interface.

    This function generates all layout configurations used by the jarvis application.
    Each layout defines the complete key mapping for a specific mode or context
    (main, git tools, conda commands, etc.).

    Args:
        deck: StreamDeck device object (needed for some dynamic key functions)

    Returns:
        dict: Dictionary mapping layout names to layout configurations

    Raises:
        RuntimeError: If render module not initialized with required paths
    """
    # Import here to avoid circular imports
    from .layouts import create_layouts as create_layouts_impl

    if PROJECTS_DIR is None:
        raise RuntimeError("Render module not initialized with required paths. Call initialize_render() first.")
    if OBSIDIAN_VAULTS is None:
        raise RuntimeError("Render module not initialized with required paths. Call initialize_render() first.")

    # Ensure PROJECTS_DIR is a Path object for safe operations
    from pathlib import Path
    projects_path = PROJECTS_DIR if hasattr(PROJECTS_DIR, '__truediv__') else Path(PROJECTS_DIR)

    return create_layouts_impl(deck, projects_path, OBSIDIAN_VAULTS)
