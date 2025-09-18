---
title: render
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-18
---

# render

Rendering functions for StreamDeck keys.
This module handles the visual appearance of StreamDeck buttons and layout management.

## Functions

- [[#initialize_render|initialize_render()]]
- [[#render_keys|render_keys()]]
- [[#render_layout|render_layout()]]
- [[#create_layouts|create_layouts()]]

## initialize_render

```python
def initialize_render():
```

Initialize the render module with required directories and paths.

This function sets up the global configuration variables needed by the render
module to create layouts and render StreamDeck keys. It implements dependency
injection to keep configuration centralized.

**Args:**
    font_dir (str): Path to font file for text rendering on keys
    icons_dir (str): Directory containing icon files for StreamDeck keys
    user_home (Path, optional): User's home directory path
    projects_dir (Path, optional): User's main projects directory
    obsidian_vaults (dict, optional): Dictionary mapping vault names to paths
    keyring_pw (str, optional): Password for keyring access

**Note:**
    This function must be called before any render functions are used,
    typically during application startup.

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

Layout Structure:
    Each layout maps key positions (0-31) to configuration dictionaries:
    ```
    {
        "main": {
            0: {"icon": "project1.png", "action": open_vscode("/path")},
            1: {"label": "Terminal", "action": hk_terminal},
            ...
        },
        "git_layout": {
            0: {"icon": "back.png", "action": switch_layout("main")},
            ...
        }
    }
    ```

Available Layouts:
    - **main**: Primary interface with projects, tools, and navigation
    - **apps**: Application launchers (Spotify, YouTube, etc.)
    - **git_layout**: Git operations and code snippets
    - **python_layout**: Python development tools
    - **conda_layout**: Conda environment management commands
    - **terminal_layout**: Terminal and command-line tools
    - Language-specific layouts: html_layout, css_layout, javascript_layout

Dynamic Elements:
    Some layouts include dynamic elements that depend on configuration:
    - Project paths from PROJECTS_DIR
    - Obsidian vault paths from OBSIDIAN_VAULTS
    - User-specific directories and tools

**Raises:**
    RuntimeError: If render module not initialized with required paths
