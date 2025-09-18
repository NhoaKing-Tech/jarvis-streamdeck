# Table of Contents

* [run\_jarvis](#run_jarvis)
  * [load\_config](#run_jarvis.load_config)
  * [USER\_HOME](#run_jarvis.USER_HOME)
  * [YDOTOOL\_PATH](#run_jarvis.YDOTOOL_PATH)
  * [PROJECTS\_DIR](#run_jarvis.PROJECTS_DIR)
  * [OBSIDIAN\_VAULTS](#run_jarvis.OBSIDIAN_VAULTS)
  * [KEYRING\_PW](#run_jarvis.KEYRING_PW)
  * [layouts](#run_jarvis.layouts)
  * [current\_layout](#run_jarvis.current_layout)
  * [main](#run_jarvis.main)

<a id="run_jarvis"></a>

# run\_jarvis

NAME: run_jarvis.py
DESCRIPTION: Python script to run my stream deck XL with custom icons and actions.
AUTHOR: NhoaKing
FINISH DATE: September 14th 2025 (Sunday)
NOTE: IMPORTANT TO EXECUTE THIS SCRIPT FROM LINUX TERMINAL, AND NOT FROM THE VSCODE TERMINAL, AS THE SYSTEM CALLS (ydotool, wmctrl, etc.) ARE NOT WORKING PROPERLY WHEN EXECUTED FROM VSCODE TERMINAL. IF WHEN TESTED FROM LINUX TERMINAL THE SCRIPT WORKS AS EXPECTED, THEN IT WILL WORK THE SAME WHEN EXECUTED FROM THE SYSTEM SERVICE.

<a id="run_jarvis.load_config"></a>

#### load\_config

```python
def load_config()
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

**Notes**:

  The config.env file should be located in the same directory as this script.
  Each line should follow the format: KEY=VALUE

<a id="run_jarvis.USER_HOME"></a>

#### USER\_HOME

Returns Path object like /home/username or /Users/username

<a id="run_jarvis.YDOTOOL_PATH"></a>

#### YDOTOOL\_PATH

Defaults to 'ydotool' which relies on system PATH

<a id="run_jarvis.PROJECTS_DIR"></a>

#### PROJECTS\_DIR

Defaults to ~/Zenith

<a id="run_jarvis.OBSIDIAN_VAULTS"></a>

#### OBSIDIAN\_VAULTS

Dictionary to store vault_name -> vault_path mappings

<a id="run_jarvis.KEYRING_PW"></a>

#### KEYRING\_PW

Defaults to empty string if not configured

<a id="run_jarvis.layouts"></a>

#### layouts

Will be populated by create_layouts() after deck initialization

<a id="run_jarvis.current_layout"></a>

#### current\_layout

Start with the main layout as default

<a id="run_jarvis.main"></a>

#### main

```python
def main()
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

**Raises**:

- `SystemExit` - If StreamDeck hardware cannot be found after retry attempts

