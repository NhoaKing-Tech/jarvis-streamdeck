---
title: actions
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-21
---

# actions

-- GENERAL INFORMATION --
AUTHOR: NhoaKing (pseudonym for privacy)
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: actions.py
-- DESCRIPTION -- 
Python module containing all the actions triggered by key press events on the stream deck XL from ElGato
This module bridges key events (key presses) with system operations.

How environment variables in config.env reach this module:
1. systemd jarvis.service loads config.env via 'EnvironmentFile'.
2. jarvis.service starts main.sh: this script activates the venv and runs main.py
3. main.py delegates to core.application which reads environment variables using os.getenv()
4. core.application calls config.initialization.init_jarvis() with all configuration
5. init_jarvis() uses the general init_module() function to set global variables in this module
6. This module stores them in global variables for use by action functions

This uses a Global Configuration with Dynamic Initialization pattern.

Why not read environment variables directly in this module?
We could have each action function call os.getenv() directly, but I chose
centralized global configuration instead because:
- Keeps configuration loading centralized in core.application, so it is easier to maintain
- Makes dependencies explicit (you can see what each module needs)
- Better separation of concerns (core.application handles config, this module handles actions)

The .env file provides the configuration, not the logic itself. The logic is provided through initialization.py and core.application.py
Configuration flows: config.env -> systemd -> main.sh -> main.py -> core.application -> config.initialization -> actions.py

This module handles so far the following topics. Function names are listed for each.
1. Opening of URLs in default browser. In my case, Google Chrome. Functions here are:
- url_freecodecamp
- url_youtube
- url_github
- url_claude
- url_chatgpt
2. Open spotify or trigger play/pause 
- spotify
3. Microphone ON/OFF toggle
Achieved via:
- is_mic_muted
- toggle_mic
4.Trigger hotkeys/shortcuts
- hot_keys
- Example of usage in hk_terminal and copy
5. Open VSCode with a given project path.
- open_vscode
Control of vscode appearance for each project is done through the 
hidden .vscode folder inside the project directory and the file settings.json
6. Type text and text blocks or snippets
- type_text
- type_snippet
- type_keyring: Type and enter passwords without exposing them in your codebase. The password can be stored in config.env
7. Open obsidian with a given vault path. It supports the possibility to open multiple vaults, so you can reuse the function in different keys for different vaults.
- open_obsidian
8. Execute bash scripts
- execute_bash
- Example of usage in terminal_env_jarvis and terminal_env_busybee for basic scripts
- Example of advanced usage with git_commit_workflow.sh
9. Open nautilus windows with a target path. If that path is already open in another window, simply raise it, to avoid multiple nautilus windows with the same path..... simply raise it, to avoid multiple nautilus windows with the same path..... which happens often if this check is not in place before opening the window. 
This was the trigger to change to X11 from Wayland, as Wayland does not support window management in a straightforward way as X11 does, and it was giving me too many headaches. I do not discard in the future to TRY to implement jarvis in wayland.

-- TO DO --
- Generalize nautilus_path function to work with other applications too (for obsidian is already done)
- Handle positioning and sizing of windows, at the moment everything opens correctly but super randomly placed and sized... >_<

## Architecture & Design Decisions

**Line 86:** Initialization flow:

**Line 87:** 1. These variables are declared as None (creates the module attributes)

**Line 88:** 2. core.application calls init_jarvis() which internally calls init_module(actions, ...)

**Line 89:** 3. init_module() uses hasattr(actions, 'YDOTOOL_PATH') to verify attribute exists

**Line 90:** 4. init_module() uses setattr(actions, 'YDOTOOL_PATH', actual_value) to set real values

**Line 91:** 5. Action functions check if variables are still None to detect initialization failures

## Educational Notes & Computer Science Concepts

### ==================================================...

```
=====================================================================================
COMPUTER SCIENCE EDUCATION: DESIGN PATTERNS COMPARISON
=====================================================================================
```

### WHAT WE'RE ACTUALLY USING: Global Configuration wi...

