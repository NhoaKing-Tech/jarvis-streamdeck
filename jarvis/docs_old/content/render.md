---
title: render
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-21
---

# render

-- GENERAL INFORMATION --
AUTHOR: NhoaKing
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: render.py
-- DESCRIPTION --
Rendering functions for StreamDeck keys.
This module handles the visual appearance of StreamDeck buttons and layout management.

How environment variables in config.env reach this module:
1. core.application calls config.initialization.init_jarvis()
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

## Functions

- [[#render_keys|render_keys()]]
- [[#render_layout|render_layout()]]
- [[#create_layouts|create_layouts()]]

## render_keys

```python
def render_keys():
```

Render the visual appearance of a StreamDeck key with icon and/or text.

This function handles the visual rendering of StreamDeck buttons, supporting
multiple display modes: icon only, text only, icon with text, or solid color.
It automatically handles text wrapping, icon scaling, and layout positioning.

**Args:**
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

**Raises:**
    RuntimeError: If render module not initialized

## render_layout

```python
def render_layout():
```

Render all keys for the given layout configuration.

This function updates the entire StreamDeck display by rendering each key
according to its configuration in the provided layout dictionary. It first
clears the existing display, then renders each configured key.

**Args:**
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

**Note:**
    Only renders visual elements. Key actions are handled by the logic module.

## create_layouts

```python
def create_layouts():
```

Create all layout definitions for the StreamDeck interface.

This function generates all layout configurations used by the jarvis application.
Each layout defines the complete key mapping for a specific mode or context
(main, git tools, conda commands, etc.).

**Args:**
    deck: StreamDeck device object (needed for some dynamic key functions)

**Returns:**
    dict: Dictionary mapping layout names to layout configurations

**Raises:**
    RuntimeError: If render module not initialized with required paths

## Additional Code Context

Other contextual comments from the codebase:

- **Line 44:** Functions from PILHelper from the original repo
- **Line 45:** PIL modules
- **Line 51:** Global configuration variables - set by config.initialization.init_module()
- **Line 52:** These are initialized to None and set during application startup via centralized initialization
- **Line 54:** Directories for UI assets
- **Line 55:** Path to font file for text rendering on keys
- **Line 56:** Directory containing icon files for StreamDeck keys
- **Line 58:** Configuration paths and user data
- **Line 59:** User's home directory path
- **Line 60:** User's main projects directory
- **Line 61:** Dictionary mapping vault names to paths
- **Line 62:** Password for keyring/password manager access
- **Line 64:** DESIGN PATTERN: Module-level Configuration with General Initialization
- **Line 65:** =======================================================================
- **Line 66:** This module now uses the general init_module() function from config.initialization
- ... and 65 more contextual comments
