---
title: application
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-21
---

# application

-- GENERAL INFORMATION --
AUTHOR: NhoaKing
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: application.py
-- DESCRIPTION --
Core application logic for the jarvis StreamDeck system.

-- NOTE --
IMPORTANT TO EXECUTE FROM LINUX TERMINAL, NOT FROM VSCODE TERMINAL,
AS THE SYSTEM CALLS (ydotool, wmctrl, etc.) DON'T WORK PROPERLY IN VSCODE.
IF IT WORKS FROM A LINUX TERMINAL, IT WILL WORK THE SAME WHEN
EXECUTED FROM THE SYSTEM SERVICE.

ENTRY POINT:
This module is executed via jarvis/__main__.py when running:
    python -m jarvis

The application is started by:
    - Command line: python -m jarvis (from project root)
    - Systemd service: main.sh calls python -m jarvis
    - Alias: jarvis-test uses python -m jarvis

ARCHITECTURE OVERVIEW:
This is the core application logic for the jarvis StreamDeck system. It:
1. Loads configuration from config.env
2. Uses config.initialization.init_jarvis() for centralized module initialization
3. Discovers and connects to StreamDeck hardware
4. Sets up UI layouts and event handling
5. Manages application lifecycle and cleanup

The centralized initialization pattern ensures all modules (actions, render, lifecycle)
are configured consistently through a single function call.

## Functions

- [[#load_config|load_config()]]
- [[#main|main()]]

## load_config

```python
def load_config():
```

Load environment variables from config.env file into os.environ.

This function implements a simple .env file parser that reads environment
variables from a config.env file and loads them into the current process
environment. This approach allows for runtime configuration without
hardcoding paths or credentials in the source code.

Process:
    1. Reads the config.env file line by line
    2. Skips empty lines and comments (lines starting with #)
    3. Parses KEY=VALUE pairs and adds them to environment variables
    4. Gracefully handles missing config files

Performance:
    This function is called once at startup, so the file I/O overhead is
    negligible. We could cache the results, but since this runs only once,
    caching would add complexity without meaningful benefit.

**Note:**
    The config.env file should be located in the config directory.
    Each line should follow the format: KEY=VALUE

## main

```python
def main():
```

Main entry point for the jarvis StreamDeck application.

This function orchestrates the entire application startup process and handles
the complete lifecycle of the StreamDeck integration. It implements a robust
initialization sequence with retry logic for hardware discovery.

Process:
    1. Initializes all modules with required configuration
    2. Discovers and connects to StreamDeck hardware with retry logic
    3. Sets up UI layouts and event handling
    4. Registers signal handlers for graceful shutdown
    5. Enters the main event loop

Retry Mechanism:
    Uses a retry mechanism to handle temporary StreamDeck disconnections,
    USB timing issues, and device driver delays. Attempts connection for
    up to 5 minutes with 5-second intervals.

Signal Handling:
    Registers handlers for SIGINT (Ctrl+C) and sets up atexit cleanup
    to ensure proper resource cleanup on exit.

**Raises:**
    SystemExit: If StreamDeck hardware cannot be found after retry attempts

## Additional Code Context

Other contextual comments from the codebase:

- **Line 36:** Standard library imports for system interaction and typing
- **Line 37:** Registers functions to be called upon normal program termination
- **Line 38:** Provides time-related functions like sleep() for delays
- **Line 39:** Import os module for interacting with the operating system: file paths, env variables, etc.
- **Line 40:** Handles asynchronous events and signals from the OS, like SIGINT (Ctrl+C)
- **Line 41:** Provides access to system-specific parameters and functions, used for system exit to terminate the program
- **Line 42:** Type hints for dictionaries and generic types
- **Line 44:** Third-party StreamDeck library imports
- **Line 45:** NOTE: This imports from the original Elgato StreamDeck repository in ../src/
- **Line 46:** The StreamDeck library provides hardware abstraction for StreamDeck devices
- **Line 47:** Original repository. The StreamDeck library provides hardware abstraction for StreamDeck devices.
- **Line 48:** Installed inside my virtual environment in developer mode (pip install -e .). This ensures latest
- **Line 49:** local changes are always used. Execute "pip install -e ." inside the repo directory to install
- **Line 50:** in developer mode.
- **Line 51:** Class for the original repo to discover connected StreamDeck devices
- ... and 198 more contextual comments