```
WHAT WE'RE ACTUALLY USING: Global Configuration with Dynamic Initialization
===========================================================================
Our pattern stores configuration in module-level global variables that are set at runtime.
This approach provides:
1. TESTABILITY: Easy to mock configuration by setting globals for unit tests
2. FLEXIBILITY: Can be configured differently for different environments
3. PERFORMANCE: Configuration accessed directly without repeated file reads or imports
4. ERROR HANDLING: Can detect and report missing configuration with None checks
```

### HOW OUR PATTERN WORKS:

```
HOW OUR PATTERN WORKS:
1. Declare global variables as None (creates module attributes)
2. At startup, init_module() uses setattr() to set real values
3. Functions access these globals directly: if YDOTOOL_PATH is None: ...
4. Configuration is "injected" into the module, not into individual functions
```


## Development Notes & Implementation Details

- **Line 81:** These global variable declarations are MANDATORY for the init_module() pattern to work.
- **Line 82:** The config.initialization.init_module() function uses hasattr() to check if each variable
- **Line 83:** exists in this module's namespace before attempting to set its value with setattr().
- **Line 84:** Without these declarations, hasattr() returns False and initialization silently fails.

## Functions

- [[#url_freecodecamp|url_freecodecamp()]]
- [[#url_youtube|url_youtube()]]
- [[#url_github|url_github()]]
- [[#url_claude|url_claude()]]
- [[#url_chatgpt|url_chatgpt()]]
- [[#spotify|spotify()]]
- [[#is_mic_muted|is_mic_muted()]]
- [[#toggle_mic|toggle_mic()]]
- [[#hot_keys|hot_keys()]]
- [[#hk_terminal|hk_terminal()]]
- [[#hk_copy|hk_copy()]]
- [[#open_vscode|open_vscode()]]
- [[#type_text|type_text()]]
- [[#type_keyring|type_keyring()]]
- [[#type_snippet|type_snippet()]]
- [[#open_obsidian|open_obsidian()]]
- [[#execute_bash|execute_bash()]]
- [[#terminal_env_jarvis|terminal_env_jarvis()]]
- [[#terminal_env_busybee|terminal_env_busybee()]]
- [[#defaultbranch_commit|defaultbranch_commit()]]
- [[#nautilus_path|nautilus_path()]]
- [[#wrapper|wrapper()]]
- [[#execute|execute()]]
- [[#wrapper|wrapper()]]
- [[#wrapper|wrapper()]]
- [[#wrapper|wrapper()]]
- [[#wrapper|wrapper()]]

## url_freecodecamp

```python
def url_freecodecamp():
```

Open freeCodeCamp website in the default web browser.

Quick access to freeCodeCamp learning platform for coding tutorials,
challenges, and educational content.

EDUCATIONAL WORKFLOW:
Having quick access to learning platforms supports continuous learning
and skill development during coding sessions.

## url_youtube

```python
def url_youtube():
```

Open YouTube in the default web browser.

Simple utility function to quickly access YouTube using the system's
default web browser via xdg-open standard.

DESIGN CONSISTENCY:
Follows same pattern as other web-opening functions for consistency
and predictable behavior across all web-based StreamDeck actions.

## url_github

```python
def url_github():
```

Open GitHub profile in the default web browser.

This function opens the GitHub profile page using the system's default web browser.
It uses xdg-open which is the standard Linux way to open URLs and files with
their associated default applications.

BROWSER INTEGRATION DECISIONS:
Originally considered checking for existing browser tabs and focusing them
instead of opening new tabs. This would involve Chrome DevTools Protocol (CDP)
or similar browser automation tools.

WHY SIMPLE APPROACH WAS CHOSEN:
- CDP is complex and overkill for simple URL opening
- Security risks with browser automation protocols
- xdg-open is simpler, safer, and more reliable
- Works with any browser (Chrome, Firefox, Edge, etc.)
- Respects user's default browser preference

TECHNICAL DETAILS:
- xdg-open delegates to desktop environment's URL handler
- Most browsers will reuse existing windows when possible
- URL opening is non-blocking (doesn't freeze jarvis)

ALTERNATIVE METHODS CONSIDERED:
- webbrowser.open(): Python standard library, but less robust on Linux
- Direct browser commands: Browser-specific, not portable
- CDP/WebDriver: Overkill and security risks for simple URL opening

## url_claude

```python
def url_claude():
```

Open Claude AI in the default web browser.

Provides quick access to Anthropic's Claude AI assistant for coding help,
analysis, and development support.

AI WORKFLOW INTEGRATION:
Having multiple AI assistants available allows choosing the best tool
for specific tasks (Claude for analysis, ChatGPT for coding, etc.).

## url_chatgpt

```python
def url_chatgpt():
```

Open ChatGPT in the default web browser.

Provides quick access to ChatGPT for coding assistance, problem-solving,
and AI-powered development support during coding sessions.

AI INTEGRATION WORKFLOW:
Quick access to AI assistants supports modern development practices
where AI tools are used for code review, debugging, and learning.

## spotify

```python
def spotify():
```

Smart Spotify control: launch if not running, otherwise toggle play/pause.

This function implements intelligent Spotify management:
- If Spotify is not running: Launch the application
- If Spotify is running: Toggle play/pause state

This dual behavior makes the StreamDeck key work like a smart media button
that adapts based on current state.

TECHNICAL IMPLEMENTATION:
- Uses pgrep to check if Spotify process is running
- Uses playerctl for media control (works with any MPRIS-compatible player)
- Non-blocking execution for responsive UI

PLAYERCTL ADVANTAGES:
- Works with multiple media players (Spotify, VLC, Firefox, etc.)
- Provides standardized media control interface
- Handles player focus and switching automatically
- More reliable than application-specific APIs

DESIGN DECISION: No lambda wrapper needed
This function doesn't take parameters and executes immediately,
so it doesn't need the factory pattern used by parameterized functions.

## is_mic_muted

```python
def is_mic_muted():
```

Check if the microphone is currently muted using amixer.

This function uses the ALSA amixer command to query the current state
of the Capture (microphone) audio device.

**Returns:**
    bool: True if microphone is muted ("[off]" in output), False if active

**Note:**
    Requires amixer to be installed and the Capture device to be available.
    This is the standard microphone control on most Linux systems.

## toggle_mic

```python
def toggle_mic():
```

Create a function that toggles microphone mute and updates the StreamDeck icon.

This function implements a factory pattern that returns a callable which,
when executed, will toggle the microphone mute state and immediately update
the corresponding StreamDeck key with appropriate visual feedback.

**Args:**
    deck: StreamDeck device object for updating key appearance
    key (int): Key number (0-31) to update with new icon and label

**Returns:**
    callable: Function that performs the mic toggle when called

Visual Feedback:
    - Muted: Shows "OFF" label with "mic-off.png" icon
    - Active: Shows "ON" label with "mic-on.png" icon

**Note:**
    Uses amixer to control the Capture device. Requires ALSA to be configured.

## hot_keys

```python
def hot_keys():
```

Simulate a hotkey combination using ydotool.

This function presses multiple keys simultaneously (like Ctrl+C, Alt+Tab, etc.)
and releases them in the correct order to avoid "sticky key" issues.

**Args:**
    *keys: Variable number of key names (e.g., "CTRL", "C" for Ctrl+C)

Technical Details:
    - Keys are pressed in the order specified (left to right)
    - Keys are released in reverse order (right to left) to prevent sticky keys
    - Each key event is formatted as "keycode:state" (1=press, 0=release)
    - All events are sent in a single ydotool command for atomic execution

Example:
    - hot_keys("CTRL", "C") -> Press Ctrl, press C, release C, release Ctrl

**Raises:**
    RuntimeError: If actions module not initialized
    ValueError: If unknown key name provided

**Note:**
    Reverse release order prevents modifier keys from remaining "stuck"
    after the hotkey sequence completes.

## hk_terminal

```python
def hk_terminal():
```

Open a new terminal window using the standard Linux desktop hotkey.

This function simulates the Ctrl+Alt+T keyboard shortcut which is the
standard way to open a terminal window across most Linux desktop environments.
This approach respects the user's default terminal preference and integrates
properly with the desktop environment's window management.

Desktop Environment Compatibility:
    - **GNOME**: Opens gnome-terminal
    - **KDE**: Opens konsole
    - **XFCE**: Opens xfce4-terminal
    - **i3/sway**: Opens configured terminal ($TERMINAL)
    - **Others**: Opens system default terminal

Advantages:
    - Respects user's default terminal preference
    - Works consistently across different desktop environments
    - Faster than discovering and launching specific terminal executable
    - Integrates with desktop environment's window management

**Note:**
    This is preferred over direct terminal commands because it uses the
    desktop environment's configured default rather than hardcoding a
    specific terminal emulator.

## hk_copy

```python
def hk_copy():
```

Copy selected text to clipboard using Ctrl+C hotkey.

Simple demonstration of the hot_keys function that sends the standard
copy-to-clipboard keyboard shortcut.

**Note:**
This is a basic example of hotkey usage.

## open_vscode

```python
def open_vscode():
```

Create a function that opens Visual Studio Code with a specific project.

This function returns a callable that opens VSCode, waits for initialization,
then automatically opens the integrated terminal. You can deactivate the terminal toggle
shortcut if you do not want it.

**Args:**
    project_path (str): Absolute path to the project directory to open

**Returns:**
    callable: A function that launches and configures VSCode when called

Workflow:
    1. Launch VSCode with the specified project directory
    2. Wait 2 seconds for VSCode to fully load and initialize
    3. Send Ctrl+` hotkey to open the integrated terminal

VSCode Integration:
    Each project should have a .vscode/settings.json file to configure:

    - Terminal working directory
    - Environment variables
    - Python interpreter path
    - Extensions and settings specific to that project

Timing:
    The 2-second delay is necessary because VSCode needs time to initialize
    before accepting hotkeys. This delay works well for most hardware and
    project sizes.

**Note:**
    Uses lambda for inline definition. For complex workflows, a dedicated
    function would be more maintainable.

## type_text

```python
def type_text():
```

Create a function that types the specified text using ydotool.

This function returns a callable that simulates typing the given text into
the currently focused application using ydotool for low-level input events.

**Args:**
    text (str): The text to type when the returned function is called

**Returns:**
    callable: A function that executes the text typing when called

Technical Details:
    - Uses "--" argument to prevent ydotool flag interpretation
    - Works on both X11 and Wayland (unlike xdotool which is X11-only)
    - Non-blocking execution doesn't freeze the UI
    - Each character sent as separate input event

Performance:
    Character-by-character input is slower for long text. For large text
    blocks, consider using clipboard operations instead.

Design Pattern:
    Factory function pattern - returns a function rather than executing
    immediately. This allows configuration during layout building and
    execution when keys are pressed.

**Raises:**
    RuntimeError: If actions module not initialized

## type_keyring

```python
def type_keyring():
```

Type the configured password followed by Enter key.

This function types the password stored in the KEYRING_PW configuration
variable, followed by a newline character to submit forms or authenticate.

**Returns:**
    callable: Function that types the password when called

Security **Note:**
    The password is stored in environment variables via config.env.
    While more secure than hardcoding, consider using proper password
    managers for production systems.

**Raises:**
    RuntimeError: If KEYRING_PW not configured in initialization

## type_snippet

```python
def type_snippet():
```

Create a function that inserts a code snippet from a text file.

This function loads a code snippet from the snippets directory and types it
into the currently focused application. Snippets are stored as .txt files
and can contain boilerplate code, templates, commonly used commands, etc.

**Args:**
    snippet_name (str): Name of the snippet file (without .txt extension)

**Returns:**
    callable: A function that loads and types the snippet when called

USAGE EXAMPLES:
- type_snippet("python_boilerplate") -> loads python_boilerplate.txt
- type_snippet("html_template") -> loads html_template.txt
- type_snippet("git_commit_msg") -> loads git_commit_msg.txt

ERROR HANDLING:
- Gracefully handles missing snippet files with user feedback
- Validates module initialization before attempting file operations

PERFORMANCE OPTIMIZATION OPPORTUNITIES:
- Could cache frequently used snippets in memory
- Could preload all snippets at startup
- Could use async I/O for large snippets
However, snippets are typically small and accessed infrequently,
so the current simple approach is adequate.

## open_obsidian

```python
def open_obsidian():
```

Create a function that opens Obsidian with a specific vault.

This function implements smart window management - it first checks if Obsidian
is already open with the target vault, and if so, brings it to focus instead
of opening a new instance. This prevents window clutter and improves UX.

**Args:**
    vault_path (str): Path to the Obsidian vault directory

**Returns:**
    callable: A function that opens/focuses Obsidian vault when called

OBSIDIAN INTEGRATION:
- Uses Obsidian's URI scheme (obsidian://open?vault=name) for launching
- Supports Obsidian's native vault naming and organization
- Works with both local and synced vaults

WINDOW MANAGEMENT STRATEGY:
1. Check if Obsidian is already running with target vault
2. If found, activate the existing window (bring to front)
3. If not found, launch new Obsidian instance with URI scheme

This prevents multiple windows for the same vault and provides seamless UX.

## execute_bash

```python
def execute_bash():
```

Arguments are optional
in_terminal=True when scripts need to be run in terminal for interactivity

## terminal_env_jarvis

```python
def terminal_env_jarvis():
```

Open a terminal with jarvis/busybee conda environment activated.

This function launches a terminal window with a pre-configured conda environment
that's set up for jarvis development work. The environment includes all necessary
dependencies for StreamDeck development, Python automation, and related tools.

Script Execution:
    Executes "open_jarvisbusybee_env_T.sh" which handles:

    - Opening a new terminal window
    - Activating the appropriate conda environment
    - Setting working directory to jarvis project
    - Loading any necessary environment variables

Design Pattern:
    Script delegation - complex terminal setup is handled by external bash
    scripts rather than Python code because bash is better suited for terminal
    and environment manipulation, and scripts can be easily modified without
    changing Python code.

**Note:**
    The script file must exist in the configured BASHSCRIPTS_DIR.

## terminal_env_busybee

```python
def terminal_env_busybee():
```

Open a terminal with busybee conda environment activated.

Similar to terminal_env_jarvis() but specifically for the busybee project
environment. Executes the "open_busybee_env_T.sh" script.

**Note:**
    See terminal_env_jarvis() for detailed workflow explanation.

## defaultbranch_commit

```python
def defaultbranch_commit():
```

Executes a git commit workflow using a bash script with interactivity.
in_terminal=False, because the script handles its own terminal.
Takes 'PROJECTS_DIR' as an argument
Prompts user for project name, then navigates to PROJECTS_DIR/PROJECT_NAME
and runs git status, git add ., and git commit with user prompts between each step.
User can exit at any point using CTRL+C. To continue the workflow, user can simply click ENTER in the terminal
to proceed to the next step,  or to close the terminal when done. I have the git config to open the
commit message in vscode, as I prefer that over nano or vim. I have the lines showing me where the
commit title and description can extend to, so this is nice.

## nautilus_path

```python
def nautilus_path():
```

I want this function to open file manager windows or raise them if there is
already one open with my target directory. Instead of always opening a new Nautilus window,
I will first check if there is already one open with my target directory.
If there is, I will just bring it to the front (raise it).
This prevents window clutter and gives me a better user experience. :)

## wrapper

```python
def wrapper():
```

## execute

```python
def execute():
```

## wrapper

```python
def wrapper():
```

## wrapper

```python
def wrapper():
```

## wrapper

```python
def wrapper():
```

## wrapper

```python
def wrapper():
```

## Production Code Comments

Essential comments that remain in the production codebase:

- **Line 80:** Required placeholders for dynamic initialization system

## Additional Code Context

Other contextual comments from the codebase:

- **Line 68:** Standard library imports for system interaction
- **Line 69:** Execute external commands like ydotool, wmctrl, applications
- **Line 70:** Time delays for application startup coordination
- **Line 71:** File system operations and path manipulation
- **Line 72:** Object-oriented filesystem paths
- **Line 75:** Import from our UI module for dynamic key rendering
- **Line 76:** Note: render_keys import moved inside toggle_mic function to avoid circular import
- **Line 77:** This was: actions -> ui.render -> core.logic -> actions
- **Line 78:** Now render_keys is imported only when needed, breaking the cycle
- **Line 93:** Path to ydotool executable for keyboard/mouse input simulation
- **Line 94:** Set by init_module() to system ydotool path or custom config path
- **Line 96:** Directory paths for various asset types
- **Line 97:** Set by init_module() to directory containing code snippet text files
- **Line 98:** Set by init_module() to directory containing executable bash scripts
- ... and 445 more contextual comments
