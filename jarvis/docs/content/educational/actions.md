---
title: "Educational Content: Actions"
tags: [edu, auto-generated]
description: "Educational Content from actions.py"
date: 2025-10-03
---

# Educational Content: Actions

**Source File**: `jarvis/actions/actions.py`

**Category**: Computer science concepts, design patterns, and learning material

---

<a id="general-1"></a>

## Module Functionality Overview

1. Opening of **URLs** in default browser. In my case, Google Chrome. Functions here are:

- url_freecodecamp

- url_youtube

- url_github

- url_gemini

- url_claude

- url_chatgpt

2. Open **Spotify** or trigger play/pause in the app

3. **Microphone ON/OFF toggle** with is_mic_muted, toggle_mic

4. Trigger **hotkeys/shortcuts**: hot_keys (example usage in hk_terminal and copy)

5. Open **VSCode** with a given project path: open_vscode

- I like to control the vscode appearance for each project. I assign different color settings for the title and status bars so that I have a visual cue of which project I am working on on which window, when I have multiple vscode windows open, and I use ALT + TAB to switch between applications.

6. Type text and text blocks or snippets:

   - type_text, type_snippet

   - type_keyring: Type and enter passwords. However, it is recommended to leave this function unused. I need to find a way to encrypt passwords. I leave this here as a placeholder for a future implementation, as I do not know at the moment how to do it securely. Therefore, in the config.env file it is recommended to leave the KEYRING_PW variable empty.

7. Open **Obsidian** with a given vault path. It supports the possibility to open multiple vaults, so you can reuse the function in different keys for different vaults with open_obsidian. However, it is needed to specify the codename, and the path to the vault needs to be in the config.env file.

8. **Execute bash** scripts: execute_bash

- Example of usage in terminal_env_jarvis and terminal_env_busybee for basic scripts

- Example of advanced usage with git_commit_workflow.sh

9. Open nautilus windows with a target path. If that path is already open in another window, simply raise it, to avoid multiple nautilus windows with the same path (which happens often if this check is not in place before opening the window). This was the trigger to change to X11 from Wayland, as Wayland does not support window management in a straightforward way as X11 does, and it was giving me too many headaches. I do not discard in the future to ==TRY== to implement jarvis in wayland.

*[Source: actions.py:7]*

---

<a id="general-2"></a>

## Configuration Flow Architecture

How environment variables in config.env reach this module:

config.env is generated with setup_config.py script (to be executed in the jarvis directory).

1. systemd jarvis.service loads config.env via 'EnvironmentFile'.

2. jarvis.service starts main.sh: this script activates the venv and runs python -m jarvis

3. \_\_main\_\_.py delegates to core.application which reads environment variables using os.getenv()

4. core.application calls config.initialization.init_jarvis() with all configuration

5. init_jarvis() uses the general init_module() function to set global variables in this module

6. This module stores them in global variables for use by action functions

### Configuration Flow

Configuration flows: config.env -> systemd -> main.sh -> python -m jarvis -> \_\_main\_\_.py -> core.application -> config.initialization -> actions.py

This uses a Global Configuration with Dynamic Initialization (DI) pattern.

### Why not read environment variables directly in this module?

We could have each action function call `os.getenv()` directly, but I chose centralized global configuration instead because:

- Keeps configuration loading centralized in core.application, so it is easier to maintain

- Makes dependencies explicit (you can see what each module needs)

- Better separation of concerns (core.application handles config, this module handles actions)

The .env file provides the configuration, not the logic itself. The logic is provided through initialization.py and core.application.py

*[Source: actions.py:40]*

---

<a id="general-3"></a>

## Global variable declarations for dynamic initialization

==IMPORTANT==: Global variable declarations are MANDATORY for the init_module() pattern to work.

The config.initialization.init_module() function uses hasattr() to check if each variable exists in this module's namespace before attempting to set its value with setattr(). Without these declarations, hasattr() returns False and initialization silently fails.

Initialization flow:

1. These variables are declared as None (creates the module attributes)

2. core.application calls init_jarvis() which internally calls init_module(actions, ...)

3. init_module() uses hasattr(actions, 'YDOTOOL_PATH') to verify attribute exists

