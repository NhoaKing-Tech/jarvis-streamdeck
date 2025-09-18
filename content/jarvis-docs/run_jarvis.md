---
title: run_jarvis
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-18
---

# run_jarvis

NAME: run_jarvis.py
DESCRIPTION: Python script to run my stream deck XL with custom icons and actions.
AUTHOR: NhoaKing
FINISH DATE: September 14th 2025 (Sunday)
NOTE: IMPORTANT TO EXECUTE THIS SCRIPT FROM LINUX TERMINAL, AND NOT FROM THE VSCODE TERMINAL, AS THE SYSTEM CALLS (ydotool, wmctrl, etc.) ARE NOT WORKING PROPERLY WHEN EXECUTED FROM VSCODE TERMINAL. IF WHEN TESTED FROM LINUX TERMINAL THE SCRIPT WORKS AS EXPECTED, THEN IT WILL WORK THE SAME WHEN EXECUTED FROM THE SYSTEM SERVICE.

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
    The config.env file should be located in the same directory as this script.
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
