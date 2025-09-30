---
title: layouts
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-21
---

# layouts

-- GENERAL INFORMATION --
AUTHOR: NhoaKing (pseudonym for privacy)
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: layouts.py
-- DESCRIPTION --
Layout definitions for StreamDeck keys.
This module contains all layout configurations used by the jarvis application.
Each layout defines the complete key mapping for a specific mode or context.

Extracted from render.py to improve separation of concerns and maintainability.

## Functions

- [[#create_layouts|create_layouts()]]

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
    projects_path: Path to the projects directory
    obsidian_vaults: Dictionary mapping vault names to paths

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
    - Project paths from projects_path
    - Obsidian vault paths from obsidian_vaults
    - User-specific directories and tools

## Additional Code Context

Other contextual comments from the codebase:

- **Line 69:** Import here to avoid circular imports - layouts depend on logic for switch_layout
- **Line 76:** =====================================================================================
- **Line 77:** STREAMDECK KEY LAYOUT GRID (32 keys total)
- **Line 78:** =====================================================================================
- **Line 79:** 0,     1,    2,   3,     4,    5,    6,    7
- **Line 80:** 8,     9,   10,   11,   12,   13,   14,   15
- **Line 81:** 16,   17,   18,   19,   20,   21,   22,   23
- **Line 82:** 24,   25,   26,   27,   28,   29,   30,   31
- **Line 84:** =====================================================================================
- **Line 85:** ACTION FUNCTION PATTERNS: Understanding how functions are called vs referenced
- **Line 86:** =====================================================================================
- **Line 88:** This file demonstrates the two wrapper patterns explained in actions.py.
- **Line 89:** Pay attention to the presence or absence of parentheses in function calls:
- ... and 113 more contextual comments