4. init_module() uses setattr(actions, 'YDOTOOL_PATH', actual_value) to set real values

5. Action functions check if variables are still None to detect initialization failures

*[Source: actions.py:67]*

---

<a id="general-4"></a>

## Design pattern comparison: Global Configuration vs dependency injection

We are using global configuration with dynamic initialization.

Our pattern stores configuration in module-level global variables that are set at runtime. This approach provides:

1. Testability: Easy to mock configuration by setting globals for unit tests

2. Flexibility: Can be configured differently for different environments

3. Performance: Configuration accessed directly without repeated file reads or imports

4. Error handling: Can detect and report missing configuration with None checks

5. Simplicity: No complex dependency injection framework needed

### How the pattern works

1. Declare global variables as None (creates module attributes)

2. At startup, init_module() uses setattr() to set real values

3. Functions access these globals directly: if YDOTOOL_PATH is None: ...

4. Configuration is "injected" into the module, not into individual functions

### What is true dependency injection?

Dependency Injection (DI) is a design pattern where an object's dependencies are provided (injected) to it from external sources rather than the object creating or finding them itself.

==KEY PRINCIPLE==: "Don't call us, we'll call you" (Inversion of Control)

- Dependencies are PASSED IN as parameters to functions/constructors

- The function/object doesn't know HOW to create its dependencies

- An external "injector" provides the dependencies

**TRUE DEPENDENCY INJECTION EXAMPLE:**

```python

def hot_keys(ydotool_path: str, keycodes: Dict, *keys: str) -> None:

    """Dependencies are INJECTED as parameters - this is true DI"""

    sequence = []

    for key in keys:

        if key not in keycodes:  # Uses injected dependency

            raise ValueError(f"Unknown key: {key}")

        sequence.append(f"{keycodes[key]}:1")

    subprocess.run([ydotool_path, "key"] + sequence)  # Uses injected dependency

```

You would call it like: `hot_keys("/usr/bin/ydotool", KEYCODES_DICT, "CTRL", "C")`  with dependencies passed in.

**CURRENT APPROACH (Global Configuration)**

```python

def hot_keys(*keys: str) -> None:

    """Dependencies accessed from global state - NOT dependency injection"""

    if KEYCODES is None or YDOTOOL_PATH is None:  # EDU: Accesses global variables

        raise RuntimeError("Module not initialized")

    sequence = []

    for key in keys:

        if key not in KEYCODES:  # EDU: Uses global variable

            raise ValueError(f"Unknown key: {key}")

        sequence.append(f"{KEYCODES[key]}:1")

    subprocess.run([YDOTOOL_PATH, "key"] + sequence)  # EDU: Uses global variable

You call it like: `hot_keys("CTRL", "C")`  No dependencies passed, function finds them globally.

```

### Key differences

1. WHERE DEPENDENCIES COME FROM:

   - TRUE DI: Dependencies passed as function parameters

   - OUR APPROACH: Dependencies accessed from module-level globals

2. FUNCTION SIGNATURES:

   - TRUE DI: Functions declare what they need as parameters

   - OUR APPROACH: Functions have simpler signatures, find dependencies internally

3. CALLER RESPONSIBILITY:

   - TRUE DI: Caller must provide all dependencies when calling function

   - OUR APPROACH: Caller just calls function, dependencies already available globally

4. COUPLING:

   - TRUE DI: Functions are decoupled from specific dependency sources

   - OUR APPROACH: Functions are coupled to specific global variable names

5. TESTING:

   - TRUE DI: Pass mock objects as parameters: hot_keys(mock_path, mock_codes, "A")

   - OUR APPROACH: Set global variables before test: YDOTOOL_PATH = mock_path

WHY WE CHOSE OUR APPROACH INSTEAD OF TRUE DEPENDENCY INJECTION:

1. STREAMDECK CONSTRAINT: StreamDeck library calls our functions with fixed signatures

   - StreamDeck expects: key_pressed(deck, key_number)

   - Can't change to: key_pressed(deck, key_number, ydotool_path, keycodes, ...)

