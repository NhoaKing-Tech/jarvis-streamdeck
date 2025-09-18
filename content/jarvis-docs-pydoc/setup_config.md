# Table of Contents

* [setup\_config](#setup_config)
  * [create\_config](#setup_config.create_config)
  * [which\_ydotool](#setup_config.which_ydotool)

<a id="setup_config"></a>

# setup\_config

Setup script to create personalized configuration for Jarvis StreamDeck.

This script provides an interactive configuration wizard that helps users
set up their jarvis environment by creating a personalized config.env file.
It handles path detection, user prompts, and configuration file generation.

Purpose:
- Simplify initial jarvis setup for new users
- Generate properly formatted configuration files
- Detect system-specific paths and tools
- Prevent common configuration errors

Usage:
    python setup_config.py

Output:
    Creates config.env file with user-specific configuration

<a id="setup_config.create_config"></a>

#### create\_config

```python
def create_config()
```

Create a personalized config.env file through interactive prompts.

This function implements an interactive configuration wizard that guides
users through setting up their jarvis environment. It provides intelligent
defaults, validates input, and generates a properly formatted configuration file.

Process:
    1. Checks for existing configuration and asks about overwriting
    2. Provides intelligent defaults based on system detection
    3. Prompts user for key configuration values
    4. Generates properly formatted config.env file
    5. Provides usage instructions

Configuration Strategy:
    - Uses sensible defaults that work for most users
    - Allows empty input to accept defaults (user-friendly)
    - Validates critical paths where possible
    - Generates self-documenting configuration file

Error Handling:
    - Checks for existing config files to prevent accidental overwrites
    - Handles file write permissions gracefully
    - Provides clear feedback and instructions

Generated Configuration:
    Creates config.env with paths for ydotool, projects directory,
    and Obsidian vaults, plus comments for additional options.

<a id="setup_config.which_ydotool"></a>

#### which\_ydotool

```python
def which_ydotool()
```

Find ydotool executable in system PATH with intelligent fallbacks.

This function attempts to locate the ydotool executable using multiple
strategies to handle different installation methods and system configurations.

**Returns**:

- `str` - Path to ydotool executable, or a reasonable fallback
  
  Detection Strategy:
  1. Check system PATH using shutil.which()
  2. Fall back to common installation locations
  3. Provide user-friendly default that can be manually corrected
  
  Installation Methods Supported:
  - Package manager installation (apt, yum, pacman, etc.)
  - Manual compilation and installation
  - Local user installation
  - Custom installation paths
  
  Fallback Locations:
  - /usr/local/bin/ydotool (manual compilation default)
  - /usr/bin/ydotool (package manager installation)
  - /opt/ydotool/bin/ydotool (custom installation)
  - ~/.local/bin/ydotool (user-local installation)
  

**Notes**:

  If no ydotool installation is found, returns a reasonable default
  path that the user can correct during the interactive setup.

