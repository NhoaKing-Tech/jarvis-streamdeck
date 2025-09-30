"""
-- GENERAL INFORMATION --
AUTHOR: NhoaKing (pseudonym for privacy)
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: layouts.py
-- DESCRIPTION --
Layout definitions for StreamDeck keys.
This module contains all layout configurations used by the jarvis application.
Each layout defines the complete key mapping for a specific mode or context.

Extracted from render.py to improve separation of concerns and maintainability.
"""

from typing import Dict, Any
from pathlib import Path
from actions import actions


def create_layouts(
    deck: Any,
    projects_path: Path,
    obsidian_vaults: Dict[str, str]
) -> Dict[str, Dict[int, Dict[str, Any]]]:
    """Create all layout definitions for the StreamDeck interface.

    This function generates all layout configurations used by the jarvis application.
    Each layout defines the complete key mapping for a specific mode or context
    (main, git tools, conda commands, etc.).

    Args:
        deck: StreamDeck device object (needed for some dynamic key functions)
        projects_path: Path to the projects directory
        obsidian_vaults: Dictionary mapping vault names to paths

    Returns:
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
    """
    # Import here to avoid circular imports - layouts depend on logic for switch_layout
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    from core.logic import switch_layout

    # =====================================================================================
    # STREAMDECK KEY LAYOUT GRID (32 keys total)
    # =====================================================================================
    # 0,     1,    2,   3,     4,    5,    6,    7
    # 8,     9,   10,   11,   12,   13,   14,   15
    # 16,   17,   18,   19,   20,   21,   22,   23
    # 24,   25,   26,   27,   28,   29,   30,   31

    # =====================================================================================
    # ACTION FUNCTION PATTERNS: Understanding how functions are called vs referenced
    # =====================================================================================
    #
    # This file demonstrates the two wrapper patterns explained in actions.py.
    # Pay attention to the presence or absence of parentheses in function calls:
    #
    # PATTERN 1: Functions WITH Arguments → Called with parentheses
    # =============================================================
    # These functions need arguments, so they are CALLED during layout creation:
    #
    #   "action": actions.toggle_mic(deck, 31)           # ✓ Called with arguments
    #   "action": actions.open_vscode(project_path)      # ✓ Called with arguments
    #   "action": actions.type_text("conda list\n")     # ✓ Called with arguments
    #   "action": actions.open_obsidian(vault_path)      # ✓ Called with arguments
    #   "action": switch_layout("main")                  # ✓ Called with arguments
    #
    # What happens: Function is called → returns wrapper function → StreamDeck stores wrapper
    # When key pressed: StreamDeck calls stored wrapper → actual work happens
    #
    # PATTERN 2: Functions WITHOUT Arguments → Referenced without parentheses
    # =======================================================================
    # These functions need no arguments, so they are REFERENCED directly:
    #
    #   "action": actions.terminal_env_jarvis            # ✓ No parentheses - function reference
    #   "action": actions.terminal_env_busybee           # ✓ No parentheses - function reference
    #   "action": actions.url_github                     # ✓ No parentheses - function reference
    #   "action": actions.spotify                        # ✓ No parentheses - function reference
    #   "action": actions.hk_terminal                    # ✓ No parentheses - function reference
    #
    # What happens: Function reference stored directly in layout
    # When key pressed: StreamDeck calls function → function executes immediately
    #
    # SPECIAL CASE: Lambda functions for inline argument passing
    # =========================================================
    # Sometimes we use lambda to pass arguments to functions that don't use wrapper pattern:
    #
    #   "action": lambda: actions.nautilus_path(str(projects_path))  # Lambda provides arguments
    #
    # This is used when the target function doesn't implement the factory pattern but needs arguments.
    #
    # DEBUGGING TIPS:
    # ===============
    # If a key doesn't work, check these common issues:
    # 1. Functions with arguments missing parentheses → key stores function instead of calling it
    # 2. Functions without arguments have parentheses → function called during layout creation
    # 3. Wrong return pattern in actions.py (wrapper vs wrapper()) → see actions.py documentation

    layouts = {}

    layouts["main"] = {
        # PATTERN 1 EXAMPLES: Functions WITH arguments → called with parentheses
        0: {"icon": "project1.png", "action": actions.open_vscode(str(projects_path / 'jarvis-streamdeck'))},  # Factory pattern: needs path argument
        1: {"icon": "project2.png", "action": actions.open_vscode(str(projects_path / 'busybee'))},           # Factory pattern: needs path argument
        2: {"icon": "project3.png", "action": actions.open_vscode(str(projects_path / 'pandora'))},           # Factory pattern: needs path argument
        3: {"icon": "project4.png", "action": actions.open_vscode(str(projects_path / 'nhoaking_website'))},  # Factory pattern: needs path argument

        # PATTERN 2 EXAMPLES: Functions WITHOUT arguments → referenced without parentheses
        4: {"icon": "commit.png", "action": actions.defaultbranch_commit},         # Direct reference: no arguments needed

        # PATTERN 1 EXAMPLES: Layout switching with arguments
        5: {"icon": "git_layout.png", "action": switch_layout("git_layout")},     # Factory pattern: needs layout name argument

        # PATTERN 2 EXAMPLES: URL functions without arguments
        6: {"icon": "github.png", "action": actions.url_github},                  # Direct reference: no arguments needed

        # PATTERN 1 EXAMPLES: More layout switching
        7: {"icon": "busybee_layout.png", "color": "#fdff8a", "action": switch_layout("busybee_layout")},  # Factory pattern: needs layout name

        # PATTERN 1 EXAMPLES: Obsidian with vault paths
        8: {"icon": "quartz.png", "action": actions.open_obsidian(obsidian_vaults.get('quartz', ''))},     # Factory pattern: needs vault path
        12: {"icon": "journal.png", "action": actions.open_obsidian(obsidian_vaults.get('journal', ''))}, # Factory pattern: needs vault path

        # SPECIAL CASE: Lambda functions to pass arguments to non-factory functions
        13: {"label": "Zenith", "icon": "nautilus.png", "action": lambda: actions.nautilus_path(str(projects_path))},           # Lambda wraps function that needs arguments
        14: {"label": "Busybee", "icon": "nautilus.png", "action": lambda: actions.nautilus_path(str(projects_path / 'busybee'))}, # Lambda wraps function that needs arguments

        # PATTERN 2 EXAMPLES: Terminal and application functions without arguments
        15: {"icon": "terminal_default.png", "action": actions.hk_terminal},      # Direct reference: no arguments needed
        16: {"icon": "terminal_jarvisbusybee.png", "action": actions.terminal_env_jarvis},  # Direct reference: no arguments needed
        17: {"icon": "terminal_busybee.png", "action": actions.terminal_env_busybee},       # Direct reference: no arguments needed
        20: {"icon": "freecodecamp.png", "action": actions.url_freecodecamp},     # Direct reference: no arguments needed
        21: {"icon": "claude.png", "action": actions.url_claude},                 # Direct reference: no arguments needed
        22: {"icon": "chatgpt.png", "action": actions.url_chatgpt},               # Direct reference: no arguments needed

        # PATTERN 1 EXAMPLES: Functions that return values when called
        23: {"icon": "key.png", "action": actions.type_keyring()},                # Factory pattern: needs to return configured function

        # PATTERN 1 EXAMPLES: More layout switching functions
        24: {"icon": "python_layout.png", "action": switch_layout("python_layout")},       # Factory pattern: needs layout name
        25: {"icon": "html_layout.png", "action": switch_layout("html_layout")},           # Factory pattern: needs layout name
        26: {"icon": "css_layout.png", "action": switch_layout("css_layout")},             # Factory pattern: needs layout name
        27: {"icon": "javascript_layout.png", "action": switch_layout("javascript_layout")}, # Factory pattern: needs layout name
        28: {"icon": "conda_layout.png", "action": switch_layout("conda_layout")},         # Factory pattern: needs layout name
        29: {"icon": "terminal_layout.png", "action": switch_layout("terminal_layout")},   # Factory pattern: needs layout name
        30: {"icon": "apps_layout.png", "action": switch_layout("apps")},                  # Factory pattern: needs layout name

        # PATTERN 1 EXAMPLE: The microphone toggle that was causing issues
        31: {"icon": "mic-fill.png", "action": actions.toggle_mic(deck, 31)},     # Factory pattern: needs deck and key arguments
    }

    # Terminal layout
    layouts["apps"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")}, #<div> Icons made by <a href="https://www.flaticon.com/authors/radhe-icon" title="Radhe Icon"> Radhe Icon </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
        1: {"icon": "spotify.png", "action": actions.spotify},
        2: {"icon": "youtube.png", "action": actions.url_youtube},
    }

    layouts["git_layout"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")}, #<div> Icons made by <a href="https://www.flaticon.com/authors/radhe-icon" title="Radhe Icon"> Radhe Icon </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
    }

    layouts["busybee_layout"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")}, #<div> Icons made by <a href="https://www.flaticon.com/authors/radhe-icon" title="Radhe Icon"> Radhe Icon </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
    }

    layouts["python_layout"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")}, #<div> Icons made by <a href="https://www.flaticon.com/authors/radhe-icon" title="Radhe Icon"> Radhe Icon </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
        1: {"label": "Simple Snippet", "color": "#31377e", "action": actions.type_snippet("function_class")},
    }

    layouts["html_layout"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")}, #<div> Icons made by <a href="https://www.flaticon.com/authors/radhe-icon" title="Radhe Icon"> Radhe Icon </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
    }

    layouts["css_layout"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")}, #<div> Icons made by <a href="https://www.flaticon.com/authors/radhe-icon" title="Radhe Icon"> Radhe Icon </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
    }

    layouts["javascript_layout"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")}, #<div> Icons made by <a href="https://www.flaticon.com/authors/radhe-icon" title="Radhe Icon"> Radhe Icon </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
    }

    # =====================================================================================
    # CONDA LAYOUT: Excellent examples of PATTERN 1 (Factory Pattern with Arguments)
    # =====================================================================================
    # This layout demonstrates the type_text() function pattern extensively.
    # Every type_text() call here uses PATTERN 1: function called with arguments.
    #
    # Notice: ALL type_text() calls have parentheses because they need text arguments.
    # Each call returns a wrapper function that will type the specified text when executed.
    layouts["conda_layout"] = {
        # Navigation back to main (also PATTERN 1 with layout name argument)
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")},

        # PATTERN 1 EXAMPLES: type_text() with various command strings
        # All of these are called during layout creation to configure what text to type
        1: {"label": "List envs", "color": "#1c2e1c", "action": actions.type_text("conda env list\n")},                         # Factory: returns function that types "conda env list\n"
        2: {"label": "Conda activate <env>", "color": "#1c2e1c", "action": actions.type_text("conda activate <env>")},         # Factory: returns function that types "conda activate <env>"
        3: {"label": "Conda deactivate <env>", "color": "#1c2e1c", "action": actions.type_text("conda deactivate\n")},        # Factory: returns function that types "conda deactivate\n"
        4: {"label": "List installed ALL packages", "color": "#1c2e1c", "action": actions.type_text("conda list\n")},         # Factory: returns function that types "conda list\n"
        5: {"label": "List install package", "color": "#1c2e1c", "action": actions.type_text("conda list <package>")},        # Factory: returns function that types "conda list <package>"
        6: {"label": "Python version", "color": "#1c2e1c", "action": actions.type_text("python --version\n")},               # Factory: returns function that types "python --version\n"
        7: {"label": "Activate env", "color": "#1c2e1c", "action": actions.type_text("conda activate <env>")},                # Factory: returns function that types "conda activate <env>"
        8: {"label": "Create new env", "color": "#1c2e1c", "action": actions.type_text("conda create -n <newenv> python=3.11.13")}, # Factory: returns function that types conda create command
        9: {"label": "Conda install", "color": "#1c2e1c", "action": actions.type_text("conda install ")},                    # Factory: returns function that types "conda install " (note trailing space)
        10: {"label": "Conda install conda-forge", "color": "#1c2e1c", "action": actions.type_text("conda install -c conda-forge ")}, # Factory: returns function that types conda-forge install command
        11: {"label": "Pip install", "color": "#1c2e1c", "action": actions.type_text("pip install ")},                       # Factory: returns function that types "pip install " (note trailing space)
        12: {"label": "Export env", "color": "#1c2e1c", "action": actions.type_text("conda env export > environment.yml\n")}, # Factory: returns function that types export command with newline
        13: {"label": "Recreate env", "color": "#1c2e1c", "action": actions.type_text("conda env create -f environment.yml\n")}, # Factory: returns function that types recreate command with newline
    }

    # KEY INSIGHT: Notice how some commands end with \n (auto-execute) while others don't (allow user to add parameters)
    # This is a UX design choice - complete commands get \n, partial commands (like "conda install ") don't.

    layouts["terminal_layout"] = {
        0: {"icon": "back.png", "color": "white", "action": switch_layout("main")}, #<div> Icons made by <a href="https://www.flaticon.com/authors/radhe-icon" title="Radhe Icon"> Radhe Icon </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
    }

    return layouts