2. SIMPLICITY: Fewer parameters to pass around in every function call

   - Our way: hot_keys("CTRL", "C")

   - DI way: hot_keys(ydotool_path, keycodes, "CTRL", "C")

3. PERFORMANCE: No need to pass the same config objects repeatedly

   - Configuration set once at startup, accessed directly when needed

4. STREAMDECK INTEGRATION: Hardware callbacks can't receive arbitrary parameters

   - Hardware events trigger callbacks with predetermined signatures

   - Global state allows callbacks to access needed configuration

ALTERNATIVE PATTERNS WE COULD HAVE USED:

========================================

1. SERVICE LOCATOR: Functions call a service to get dependencies

   config = ConfigService.get_config(); config.ydotool_path

2. SINGLETON: Global configuration object

   Config.instance().ydotool_path

3. CLOSURE WITH DEPENDENCY INJECTION: Factory functions that capture dependencies

   def create_hotkey_function(ydotool_path, keycodes):

       def hot_keys(*keys): # Uses captured dependencies

       return hot_keys

*[Source: actions.py:87]*

---

<a id="general-5"></a>

=====================================================================================

WRAPPER FUNCTION PATTERNS: return wrapper vs return wrapper()

=====================================================================================

This module uses two different wrapper patterns depending on how functions are called

from the layouts.py file. Understanding this pattern is crucial for maintaining the

StreamDeck key action system.

PATTERN 1: Functions with Arguments → return wrapper

====================================================

Functions that need arguments use the Factory Pattern:

Definition in actions.py:

  def toggle_mic(deck, key):

      def wrapper():

          # ... do the actual work ...

      return wrapper  # Return function reference, don't call it

Usage in layouts.py:

  "action": actions.toggle_mic(deck, 31)  # Called WITH parentheses

What happens:

  1. Layout creation: toggle_mic(deck, 31) is called → returns wrapper function

  2. Key press: StreamDeck calls the stored wrapper function → actual work happens

Examples: toggle_mic(deck, key), type_text(text), open_obsidian(vault_path)

PATTERN 2: Functions without Arguments → return wrapper()

=========================================================

Functions that need no arguments use Direct Execution Pattern:

Definition in actions.py:

  def terminal_env_jarvis():

      def wrapper():

          # ... do the actual work ...

      return wrapper()  # Call function immediately and return result

Usage in layouts.py:

  "action": actions.terminal_env_jarvis  # Referenced WITHOUT parentheses

What happens:

  1. Layout creation: terminal_env_jarvis is stored as function reference

  2. Key press: StreamDeck calls terminal_env_jarvis() → wrapper() executes immediately

Examples: terminal_env_jarvis, terminal_env_busybee, defaultbranch_commit

WHY TWO DIFFERENT PATTERNS?

============================

The pattern depends on whether the function needs arguments:

1. Functions WITH arguments:

   - Must be called during layout creation to pass arguments

   - Return wrapper function for later execution

   - Use: "action": actions.function_name(arg1, arg2)

2. Functions WITHOUT arguments:

   - Can be referenced directly in layout

   - Execute immediately when called by StreamDeck

   - Use: "action": actions.function_name

COMMON MISTAKE:

===============

Using return wrapper() for functions with arguments will cause them to execute

during layout creation instead of when the key is pressed, breaking the intended

behavior and causing the layout to store None instead of a callable function.

EXAMPLE COMPARISON:

===================

CORRECT (with arguments):

  def toggle_mic(deck, key):

      def wrapper():

          render_keys(deck, key, ...)

      return wrapper  # ✓ Correct: returns function for later execution

INCORRECT (with arguments):

  def toggle_mic(deck, key):

      def wrapper():

          render_keys(deck, key, ...)

      return wrapper()  # ✗ Wrong: executes immediately, returns None

This documentation explains the wrapper pattern inconsistencies that were

causing the microphone toggle functionality to fail.

*[Source: actions.py:200]*

---

<a id="general-6"></a>

DESIGN PATTERN: Module-level Configuration with General Initialization

=======================================================================

This module now uses the general init_module() function from config.initialization

instead of having its own initialization function. This reduces code duplication

and provides a consistent initialization pattern across all jarvis modules.

WHAT ARE GLOBAL VARIABLES? (For Beginners)

==========================================

Global variables are variables that can be accessed from anywhere in the module.

They exist at the "module level" - outside of any function or class.

WHY USE GLOBAL VARIABLES HERE?

==============================

The StreamDeck library calls our action functions directly when keys are pressed.

We can't change the function signatures (parameters) that StreamDeck expects.

So we need a way for all action functions to access the configuration.

EXAMPLE: When you press key 5, StreamDeck calls toggle_mic() with no parameters.

But toggle_mic() needs YDOTOOL_PATH and KEYCODES to work. Global variables

let us store these values once and access them from any function.

INITIALIZATION:

The config.initialization.init_module() function sets these global variables

by calling setattr(module, key, value) for each configuration parameter.

*[Source: actions.py:283]*

---

<a id="general-7"></a>

URL Functions - Browser Integration

======================================

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

   BROWSER COMPATIBILITY:

   xdg-open works with all major browsers:

   - Chrome/Chromium: google-chrome

   - Firefox: firefox

   - Edge: microsoft-edge

   - Safari: (not available on Linux)

   - Brave: brave-browser

   - Opera: opera

   SECURITY CONSIDERATIONS:

   - URL is hardcoded and safe (no user input injection)

   - xdg-open is a trusted system utility

   - No browser automation or remote control involved

   - Browser handles HTTPS validation and security

*[Source: actions.py:308]*

---

<a id="general-8"></a>

SPOTIFY LAUNCH ALTERNATIVES:

- Flatpak: flatpak run com.spotify.Client

- Snap: snap run spotify

- Web player: xdg-open https://open.spotify.com

Using simple "spotify" command works with most installation methods

as they typically create a symlink in PATH

*[Source: actions.py:435]*

---

<a id="general-9"></a>

ERROR HANDLING CONSIDERATIONS:

- pgrep might fail if procfs is not available

- playerctl might fail if no MPRIS session exists

- spotify command might fail if not in PATH

Current implementation gracefully handles these by allowing subprocess errors

*[Source: actions.py:448]*

---

<a id="general-10"></a>

## Circular import to avoid

I was importing render_keys from ui.render at the top of the file, but this was causing a circular import issue.

render_keys import moved inside toggle_mic function to avoid circular import

This breaks the cycle: actions -> ui.render -> core.logic -> actions

*[Source: actions.py:454]*

---

## function: defaultbranch_commit

<a id="function:-defaultbranch_commit-1"></a>

Executes a git commit workflow using a bash script with interactivity.

in_terminal=False, because the script handles its own terminal.

Takes 'PROJECTS_DIR' as an argument

Prompts user for project name, then navigates to PROJECTS_DIR/PROJECT_NAME

and runs git status, git add ., and git commit with user prompts between each step.

User can exit at any point using CTRL+C. To continue the workflow, user can simply click ENTER in the terminal

to proceed to the next step, or to close the terminal when done. I have the git config to open the

commit message in vscode, as I prefer that over nano or vim. I have the lines showing me where the

commit title and description can extend to, so this is nice.

*[Source: actions.py:982]*

---

## function: hk_copy

<a id="function:-hk_copy-1"></a>

Simple demonstration of the hot_keys function that sends the standard

copy-to-clipboard keyboard shortcut. This is a basic example of hotkey usage.

*[Source: actions.py:607]*

---

## function: hk_terminal

<a id="function:-hk_terminal-1"></a>

This function simulates the Ctrl+Alt+T keyboard shortcut which is the

standard way to open a terminal window across most Linux desktop environments.

This approach respects the user's default terminal preference and integrates

properly with the desktop environment's window management.

Desktop Environment Compatibility:

- GNOME: Opens gnome-terminal

- KDE: Opens konsole

- XFCE: Opens xfce4-terminal

- i3/sway: Opens configured terminal ($TERMINAL)

- Others: Opens system default terminal

Advantages:

- Respects user's default terminal preference

- Works consistently across different desktop environments

- Faster than discovering and launching specific terminal executable

- Integrates with desktop environment's window management

*[Source: actions.py:575]*

---

<a id="function:-hk_terminal-2"></a>

Send the standard Linux terminal hotkey combination

This is recognized by virtually all Linux desktop environments

*[Source: actions.py:597]*

---

## function: hot_keys

<a id="function:-hot_keys-1"></a>

This function presses multiple keys simultaneously (like Ctrl+C, Alt+Tab, etc.)

and releases them in the correct order to avoid "sticky key" issues.

Technical Details:

- Keys are pressed in the order specified (left to right)

- Keys are released in reverse order (right to left) to prevent sticky keys

- Each key event is formatted as "keycode:state" (1=press, 0=release)

- All events are sent in a single ydotool command for atomic execution

*[Source: actions.py:531]*

---

<a id="function:-hot_keys-2"></a>

Look up the Linux input event code for this key name

*[Source: actions.py:547]*

---

<a id="function:-hot_keys-3"></a>

Format as "keycode:1" for key press event

*[Source: actions.py:550]*

---

<a id="function:-hot_keys-4"></a>

Format as "keycode:0" for key release event

*[Source: actions.py:555]*

---

<a id="function:-hot_keys-5"></a>

Give ydotool daemon time to wake up from idle state

First command after idle needs a moment to initialize properly

*[Source: actions.py:559]*

---

## function: is_mic_muted

<a id="function:-is_mic_muted-1"></a>

This function uses the ALSA amixer command to query the current state

of the Capture (microphone) audio device.

Requires amixer to be installed and the Capture device to be available.

This is the standard microphone control on most Linux systems.

*[Source: actions.py:468]*

---

## function: nautilus_path

<a id="function:-nautilus_path-1"></a>

Window Management Strategy (same as open_obsidian):

1. Check if Nautilus already has directory open

2. If found, activate window

3. If not, launch new Nautilus instance

Prevents multiple windows for same directory

Path Resolution:

- Resolves relative paths to absolute for consistent matching

- Resolves symbolic links to actual paths

- Ensures same format when checking window titles

wmctrl Details:

- "-lx" flags: -l (list windows), -x (include WM_CLASS)

- Output format: window_id desktop_num WM_CLASS hostname window_title

- WM_CLASS "org.gnome.Nautilus" identifies Nautilus windows

- "-i -a window_id" activates window by ID

*[Source: actions.py:1008]*

---

## function: open_obsidian

<a id="function:-open_obsidian-1"></a>

Window Management Strategy:

1. Check if Obsidian already has vault open (wmctrl)

2. If found, activate existing window

3. If not found, launch via URI scheme

This prevents window clutter and improves UX

*[Source: actions.py:828]*

---

<a id="function:-open_obsidian-2"></a>

Alternative Launch Methods:

- Direct: obsidian --vault /path/to/vault

- Flatpak: flatpak run md.obsidian.Obsidian --vault /path/to/vault

- AppImage: ./Obsidian.AppImage --vault /path/to/vault

URI scheme works regardless of installation method

*[Source: actions.py:836]*

---

<a id="function:-open_obsidian-3"></a>

This function implements smart window management - it first checks if Obsidian

is already open with the target vault, and if so, brings it to focus instead

of opening a new instance. This prevents window clutter and improves UX.

OBSIDIAN INTEGRATION:

- Uses Obsidian's URI scheme (obsidian://open?vault=name) for launching

- Supports Obsidian's native vault naming and organization

- Works with both local and synced vaults

*[Source: actions.py:842]*

---

<a id="function:-open_obsidian-4"></a>

Extract vault name from the full path for window matching and URI construction

Path.resolve() normalizes the path and .name gets the final component

*[Source: actions.py:851]*

---

## function: open_vscode

<a id="function:-open_vscode-1"></a>

Alternative approaches:

- Use VSCode's --command flag: code --command workbench.action.terminal.new

- Use VSCode's remote development features for containerized projects

- Integrate with VSCode's workspace API for session management

*[Source: actions.py:627]*

---

<a id="function:-open_vscode-2"></a>

This function returns a callable that opens VSCode, waits for initialization,

then automatically opens the integrated terminal. You can deactivate the terminal toggle

shortcut if you do not want it.

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

*[Source: actions.py:632]*

---

## function: spotify

<a id="function:-spotify-1"></a>

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

*[Source: actions.py:391]*

---

<a id="function:-spotify-2"></a>

Check if Spotify process is currently running

pgrep flags: -x (exact match), searches for process name "spotify"

capture_output=True prevents command output from appearing in terminal

*[Source: actions.py:412]*

---

<a id="function:-spotify-3"></a>

Check return code: 0 = found process, non-zero = process not found

*[Source: actions.py:417]*

---

<a id="function:-spotify-4"></a>

Spotify is running - toggle play/pause state

playerctl flags: --player=spotify (target specific player), play-pause (toggle command)

*[Source: actions.py:419]*

---

<a id="function:-spotify-5"></a>

ALTERNATIVE PLAYERCTL COMMANDS:

- "play" - force play state

- "pause" - force pause state

- "next" - skip to next track

- "previous" - go to previous track

- "stop" - stop playback

*[Source: actions.py:423]*

---

<a id="function:-spotify-6"></a>

Spotify not running - launch the application

This will start Spotify in the background

*[Source: actions.py:431]*

---

## function: terminal_env_busybee

<a id="function:-terminal_env_busybee-1"></a>

Similar to terminal_env_jarvis() but specifically for the busybee project

environment. See terminal_env_jarvis() for detailed workflow explanation.

*[Source: actions.py:971]*

---

## function: terminal_env_jarvis

<a id="function:-terminal_env_jarvis-1"></a>

Script Delegation Pattern:

Complex terminal setup handled by bash scripts rather than Python

because bash is better suited for terminal/environment manipulation

and scripts can be modified without changing Python code

This function launches a terminal window with a pre-configured conda environment

that's set up for jarvis development work. The environment includes all necessary

dependencies for StreamDeck development, Python automation, and related tools.

Script Execution:

Executes "open_jarvisbusybee_env_T.sh" which handles:

- Opening a new terminal window

- Activating the appropriate conda environment

- Setting working directory to jarvis project

- Loading any necessary environment variables

*[Source: actions.py:948]*

---

## function: toggle_mic

<a id="function:-toggle_mic-1"></a>

This function implements a factory pattern that returns a callable which,

when executed, will toggle the microphone mute state and immediately update

the corresponding StreamDeck key with appropriate visual feedback.

Visual Feedback:

- Muted: Shows "OFF" label with "mic-off.png" icon

- Active: Shows "ON" label with "mic-on.png" icon

Uses amixer to control the Capture device. Requires ALSA to be configured.

*[Source: actions.py:493]*

---

## function: type_snippet

<a id="function:-type_snippet-1"></a>

Design Decision - File-based storage vs Database:

We use text files because:

1. SIMPLICITY: Easy to edit snippets with any text editor

2. VERSION CONTROL: Can track snippet changes in git

3. PORTABILITY: No database setup required

4. TRANSPARENCY: Users can see exactly what will be typed

USAGE EXAMPLES:

- type_snippet("python_boilerplate") -> loads python_boilerplate.txt

- type_snippet("html_template") -> loads html_template.txt

- type_snippet("git_commit_msg") -> loads git_commit_msg.txt

This function loads a code snippet from the snippets directory and types it

into the currently focused application. Snippets are stored as .txt files

and can contain boilerplate code, templates, commonly used commands, etc.

ERROR HANDLING:

- Gracefully handles missing snippet files with user feedback

- Validates module initialization before attempting file operations

PERFORMANCE OPTIMIZATION OPPORTUNITIES:

- Could cache frequently used snippets in memory

- Could preload all snippets at startup

- Could use async I/O for large snippets

However, snippets are typically small and accessed infrequently,

so the current simple approach is adequate.

*[Source: actions.py:761]*

---

## function: type_text

<a id="function:-type_text-1"></a>

This function returns a callable that simulates typing the given text into

the currently focused application using ydotool for low-level input events.

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

*[Source: actions.py:686]*

---

<a id="function:-type_text-2"></a>

ALTERNATIVE TOOLS CONSIDERED:

- xdotool: More mature but X11-only, doesn't work on Wayland, and since this project was started

on Wayland, ydotool was the better choice. When shifting to X11, I kept ydotool as it seems to work

fine on X11 too. No need to change it for now, unless I face limitations or issues in the future.

- PyAutoGUI: Not tested yet, but I keep it in mind for future exploration.

*[Source: actions.py:717]*

---

## function: url_freecodecamp

<a id="function:-url_freecodecamp-1"></a>

Quick access to freeCodeCamp learning platform for coding tutorials,

challenges, and educational content.

EDUCATIONAL WORKFLOW:

Having quick access to learning platforms supports continuous learning

and skill development during coding sessions.

*[Source: actions.py:349]*

---

## function: url_github

<a id="function:-url_github-1"></a>

This function opens the GitHub profile page using the system's default web browser.

It uses xdg-open which is the standard Linux way to open URLs and files with

their associated default applications.

xdg-open is the freedesktop.org standard for opening files/URLs

*[Source: actions.py:367]*

---

## function: url_youtube

<a id="function:-url_youtube-1"></a>

Simple utility function to quickly access YouTube using the system's

default web browser via xdg-open standard.

DESIGN CONSISTENCY:

Follows same pattern as other web-opening functions for consistency

and predictable behavior across all web-based StreamDeck actions.

*[Source: actions.py:358]*

---

## function: wrapper

<a id="function:-wrapper-1"></a>

Launch VSCode with the project path as argument

VSCode will open the directory and load workspace settings

*[Source: actions.py:654]*

---

<a id="function:-wrapper-2"></a>

Wait for VSCode to fully initialize before sending hotkeys

This prevents the terminal hotkey from being ignored

*[Source: actions.py:659]*

---

<a id="function:-wrapper-3"></a>

Open VSCode integrated terminal using Ctrl+` (grave/backtick)

This provides immediate access to command line in project context

*[Source: actions.py:663]*

---

<a id="function:-wrapper-4"></a>

Execute ydotool command to type the text

Arguments:

- YDOTOOL_PATH: Path to ydotool executable

- "type": ydotool subcommand for typing text

- "--": Indicates end of options, prevents text starting with "-" being interpreted as flags

- text: The actual text to type

*[Source: actions.py:709]*

---

<a id="function:-wrapper-5"></a>

Read snippet content from file

Using context manager (with statement) ensures file is properly closed

*[Source: actions.py:798]*

---

<a id="function:-wrapper-6"></a>

Type the snippet content using ydotool

Same approach as type_text() function

*[Source: actions.py:807]*

---

<a id="function:-wrapper-7"></a>

STEP 1: Check if Obsidian is already open with this vault

*[Source: actions.py:856]*

---

<a id="function:-wrapper-8"></a>

Use wmctrl to list all open windows with their titles

wmctrl -l output format: window_id desktop_num client_machine window_title

*[Source: actions.py:858]*

---

<a id="function:-wrapper-9"></a>

Search through each window to find Obsidian with our vault

*[Source: actions.py:862]*

---

<a id="function:-wrapper-10"></a>

Look for lines containing both "Obsidian" and our vault name

This matches window titles like "Obsidian - vault_name" or "vault_name - Obsidian"

*[Source: actions.py:864]*

---

<a id="function:-wrapper-11"></a>

Extract window ID (first column in wmctrl output)

*[Source: actions.py:867]*

---

<a id="function:-wrapper-12"></a>

Activate the existing window (bring to front and focus)

wmctrl flags: -i (use window ID), -a (activate window)

*[Source: actions.py:870]*

---

<a id="function:-wrapper-13"></a>

wmctrl command failed (maybe not installed, or no X11 session)

Continue to launch new instance - this is not a critical error

*[Source: actions.py:876]*

---

<a id="function:-wrapper-14"></a>

STEP 2: No existing window found, launch new Obsidian instance

Use Obsidian's URI scheme for clean vault opening

Format: obsidian://open?vault=vault_name

*[Source: actions.py:880]*

---

<a id="function:-wrapper-15"></a>

Use xdg-open to handle the URI scheme

xdg-open is the standard Linux way to open files/URIs with default applications

*[Source: actions.py:885]*

---

<a id="function:-wrapper-16"></a>

pathlib.Path provides cross-platform path construction

*[Source: actions.py:910]*

---

<a id="function:-wrapper-17"></a>

The bash script should be executable (chmod u+x)

*[Source: actions.py:919]*

---

<a id="function:-wrapper-18"></a>

Build command for terminal execution

*[Source: actions.py:926]*

---

<a id="function:-wrapper-19"></a>

I need to convert the target directory to an absolute path because:

1. Relative paths like "../folder" or "./folder" can be ambiguous

2. Path.resolve() converts these to full paths like "/home/user/folder"

3. This ensures I am comparing the same format when checking window titles later

4. It also resolves any symbolic links to their actual paths

   (Symbolic links are like shortcuts - they point to another file/directory.

    Path.resolve() follows the shortcut to get the real location)

*[Source: actions.py:1027]*

---

<a id="function:-wrapper-20"></a>

STEP 1: Check if Nautilus is already open with my target directory

wmctrl is a command-line tool that lets me interact with X11 windows in Linux

The "-lx" flags mean:

-l: list all windows

-x: include the WM_CLASS property (this helps me identify the application type)

subprocess.check_output() runs this command and captures its text output

text=True ensures I get a string back instead of bytes

*[Source: actions.py:1036]*

---

<a id="function:-wrapper-21"></a>

The wmctrl output looks like this (one line per window):

0x02400003  0 org.gnome.Nautilus.org.gnome.Nautilus desktop file-browser - /home/user/Documents

0x02600004  0 firefox.Firefox          desktop Firefox

Each line contains: window_id, desktop_number, WM_CLASS, hostname, window_title

I need to parse each line to extract the information I need

*[Source: actions.py:1048]*

---

<a id="function:-wrapper-22"></a>

I only care about Nautilus windows, so I check if "org.gnome.Nautilus"

is in the line. This is the WM_CLASS identifier for Nautilus windows.

*[Source: actions.py:1055]*

---

<a id="function:-wrapper-23"></a>

Now I need to extract the window ID and title from this line

line.split() breaks the line into parts separated by whitespace

The window ID is always the first part (index 0)

Example: "0x02400003" from the line above

*[Source: actions.py:1059]*

---

<a id="function:-wrapper-24"></a>

The window title starts from the 4th element (index 3) onwards

I use " ".join() to put the title back together with spaces

because the title might contain spaces that were split apart

Example: from "desktop file-browser - /home/user/Documents"

I want "file-browser - /home/user/Documents"

*[Source: actions.py:1065]*

---

<a id="function:-wrapper-25"></a>

Now I need to check if this Nautilus window is showing my target directory

There are different ways the directory might appear in the window title:

First, I get just the folder name (last part of the path)

Path(path).name returns "Documents" from "/home/user/Documents"

This helps me match windows that might not show the full path

*[Source: actions.py:1072]*

---

<a id="function:-wrapper-26"></a>

I check three conditions to see if this window matches my target:

*[Source: actions.py:1081]*

---

<a id="function:-wrapper-27"></a>

I found a matching window! Instead of opening a new one,

I will bring this existing window to the front (raise it)

wmctrl can also control windows, not just list them

-i: "use window ID" - I am giving it a window ID number (0x02400003)

instead of a window title/name (more reliable than titles)

-a: "activate window" - bring the window to front and give it focus

(like clicking on it in the taskbar)

window_id: the window ID I extracted earlier (like 0x02400003)

*[Source: actions.py:1086]*

---

<a id="function:-wrapper-28"></a>

wmctrl command failed (maybe not installed, or no X11 session)

Continue to launch new instance - this is not a critical error

*[Source: actions.py:1099]*

---

<a id="function:-wrapper-29"></a>

STEP 2: If I get here, it means I did not find any existing Nautilus window

with my target directory, so I need to open a new one

subprocess.Popen() starts a new process without waiting for it to finish

This is perfect for GUI applications because:

1. I don't want my Python script to hang waiting for Nautilus to close

2. The user should be able to use Nautilus independently

3. My script can continue with other tasks

I pass the target directory as an argument to nautilus so it opens there

*[Source: actions.py:1103]*

---
