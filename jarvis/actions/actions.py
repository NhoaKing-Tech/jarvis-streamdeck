"""StreamDeck action functions for jarvis assistant.

Bridges StreamDeck key events to system operations/actions.
Configuration initialized via config.initialization.init_module().
"""

# EDU: ## Module Functionality Overview
# EDU: 
# EDU: 1. Opening of **URLs** in default browser. In my case, Google Chrome. Functions here are:
# EDU: - url_freecodecamp
# EDU: - url_youtube
# EDU: - url_github
# EDU: - url_gemini
# EDU: - url_claude
# EDU: - url_chatgpt
# EDU: 2. Open **Spotify** or trigger play/pause in the app
# EDU: 3. **Microphone ON/OFF toggle** with is_mic_muted, toggle_mic
# EDU: 4. Trigger **hotkeys/shortcuts**: hot_keys (example usage in hk_terminal and copy)
# EDU: 5. Open **VSCode** with a given project path: open_vscode
# EDU: - I like to control the vscode appearance for each project. I assign different color settings for the title and status bars so that I have a visual cue of which project I am working on on which window, when I have multiple vscode windows open, and I use ALT + TAB to switch between applications.
# EDU: 6. Type text and text blocks or snippets:
# EDU:    - type_text, type_snippet
# EDU:    - type_keyring: Type and enter passwords. However, it is recommended to leave this function unused. I need to find a way to encrypt passwords. I leave this here as a placeholder for a future implementation, as I do not know at the moment how to do it securely. Therefore, in the config.env file it is recommended to leave the KEYRING_PW variable empty.
# EDU: 7. Open **Obsidian** with a given vault path. It supports the possibility to open multiple vaults, so you can reuse the function in different keys for different vaults with open_obsidian. However, it is needed to specify the codename, and the path to the vault needs to be in the config.env file.
# EDU: 8. **Execute bash** scripts: execute_bash
# EDU: - Example of usage in terminal_env_jarvis and terminal_env_busybee for basic scripts
# EDU: - Example of advanced usage with git_commit_workflow.sh
# EDU: 9. Open nautilus windows with a target path. If that path is already open in another window, simply raise it, to avoid multiple nautilus windows with the same path (which happens often if this check is not in place before opening the window). This was the trigger to change to X11 from Wayland, as Wayland does not support window management in a straightforward way as X11 does, and it was giving me too many headaches. I do not discard in the future to ==TRY== to implement jarvis in wayland.

# TODO: Generalize nautilus_path function to work with other applications too (for obsidian is already done)
# TODO: Handle positioning and sizing of windows, at the moment everything opens correctly but super randomly placed and sized.

# Standard library imports for system interaction
import subprocess  # Execute external commands like ydotool, wmctrl, applications
import time        # Time delays for application startup coordination
import os          # File system operations and path manipulation
from pathlib import Path  # Object-oriented filesystem paths
from typing import Dict, Optional, Callable, Any

# EDU: ## Configuration Flow Architecture
# EDU: 
# EDU: How environment variables in config.env reach this module:
# EDU:  
# EDU: config.env is generated with setup_config.py script (to be executed in the jarvis directory).
# EDU: 1. systemd jarvis.service loads config.env via 'EnvironmentFile'.
# EDU: 2. jarvis.service starts main.sh: this script activates the venv and runs python -m jarvis
# EDU: 3. \_\_main\_\_.py delegates to core.application which reads environment variables using os.getenv()
# EDU: 4. core.application calls config.initialization.init_jarvis() with all configuration
# EDU: 5. init_jarvis() uses the general init_module() function to set global variables in this module
# EDU: 6. This module stores them in global variables for use by action functions
# EDU: 
# EDU: ### Configuration Flow
# EDU: Configuration flows: config.env -> systemd -> main.sh -> python -m jarvis -> \_\_main\_\_.py -> core.application -> config.initialization -> actions.py
# EDU: 
# EDU: This uses a Global Configuration with Dynamic Initialization (DI) pattern.
# EDU: 
# EDU: ### Why not read environment variables directly in this module?
# EDU: 
# EDU: We could have each action function call `os.getenv()` directly, but I chose centralized global configuration instead because:
# EDU: - Keeps configuration loading centralized in core.application, so it is easier to maintain
# EDU: - Makes dependencies explicit (you can see what each module needs)
# EDU: - Better separation of concerns (core.application handles config, this module handles actions)
# EDU: 
# EDU: The .env file provides the configuration, not the logic itself. The logic is provided through initialization.py and core.application.py
# EDU:

# EDU: ## Global variable declarations for dynamic initialization
# EDU: 
# EDU: ==IMPORTANT==: Global variable declarations are MANDATORY for the init_module() pattern to work.
# EDU: 
# EDU: The config.initialization.init_module() function uses hasattr() to check if each variable exists in this module's namespace before attempting to set its value with setattr(). Without these declarations, hasattr() returns False and initialization silently fails.
# EDU: 
# EDU: Initialization flow:
# EDU: 1. These variables are declared as None (creates the module attributes)
# EDU: 2. core.application calls init_jarvis() which internally calls init_module(actions, ...)
# EDU: 3. init_module() uses hasattr(actions, 'YDOTOOL_PATH') to verify attribute exists
# EDU: 4. init_module() uses setattr(actions, 'YDOTOOL_PATH', actual_value) to set real values
# EDU: 5. Action functions check if variables are still None to detect initialization failures

YDOTOOL_PATH: Optional[str] = None     # Path to ydotool executable for keyboard/mouse input simulation. It should be the path to custom build with uinput support in udev
SNIPPETS_DIR: Optional[Path] = None     # Directory containing code snippet text files
BASHSCRIPTS_DIR: Optional[Path] = None  # Directory containing executable bash scripts
PROJECTS_DIR: Optional[Path] = None     # User's main projects directory (usually ~/Zenith)
KEYCODES: Optional[Dict[str, int]] = None  # Mapping of key names to Linux input event codes
KEYRING_PW: Optional[str] = None       # Password for keyring/password manager access (from config.env)

# EDU: ## Design pattern comparison: Global Configuration vs dependency injection
# EDU: 
# EDU: We are using global configuration with dynamic initialization.
# EDU: 
# EDU: Our pattern stores configuration in module-level global variables that are set at runtime. This approach provides:
# EDU: 1. Testability: Easy to mock configuration by setting globals for unit tests
# EDU: 2. Flexibility: Can be configured differently for different environments
# EDU: 3. Performance: Configuration accessed directly without repeated file reads or imports
# EDU: 4. Error handling: Can detect and report missing configuration with None checks
# EDU: 5. Simplicity: No complex dependency injection framework needed
# EDU: 
# EDU: ### How the pattern works
# EDU: 1. Declare global variables as None (creates module attributes)
# EDU: 2. At startup, init_module() uses setattr() to set real values
# EDU: 3. Functions access these globals directly: if YDOTOOL_PATH is None: ...
# EDU: 4. Configuration is "injected" into the module, not into individual functions
# EDU: 
# EDU: ### What is true dependency injection?
# EDU: 
# EDU: Dependency Injection (DI) is a design pattern where an object's dependencies are provided (injected) to it from external sources rather than the object creating or finding them itself.
# EDU: 
# EDU: ==KEY PRINCIPLE==: "Don't call us, we'll call you" (Inversion of Control)
# EDU: - Dependencies are PASSED IN as parameters to functions/constructors
# EDU: - The function/object doesn't know HOW to create its dependencies
# EDU: - An external "injector" provides the dependencies
#
# EDU: **TRUE DEPENDENCY INJECTION EXAMPLE:**
# EDU: ```python
# EDU: def hot_keys(ydotool_path: str, keycodes: Dict, *keys: str) -> None:
# EDU:     """Dependencies are INJECTED as parameters - this is true DI"""
# EDU:     sequence = []
# EDU:     for key in keys:
# EDU:         if key not in keycodes:  # Uses injected dependency
# EDU:             raise ValueError(f"Unknown key: {key}")
# EDU:         sequence.append(f"{keycodes[key]}:1")
# EDU:
# EDU:     subprocess.run([ydotool_path, "key"] + sequence)  # Uses injected dependency
# EDU: ```
# EDU: You would call it like: `hot_keys("/usr/bin/ydotool", KEYCODES_DICT, "CTRL", "C")`  with dependencies passed in.
# EDU:
# EDU: CURRENT APPROACH (Global Configuration):
# EDU:
# EDU: def hot_keys(*keys: str) -> None:
# EDU:
# EDU:     """Dependencies accessed from global state - NOT dependency injection"""
# EDU:
# EDU:     if KEYCODES is None or YDOTOOL_PATH is None:  # EDU: Accesses global variables
# EDU:
# EDU:         raise RuntimeError("Module not initialized")
# EDU:
# EDU:     sequence = []
# EDU:
# EDU:     for key in keys:
# EDU:
# EDU:         if key not in KEYCODES:  # EDU: Uses global variable
# EDU:
# EDU:             raise ValueError(f"Unknown key: {key}")
# EDU:
# EDU:         sequence.append(f"{KEYCODES[key]}:1")
# EDU:
# EDU:     subprocess.run([YDOTOOL_PATH, "key"] + sequence)  # EDU: Uses global variable
# EDU:
# EDU: You call it like: `hot_keys("CTRL", "C")`  No dependencies passed, function finds them globally.
# EDU: 
# EDU: ### Key differences
# EDU: 
# EDU: 1. WHERE DEPENDENCIES COME FROM:
# EDU:    - TRUE DI: Dependencies passed as function parameters
# EDU:    - OUR APPROACH: Dependencies accessed from module-level globals
#
# EDU: 2. FUNCTION SIGNATURES:
# EDU:    - TRUE DI: Functions declare what they need as parameters
# EDU:    - OUR APPROACH: Functions have simpler signatures, find dependencies internally
#
# EDU: 3. CALLER RESPONSIBILITY:
# EDU:    - TRUE DI: Caller must provide all dependencies when calling function
# EDU:    - OUR APPROACH: Caller just calls function, dependencies already available globally
#
# EDU: 4. COUPLING:
# EDU:    - TRUE DI: Functions are decoupled from specific dependency sources
# EDU:    - OUR APPROACH: Functions are coupled to specific global variable names
#
# EDU: 5. TESTING:
# EDU:    - TRUE DI: Pass mock objects as parameters: hot_keys(mock_path, mock_codes, "A")
# EDU:    - OUR APPROACH: Set global variables before test: YDOTOOL_PATH = mock_path
#
# EDU: WHY WE CHOSE OUR APPROACH INSTEAD OF TRUE DEPENDENCY INJECTION:
# EDU: 
# EDU: 1. STREAMDECK CONSTRAINT: StreamDeck library calls our functions with fixed signatures
# EDU:    - StreamDeck expects: key_pressed(deck, key_number)
# EDU:    - Can't change to: key_pressed(deck, key_number, ydotool_path, keycodes, ...)
# EDU:
# EDU: 2. SIMPLICITY: Fewer parameters to pass around in every function call
# EDU:    - Our way: hot_keys("CTRL", "C")
# EDU:    - DI way: hot_keys(ydotool_path, keycodes, "CTRL", "C")
# EDU:
# EDU: 3. PERFORMANCE: No need to pass the same config objects repeatedly
# EDU:    - Configuration set once at startup, accessed directly when needed
# EDU:
# EDU: 4. STREAMDECK INTEGRATION: Hardware callbacks can't receive arbitrary parameters
# EDU:    - Hardware events trigger callbacks with predetermined signatures
# EDU:    - Global state allows callbacks to access needed configuration
# EDU:
# EDU: ALTERNATIVE PATTERNS WE COULD HAVE USED:
# EDU: ========================================
# EDU: 1. SERVICE LOCATOR: Functions call a service to get dependencies
# EDU:    config = ConfigService.get_config(); config.ydotool_path
# EDU:
# EDU: 2. SINGLETON: Global configuration object
# EDU:    Config.instance().ydotool_path
# EDU:
# EDU: 3. CLOSURE WITH DEPENDENCY INJECTION: Factory functions that capture dependencies
# EDU:    def create_hotkey_function(ydotool_path, keycodes):
# EDU:        def hot_keys(*keys): # Uses captured dependencies
# EDU:        return hot_keys
# EDU:
# NOTE: Global Configuration with Dynamic Initialization chosen for:
# - Simple and straightforward for this hardware integration use case
# - Balances testability with StreamDeck API constraints
# - Provides clear error handling and initialization validation

# EDU: =====================================================================================
# EDU: WRAPPER FUNCTION PATTERNS: return wrapper vs return wrapper()
# EDU: =====================================================================================
# EDU:
# EDU: This module uses two different wrapper patterns depending on how functions are called
# EDU: from the layouts.py file. Understanding this pattern is crucial for maintaining the
# EDU: StreamDeck key action system.
# EDU:
# EDU: PATTERN 1: Functions with Arguments → return wrapper
# EDU: ====================================================
# EDU: Functions that need arguments use the Factory Pattern:
# EDU:
# EDU: Definition in actions.py:
# EDU:   def toggle_mic(deck, key):
# EDU:       def wrapper():
# EDU:           # ... do the actual work ...
# EDU:       return wrapper  # Return function reference, don't call it
# EDU:
# EDU: Usage in layouts.py:
# EDU:   "action": actions.toggle_mic(deck, 31)  # Called WITH parentheses
# EDU:
# EDU: What happens:
# EDU:   1. Layout creation: toggle_mic(deck, 31) is called → returns wrapper function
# EDU:   2. Key press: StreamDeck calls the stored wrapper function → actual work happens
# EDU:
# EDU: Examples: toggle_mic(deck, key), type_text(text), open_obsidian(vault_path)
# EDU:
# EDU: PATTERN 2: Functions without Arguments → return wrapper()
# EDU: =========================================================
# EDU: Functions that need no arguments use Direct Execution Pattern:
# EDU:
# EDU: Definition in actions.py:
# EDU:   def terminal_env_jarvis():
# EDU:       def wrapper():
# EDU:           # ... do the actual work ...
# EDU:       return wrapper()  # Call function immediately and return result
# EDU:
# EDU: Usage in layouts.py:
# EDU:   "action": actions.terminal_env_jarvis  # Referenced WITHOUT parentheses
# EDU:
# EDU: What happens:
# EDU:   1. Layout creation: terminal_env_jarvis is stored as function reference
# EDU:   2. Key press: StreamDeck calls terminal_env_jarvis() → wrapper() executes immediately
# EDU:
# EDU: Examples: terminal_env_jarvis, terminal_env_busybee, defaultbranch_commit
# EDU:
# EDU: WHY TWO DIFFERENT PATTERNS?
# EDU: ============================
# EDU: The pattern depends on whether the function needs arguments:
# EDU:
# EDU: 1. Functions WITH arguments:
# EDU:    - Must be called during layout creation to pass arguments
# EDU:    - Return wrapper function for later execution
# EDU:    - Use: "action": actions.function_name(arg1, arg2)
# EDU:
# EDU: 2. Functions WITHOUT arguments:
# EDU:    - Can be referenced directly in layout
# EDU:    - Execute immediately when called by StreamDeck
# EDU:    - Use: "action": actions.function_name
# EDU:
# EDU: COMMON MISTAKE:
# EDU: ===============
# EDU: Using return wrapper() for functions with arguments will cause them to execute
# EDU: during layout creation instead of when the key is pressed, breaking the intended
# EDU: behavior and causing the layout to store None instead of a callable function.
# EDU:
# EDU: EXAMPLE COMPARISON:
# EDU: ===================
# EDU: CORRECT (with arguments):
# EDU:   def toggle_mic(deck, key):
# EDU:       def wrapper():
# EDU:           render_keys(deck, key, ...)
# EDU:       return wrapper  # ✓ Correct: returns function for later execution
# EDU:
# EDU: INCORRECT (with arguments):
# EDU:   def toggle_mic(deck, key):
# EDU:       def wrapper():
# EDU:           render_keys(deck, key, ...)
# EDU:       return wrapper()  # ✗ Wrong: executes immediately, returns None
# EDU:
# EDU: This documentation explains the wrapper pattern inconsistencies that were
# EDU: causing the microphone toggle functionality to fail.

# EDU: DESIGN PATTERN: Module-level Configuration with General Initialization
# EDU: =======================================================================
# EDU: This module now uses the general init_module() function from config.initialization
# EDU: instead of having its own initialization function. This reduces code duplication
# EDU: and provides a consistent initialization pattern across all jarvis modules.
# EDU:
# EDU: WHAT ARE GLOBAL VARIABLES? (For Beginners)
# EDU: ==========================================
# EDU: Global variables are variables that can be accessed from anywhere in the module.
# EDU: They exist at the "module level" - outside of any function or class.
# EDU:
# EDU: WHY USE GLOBAL VARIABLES HERE?
# EDU: ==============================
# EDU: The StreamDeck library calls our action functions directly when keys are pressed.
# EDU: We can't change the function signatures (parameters) that StreamDeck expects.
# EDU: So we need a way for all action functions to access the configuration.
# EDU:
# EDU: EXAMPLE: When you press key 5, StreamDeck calls toggle_mic() with no parameters.
# EDU: But toggle_mic() needs YDOTOOL_PATH and KEYCODES to work. Global variables
# EDU: let us store these values once and access them from any function.
# EDU:
# EDU: INITIALIZATION:
# EDU: The config.initialization.init_module() function sets these global variables
# EDU: by calling setattr(module, key, value) for each configuration parameter.

# EDU: URL Functions - Browser Integration
# EDU: ======================================
# EDU: BROWSER INTEGRATION DECISIONS:
# EDU:    Originally considered checking for existing browser tabs and focusing them
# EDU:    instead of opening new tabs. This would involve Chrome DevTools Protocol (CDP)
# EDU:    or similar browser automation tools.
# EDU:
# EDU:    WHY SIMPLE APPROACH WAS CHOSEN:
# EDU:    - CDP is complex and overkill for simple URL opening
# EDU:    - Security risks with browser automation protocols
# EDU:    - xdg-open is simpler, safer, and more reliable
# EDU:    - Works with any browser (Chrome, Firefox, Edge, etc.)
# EDU:    - Respects user's default browser preference
# EDU:
# EDU:    TECHNICAL DETAILS:
# EDU:    - xdg-open delegates to desktop environment's URL handler
# EDU:    - Most browsers will reuse existing windows when possible
# EDU:    - URL opening is non-blocking (doesn't freeze jarvis)
# EDU:
# EDU:    ALTERNATIVE METHODS CONSIDERED:
# EDU:    - webbrowser.open(): Python standard library, but less robust on Linux
# EDU:    - Direct browser commands: Browser-specific, not portable
# EDU:    - CDP/WebDriver: Overkill and security risks for simple URL opening
# EDU:
# EDU:    BROWSER COMPATIBILITY:
# EDU:    xdg-open works with all major browsers:
# EDU:    - Chrome/Chromium: google-chrome
# EDU:    - Firefox: firefox
# EDU:    - Edge: microsoft-edge
# EDU:    - Safari: (not available on Linux)
# EDU:    - Brave: brave-browser
# EDU:    - Opera: opera
# EDU:
# EDU:    SECURITY CONSIDERATIONS:
# EDU:    - URL is hardcoded and safe (no user input injection)
# EDU:    - xdg-open is a trusted system utility
# EDU:    - No browser automation or remote control involved
# EDU:    - Browser handles HTTPS validation and security

def url_freecodecamp() -> None:
    """Open freeCodeCamp website in default browser."""
    # EDU: Quick access to freeCodeCamp learning platform for coding tutorials,
    # EDU: challenges, and educational content.
    # EDU: EDUCATIONAL WORKFLOW:
    # EDU: Having quick access to learning platforms supports continuous learning
    # EDU: and skill development during coding sessions.
    subprocess.Popen(["xdg-open", "https://www.freecodecamp.org/"])

def url_youtube() -> None:
    """Open YouTube in default browser."""
    # EDU: Simple utility function to quickly access YouTube using the system's
    # EDU: default web browser via xdg-open standard.
    # EDU: DESIGN CONSISTENCY:
    # EDU: Follows same pattern as other web-opening functions for consistency
    # EDU: and predictable behavior across all web-based StreamDeck actions.
    subprocess.Popen(["xdg-open", "https://www.youtube.com/"])

def url_github() -> None:
    """Open GitHub profile in default browser."""
    # EDU: This function opens the GitHub profile page using the system's default web browser.
    # EDU: It uses xdg-open which is the standard Linux way to open URLs and files with
    # EDU: their associated default applications.
    # EDU: xdg-open is the freedesktop.org standard for opening files/URLs
    subprocess.Popen(["xdg-open", "https://github.com/NhoaKing-Tech"])

def url_gemini() -> None:
    """Open Gemini AI in default browser."""
    subprocess.Popen(["xdg-open", "https://gemini.google.com/"])

def url_claude() -> None:
    """Open Claude AI in default browser."""
    subprocess.Popen(["xdg-open", "https://claude.ai/"])

def url_chatgpt() -> None:
    """Open ChatGPT in default browser."""
    subprocess.Popen(["xdg-open", "https://chatgpt.com/"])

# 2. Spotify
def spotify() -> None:
    """Launch Spotify if not running, otherwise toggle play/pause.

    Uses pgrep to check process and playerctl for media control.
    """
    # EDU: This function implements intelligent Spotify management:
    # EDU: - If Spotify is not running: Launch the application
    # EDU: - If Spotify is running: Toggle play/pause state
    # EDU:
    # EDU: This dual behavior makes the StreamDeck key work like a smart media button
    # EDU: that adapts based on current state.
    # EDU:
    # EDU: TECHNICAL IMPLEMENTATION:
    # EDU: - Uses pgrep to check if Spotify process is running
    # EDU: - Uses playerctl for media control (works with any MPRIS-compatible player)
    # EDU: - Non-blocking execution for responsive UI
    # EDU:
    # EDU: PLAYERCTL ADVANTAGES:
    # EDU: - Works with multiple media players (Spotify, VLC, Firefox, etc.)
    # EDU: - Provides standardized media control interface
    # EDU: - Handles player focus and switching automatically
    # EDU: - More reliable than application-specific APIs
    # EDU:
    # NOTE: No lambda wrapper needed - this function doesn't take parameters and executes immediately,
    # so it doesn't need the factory pattern used by parameterized functions.

    # EDU: Check if Spotify process is currently running
    # EDU: pgrep flags: -x (exact match), searches for process name "spotify"
    # EDU: capture_output=True prevents command output from appearing in terminal
    spotify_check = subprocess.run(["pgrep", "-x", "spotify"], capture_output=True)

    # EDU: Check return code: 0 = found process, non-zero = process not found
    if spotify_check.returncode == 0:
        # EDU: Spotify is running - toggle play/pause state
        # EDU: playerctl flags: --player=spotify (target specific player), play-pause (toggle command)
        subprocess.Popen(["playerctl", "--player=spotify", "play-pause"])

        # EDU: ALTERNATIVE PLAYERCTL COMMANDS:
        # EDU: - "play" - force play state
        # EDU: - "pause" - force pause state
        # EDU: - "next" - skip to next track
        # EDU: - "previous" - go to previous track
        # EDU: - "stop" - stop playback

    else:
        # EDU: Spotify not running - launch the application
        # EDU: This will start Spotify in the background
        subprocess.Popen(["spotify"])

        # EDU: SPOTIFY LAUNCH ALTERNATIVES:
        # EDU: - Flatpak: flatpak run com.spotify.Client
        # EDU: - Snap: snap run spotify
        # EDU: - Web player: xdg-open https://open.spotify.com
        # EDU:
        # EDU: Using simple "spotify" command works with most installation methods
        # EDU: as they typically create a symlink in PATH

    # OPTIMIZE: Cache Spotify running state to avoid repeated pgrep calls
    # OPTIMIZE: Use D-Bus to communicate directly with Spotify (more efficient)
    # OPTIMIZE: Implement timeout for Spotify launch detection
    # TODO: Add visual feedback on StreamDeck key for current state

    # EDU: ERROR HANDLING CONSIDERATIONS:
    # EDU: - pgrep might fail if procfs is not available
    # EDU: - playerctl might fail if no MPRIS session exists
    # EDU: - spotify command might fail if not in PATH
    # EDU: Current implementation gracefully handles these by allowing subprocess errors

# EDU: ## Circular import to avoid
# EDU: I was importing render_keys from ui.render at the top of the file, but this was causing a circular import issue.
# EDU: 
# EDU: render_keys import moved inside toggle_mic function to avoid circular import
# EDU: 
# EDU: This breaks the cycle: actions -> ui.render -> core.logic -> actions

# 3. Microphone state function and toggle ON/OFF
def is_mic_muted() -> bool:
    """Check if microphone is muted using amixer.

    Returns:
        bool: True if muted ("[off]" in output), False if active
    """
    # EDU: This function uses the ALSA amixer command to query the current state
    # EDU: of the Capture (microphone) audio device.
    # EDU: Requires amixer to be installed and the Capture device to be available.
    # EDU: This is the standard microphone control on most Linux systems.
    result = subprocess.run(
        ["amixer", "get", "Capture"],
        capture_output=True,
        text=True
    )
    return "[off]" in result.stdout


def toggle_mic(deck: Any, key: int):
    """Toggle microphone mute and update StreamDeck key with visual feedback.

    Args:
        deck: StreamDeck device object
        key: Key number (0-31) to update

    Returns:
        callable: Function that performs toggle when called

    Note:
        Uses factory pattern (returns wrapper, not wrapper())
    """
    # EDU: This function implements a factory pattern that returns a callable which,
    # EDU: when executed, will toggle the microphone mute state and immediately update
    # EDU: the corresponding StreamDeck key with appropriate visual feedback.
    # EDU:
    # EDU: Visual Feedback:
    # EDU: - Muted: Shows "OFF" label with "mic-off.png" icon
    # EDU: - Active: Shows "ON" label with "mic-on.png" icon
    # EDU:
    # EDU: Uses amixer to control the Capture device. Requires ALSA to be configured.

    def wrapper():
        # NOTE: Import render_keys here to avoid circular import
        from jarvis.ui.render import render_keys

        subprocess.run(["amixer", "set", "Capture", "toggle"])
        muted = is_mic_muted()
        render_keys(deck, key,
                   label="OFF" if muted else "ON",
                   icon="mic-off.png" if muted else "mic-on.png")

    return wrapper

# 4. Hotkeys
def hot_keys(*keys: str) -> None:
    """Simulate hotkey combination using ydotool.

    Keys are pressed in order, released in reverse to prevent sticky keys.

    Args:
        *keys: Key names (e.g., "CTRL", "C" for Ctrl+C)

    Raises:
        RuntimeError: If module not initialized
        ValueError: If unknown key name provided

    Example:
        hot_keys("CTRL", "C") -> Press Ctrl, press C, release C, release Ctrl
    """
    # EDU: This function presses multiple keys simultaneously (like Ctrl+C, Alt+Tab, etc.)
    # EDU: and releases them in the correct order to avoid "sticky key" issues.
    # EDU:
    # EDU: Technical Details:
    # EDU: - Keys are pressed in the order specified (left to right)
    # EDU: - Keys are released in reverse order (right to left) to prevent sticky keys
    # EDU: - Each key event is formatted as "keycode:state" (1=press, 0=release)
    # EDU: - All events are sent in a single ydotool command for atomic execution

    if KEYCODES is None or YDOTOOL_PATH is None:
        raise RuntimeError("Actions module not initialized. Call initialize_actions() from main first.")

    sequence = []

    # NOTE: Press keys in forward order
    for key in keys:
        # EDU: Look up the Linux input event code for this key name
        if key not in KEYCODES:
            raise ValueError(f"Unknown key: {key}. Available keys: {list(KEYCODES.keys())}")
        # EDU: Format as "keycode:1" for key press event
        sequence.append(f"{KEYCODES[key]}:1")

    # IMPORTANT: Release keys in reverse order (essential for proper modifier key handling)
    for key in reversed(keys):
        # EDU: Format as "keycode:0" for key release event
        sequence.append(f"{KEYCODES[key]}:0")

    # HACK: Wake up ydotool daemon from idle with harmless CTRL press
    # EDU: Give ydotool daemon time to wake up from idle state
    # EDU: First command after idle needs a moment to initialize properly
    subprocess.run([YDOTOOL_PATH, "key", "29:1", "29:0"])  # Press and release CTRL key (truly harmless)
    time.sleep(0.05)  # Small delay to ensure completion
    subprocess.run([YDOTOOL_PATH, "key"] + sequence)

    # DEBUG: If hotkeys aren't working, try running this manually:
    # DEBUG: ydotool key 29:1 46:1 46:0 29:0  # Ctrl+C example
    # DEBUG: This helps verify that ydotool is working and the keycodes are correct


def hk_terminal() -> None:
    """Open terminal using Ctrl+Alt+T (standard Linux hotkey).

    Respects user's default terminal and desktop environment settings.
    """
    # EDU: This function simulates the Ctrl+Alt+T keyboard shortcut which is the
    # EDU: standard way to open a terminal window across most Linux desktop environments.
    # EDU: This approach respects the user's default terminal preference and integrates
    # EDU: properly with the desktop environment's window management.
    # EDU:
    # EDU: Desktop Environment Compatibility:
    # EDU: - GNOME: Opens gnome-terminal
    # EDU: - KDE: Opens konsole
    # EDU: - XFCE: Opens xfce4-terminal
    # EDU: - i3/sway: Opens configured terminal ($TERMINAL)
    # EDU: - Others: Opens system default terminal
    # EDU:
    # EDU: Advantages:
    # EDU: - Respects user's default terminal preference
    # EDU: - Works consistently across different desktop environments
    # EDU: - Faster than discovering and launching specific terminal executable
    # EDU: - Integrates with desktop environment's window management
    # EDU:
    # NOTE: This is preferred over direct terminal commands because it uses the
    # desktop environment's configured default rather than hardcoding a
    # specific terminal emulator.

    # EDU: Send the standard Linux terminal hotkey combination
    # EDU: This is recognized by virtually all Linux desktop environments
    hot_keys("CTRL", "ALT", "T")

    # OPTIMIZE: Hotkey simulation is faster than process discovery and launching
    # OPTIMIZE: The desktop environment handles terminal selection and configuration


def hk_copy() -> None:
    """Copy selected text using Ctrl+C."""
    # EDU: Simple demonstration of the hot_keys function that sends the standard
    # EDU: copy-to-clipboard keyboard shortcut. This is a basic example of hotkey usage.
    hot_keys("CTRL", "C")

# 5. Open VSCode application with a given project path
def open_vscode(project_path: str) -> Callable[[], None]:
    """Open VSCode with project and integrated terminal.

    Args:
        project_path: Absolute path to project directory

    Returns:
        callable: Function that launches VSCode when called

    Note:
        2-second delay allows VSCode to initialize before terminal hotkey.
        Configure per-project settings in .vscode/settings.json
    """
    # TODO: Check if VSCode already has project open before launching
    # OPTIMIZE: Make delay configurable based on system performance
    # EDU: Alternative approaches:
    # EDU: - Use VSCode's --command flag: code --command workbench.action.terminal.new
    # EDU: - Use VSCode's remote development features for containerized projects
    # EDU: - Integrate with VSCode's workspace API for session management

    # EDU: This function returns a callable that opens VSCode, waits for initialization,
    # EDU: then automatically opens the integrated terminal. You can deactivate the terminal toggle
    # EDU: shortcut if you do not want it.
    # EDU:
    # EDU: Workflow:
    # EDU: 1. Launch VSCode with the specified project directory
    # EDU: 2. Wait 2 seconds for VSCode to fully load and initialize
    # EDU: 3. Send Ctrl+` hotkey to open the integrated terminal
    # EDU:
    # EDU: VSCode Integration:
    # EDU: Each project should have a .vscode/settings.json file to configure:
    # EDU: - Terminal working directory
    # EDU: - Environment variables
    # EDU: - Python interpreter path
    # EDU: - Extensions and settings specific to that project
    # EDU:
    # EDU: Timing:
    # EDU: The 2-second delay is necessary because VSCode needs time to initialize
    # EDU: before accepting hotkeys. This delay works well for most hardware and
    # EDU: project sizes.

    def wrapper():
        # EDU: Launch VSCode with the project path as argument
        # EDU: VSCode will open the directory and load workspace settings
        subprocess.Popen(["code", project_path])

        # NOTE: VSCode needs time to initialize
        # EDU: Wait for VSCode to fully initialize before sending hotkeys
        # EDU: This prevents the terminal hotkey from being ignored
        time.sleep(2)

        # EDU: Open VSCode integrated terminal using Ctrl+` (grave/backtick)
        # EDU: This provides immediate access to command line in project context
        hot_keys("CTRL", "GRAVE")

    return wrapper

# 6. Type text and snippets
def type_text(text: str) -> Callable[[], None]:
    """Type text using ydotool into focused application.

    Args:
        text: Text to type

    Returns:
        callable: Function that types text when called

    Raises:
        RuntimeError: If module not initialized

    Note:
        Uses factory pattern (returns wrapper, not wrapper())
    """
    # OPTIMIZE: For large text blocks, consider clipboard operations instead
    # EDU: This function returns a callable that simulates typing the given text into
    # EDU: the currently focused application using ydotool for low-level input events.
    # EDU:
    # EDU: Technical Details:
    # EDU: - Uses "--" argument to prevent ydotool flag interpretation
    # EDU: - Works on both X11 and Wayland (unlike xdotool which is X11-only)
    # EDU: - Non-blocking execution doesn't freeze the UI
    # EDU: - Each character sent as separate input event
    # EDU:
    # EDU: Performance:
    # EDU: Character-by-character input is slower for long text. For large text
    # EDU: blocks, consider using clipboard operations instead.
    # EDU:
    # EDU: Design Pattern:
    # EDU: Factory function pattern - returns a function rather than executing
    # EDU: immediately. This allows configuration during layout building and
    # EDU: execution when keys are pressed.

    def wrapper():
        if YDOTOOL_PATH is None:
            raise RuntimeError("Actions module not initialized. Call initialize_actions() from main first.")

        # NOTE: "--" prevents text starting with "-" being interpreted as flags
        # EDU: Execute ydotool command to type the text
        # EDU: Arguments:
        # EDU: - YDOTOOL_PATH: Path to ydotool executable
        # EDU: - "type": ydotool subcommand for typing text
        # EDU: - "--": Indicates end of options, prevents text starting with "-" being interpreted as flags
        # EDU: - text: The actual text to type
        subprocess.Popen([YDOTOOL_PATH, "type", "--", text])

        # EDU: ALTERNATIVE TOOLS CONSIDERED:
        # EDU: - xdotool: More mature but X11-only, doesn't work on Wayland, and since this project was started
        # EDU: on Wayland, ydotool was the better choice. When shifting to X11, I kept ydotool as it seems to work
        # EDU: fine on X11 too. No need to change it for now, unless I face limitations or issues in the future.
        # EDU: - PyAutoGUI: Not tested yet, but I keep it in mind for future exploration.

    return wrapper


def type_keyring() -> Callable[[], None]:
    """Type configured password followed by Enter.

    Returns:
        callable: Function that types password when called

    Raises:
        RuntimeError: If KEYRING_PW not configured

    Security:
        Password stored in environment variables (config.env).
        Consider using proper password managers for production.
    """
    if KEYRING_PW is None:
        raise RuntimeError("KEYRING_PW not initialized. Call initialize_actions() from main first.")
    return type_text(KEYRING_PW + "\n")


def type_snippet(snippet_name: str) -> Callable[[], None]:
    """Load and type code snippet from text file.

    Args:
        snippet_name: Snippet filename without .txt extension

    Returns:
        callable: Function that types snippet when called

    Raises:
        RuntimeError: If module not initialized

    Note:
        Snippets stored in SNIPPETS_DIR as .txt files.
        Missing snippets generate warning but don't crash.
    """
    # OPTIMIZE: Could cache frequently used snippets in memory
    # EDU: Design Decision - File-based storage vs Database:
    # EDU: We use text files because:
    # EDU: 1. SIMPLICITY: Easy to edit snippets with any text editor
    # EDU: 2. VERSION CONTROL: Can track snippet changes in git
    # EDU: 3. PORTABILITY: No database setup required
    # EDU: 4. TRANSPARENCY: Users can see exactly what will be typed
    # EDU:
    # EDU: USAGE EXAMPLES:
    # EDU: - type_snippet("python_boilerplate") -> loads python_boilerplate.txt
    # EDU: - type_snippet("html_template") -> loads html_template.txt
    # EDU: - type_snippet("git_commit_msg") -> loads git_commit_msg.txt
    # EDU:
    # EDU: This function loads a code snippet from the snippets directory and types it
    # EDU: into the currently focused application. Snippets are stored as .txt files
    # EDU: and can contain boilerplate code, templates, commonly used commands, etc.
    # EDU:
    # EDU: ERROR HANDLING:
    # EDU: - Gracefully handles missing snippet files with user feedback
    # EDU: - Validates module initialization before attempting file operations
    # EDU:
    # EDU: PERFORMANCE OPTIMIZATION OPPORTUNITIES:
    # EDU: - Could cache frequently used snippets in memory
    # EDU: - Could preload all snippets at startup
    # EDU: - Could use async I/O for large snippets
    # EDU: However, snippets are typically small and accessed infrequently,
    # EDU: so the current simple approach is adequate.

    def wrapper():
        if SNIPPETS_DIR is None or YDOTOOL_PATH is None:
            raise RuntimeError("Actions module not initialized. Call initialize_actions() from main first.")

        snippet_path = SNIPPETS_DIR / (snippet_name + ".txt")

        if not snippet_path.exists():
            print(f"Warning: Snippet '{snippet_name}' not found at {snippet_path}")
            return

        # EDU: Read snippet content from file
        # EDU: Using context manager (with statement) ensures file is properly closed
        try:
            with open(snippet_path, "r", encoding="utf-8") as f:
                snippet_content = f.read()
        except IOError as e:
            print(f"Error reading snippet file {snippet_path}: {e}")
            return

        # EDU: Type the snippet content using ydotool
        # EDU: Same approach as type_text() function
        subprocess.Popen([YDOTOOL_PATH, "type", "--", snippet_content])

    return wrapper

# 7. Open obsidian with a given vault path
def open_obsidian(vault_path: str) -> Callable[[], None]:
    """Open or focus Obsidian vault.

    Checks if vault already open and focuses window instead of opening new instance.

    Args:
        vault_path: Path to Obsidian vault directory

    Returns:
        callable: Function that opens/focuses vault when called

    Note:
        Uses Obsidian URI scheme and wmctrl for window management.
    """
    # EDU: Window Management Strategy:
    # EDU: 1. Check if Obsidian already has vault open (wmctrl)
    # EDU: 2. If found, activate existing window
    # EDU: 3. If not found, launch via URI scheme
    # EDU: This prevents window clutter and improves UX

    # OPTIMIZE: wmctrl window search typically <10ms
    # OPTIMIZE: Could cache window list to avoid repeated wmctrl calls
    # EDU: Alternative Launch Methods:
    # EDU: - Direct: obsidian --vault /path/to/vault
    # EDU: - Flatpak: flatpak run md.obsidian.Obsidian --vault /path/to/vault
    # EDU: - AppImage: ./Obsidian.AppImage --vault /path/to/vault
    # EDU: URI scheme works regardless of installation method

    # EDU: This function implements smart window management - it first checks if Obsidian
    # EDU: is already open with the target vault, and if so, brings it to focus instead
    # EDU: of opening a new instance. This prevents window clutter and improves UX.
    # EDU:
    # EDU: OBSIDIAN INTEGRATION:
    # EDU: - Uses Obsidian's URI scheme (obsidian://open?vault=name) for launching
    # EDU: - Supports Obsidian's native vault naming and organization
    # EDU: - Works with both local and synced vaults

    # EDU: Extract vault name from the full path for window matching and URI construction
    # EDU: Path.resolve() normalizes the path and .name gets the final component
    vault_name = Path(vault_path).resolve().name

    def wrapper():
        # EDU: STEP 1: Check if Obsidian is already open with this vault
        try:
            # EDU: Use wmctrl to list all open windows with their titles
            # EDU: wmctrl -l output format: window_id desktop_num client_machine window_title
            wmctrl_output = subprocess.check_output(["wmctrl", "-l"], text=True)

            # EDU: Search through each window to find Obsidian with our vault
            for line in wmctrl_output.splitlines():
                # EDU: Look for lines containing both "Obsidian" and our vault name
                # EDU: This matches window titles like "Obsidian - vault_name" or "vault_name - Obsidian"
                if "Obsidian" in line and vault_name in line:
                    # EDU: Extract window ID (first column in wmctrl output)
                    window_id = line.split()[0]  # Format: 0x01234567

                    # EDU: Activate the existing window (bring to front and focus)
                    # EDU: wmctrl flags: -i (use window ID), -a (activate window)
                    subprocess.run(["wmctrl", "-i", "-a", window_id])
                    return  # Exit early - we found and activated the window

        except subprocess.CalledProcessError:
            # EDU: wmctrl command failed (maybe not installed, or no X11 session)
            # EDU: Continue to launch new instance - this is not a critical error
            pass

        # EDU: STEP 2: No existing window found, launch new Obsidian instance
        # EDU: Use Obsidian's URI scheme for clean vault opening
        # EDU: Format: obsidian://open?vault=vault_name
        uri = f"obsidian://open?vault={vault_name}"

        # EDU: Use xdg-open to handle the URI scheme
        # EDU: xdg-open is the standard Linux way to open files/URIs with default applications
        subprocess.Popen(["xdg-open", uri])

    return wrapper

# 8. Execute bash scripts for automating stuff
def execute_bash(bash_script: str, *args: str, in_terminal: bool = False):
    """Execute bash script with optional arguments.

    Args:
        bash_script: Script filename in BASHSCRIPTS_DIR
        *args: Optional arguments to pass to script
        in_terminal: If True, run in new terminal window

    Returns:
        callable: Function that executes script when called

    Note:
        Auto-fixes executable permissions if needed.
    """
    def wrapper():
        if BASHSCRIPTS_DIR is None:
            raise RuntimeError("Actions module not initialized. Call initialize_actions() from main first.")

        # EDU: pathlib.Path provides cross-platform path construction
        script_path = BASHSCRIPTS_DIR / bash_script

        if not script_path.exists():
            return

        # NOTE: Auto-fix permissions if not executable
        if not os.access(script_path, os.X_OK):
            try:
                # EDU: The bash script should be executable (chmod u+x)
                os.chmod(script_path, 0o744)  # rwxr--r-- permissions (user execute only)
            except Exception:
                return

        try:
            if in_terminal:
                # EDU: Build command for terminal execution
                cmd_str = f"bash '{script_path}'"
                if args:
                    escaped_args = [f"'{arg}'" for arg in args]
                    cmd_str += " " + " ".join(escaped_args)
                subprocess.Popen([
                    "gnome-terminal", "--", "bash", "-c", cmd_str
                ])
            else:
                cmd = [script_path] + list(args)
                subprocess.Popen(cmd)
        except Exception as e:
            print(f"Failed to execute script: {e}")

    return wrapper()


def terminal_env_jarvis() -> None:
    """Open terminal with jarvis/busybee conda environment activated.

    Executes open_jarvisbusybee_env_T.sh script.
    """
    # EDU: Script Delegation Pattern:
    # EDU: Complex terminal setup handled by bash scripts rather than Python
    # EDU: because bash is better suited for terminal/environment manipulation
    # EDU: and scripts can be modified without changing Python code
    # EDU:
    # EDU: This function launches a terminal window with a pre-configured conda environment
    # EDU: that's set up for jarvis development work. The environment includes all necessary
    # EDU: dependencies for StreamDeck development, Python automation, and related tools.
    # EDU:
    # EDU: Script Execution:
    # EDU: Executes "open_jarvisbusybee_env_T.sh" which handles:
    # EDU: - Opening a new terminal window
    # EDU: - Activating the appropriate conda environment
    # EDU: - Setting working directory to jarvis project
    # EDU: - Loading any necessary environment variables
    execute_bash("open_jarvisbusybee_env_T.sh")


def terminal_env_busybee() -> None:
    """Open terminal with busybee conda environment activated.

    Executes open_busybee_env_T.sh script.
    """
    # EDU: Similar to terminal_env_jarvis() but specifically for the busybee project
    # EDU: environment. See terminal_env_jarvis() for detailed workflow explanation.
    execute_bash("open_busybee_env_T.sh")


def defaultbranch_commit() -> None:
    """Execute interactive git commit workflow.

    Runs git_commit_workflow.sh which prompts for project and handles
    git status, add, and commit with user interaction at each step.
    """
    # EDU: Executes a git commit workflow using a bash script with interactivity.
    # EDU: in_terminal=False, because the script handles its own terminal.
    # EDU: Takes 'PROJECTS_DIR' as an argument
    # EDU: Prompts user for project name, then navigates to PROJECTS_DIR/PROJECT_NAME
    # EDU: and runs git status, git add ., and git commit with user prompts between each step.
    # EDU: User can exit at any point using CTRL+C. To continue the workflow, user can simply click ENTER in the terminal
    # EDU: to proceed to the next step, or to close the terminal when done. I have the git config to open the
    # EDU: commit message in vscode, as I prefer that over nano or vim. I have the lines showing me where the
    # EDU: commit title and description can extend to, so this is nice.
    execute_bash("git_commit_workflow.sh", str(PROJECTS_DIR), in_terminal=False)

# 9. Open nautilus windows with a target path. If that path is already open in another window, simply raise it, to avoid multiple nautilus windows with the same path
def nautilus_path(target_dir: str) -> Callable[[], None]:
    """Open or focus Nautilus file manager at directory.

    Checks if directory already open and focuses window instead of opening new instance.

    Args:
        target_dir: Path to directory

    Returns:
        callable: Function that opens/focuses directory when called

    Note:
        Requires wmctrl for window management.
    """
    # EDU: Window Management Strategy (same as open_obsidian):
    # EDU: 1. Check if Nautilus already has directory open
    # EDU: 2. If found, activate window
    # EDU: 3. If not, launch new Nautilus instance
    # EDU: Prevents multiple windows for same directory
    # EDU:
    # EDU: Path Resolution:
    # EDU: - Resolves relative paths to absolute for consistent matching
    # EDU: - Resolves symbolic links to actual paths
    # EDU: - Ensures same format when checking window titles
    # EDU:
    # EDU: wmctrl Details:
    # EDU: - "-lx" flags: -l (list windows), -x (include WM_CLASS)
    # EDU: - Output format: window_id desktop_num WM_CLASS hostname window_title
    # EDU: - WM_CLASS "org.gnome.Nautilus" identifies Nautilus windows
    # EDU: - "-i -a window_id" activates window by ID

    def wrapper():
        # NOTE: Resolve to absolute path for consistent window title matching
        # EDU: I need to convert the target directory to an absolute path because:
        # EDU: 1. Relative paths like "../folder" or "./folder" can be ambiguous
        # EDU: 2. Path.resolve() converts these to full paths like "/home/user/folder"
        # EDU: 3. This ensures I am comparing the same format when checking window titles later
        # EDU: 4. It also resolves any symbolic links to their actual paths
        # EDU:    (Symbolic links are like shortcuts - they point to another file/directory.
        # EDU:     Path.resolve() follows the shortcut to get the real location)
        resolved_dir = str(Path(target_dir).resolve())

        # EDU: STEP 1: Check if Nautilus is already open with my target directory
        # EDU:
        # EDU: wmctrl is a command-line tool that lets me interact with X11 windows in Linux
        # EDU: The "-lx" flags mean:
        # EDU: -l: list all windows
        # EDU: -x: include the WM_CLASS property (this helps me identify the application type)
        # EDU:
        # EDU: subprocess.check_output() runs this command and captures its text output
        # EDU: text=True ensures I get a string back instead of bytes
        try:
            wmctrl_output = subprocess.check_output(["wmctrl", "-lx"], text=True)

            # EDU: The wmctrl output looks like this (one line per window):
            # EDU: 0x02400003  0 org.gnome.Nautilus.org.gnome.Nautilus desktop file-browser - /home/user/Documents
            # EDU: 0x02600004  0 firefox.Firefox          desktop Firefox
            # EDU:
            # EDU: Each line contains: window_id, desktop_number, WM_CLASS, hostname, window_title
            # EDU: I need to parse each line to extract the information I need
            for line in wmctrl_output.splitlines():
                # EDU: I only care about Nautilus windows, so I check if "org.gnome.Nautilus"
                # EDU: is in the line. This is the WM_CLASS identifier for Nautilus windows.
                if "org.gnome.Nautilus" in line:

                    # EDU: Now I need to extract the window ID and title from this line
                    # EDU: line.split() breaks the line into parts separated by whitespace
                    # EDU: The window ID is always the first part (index 0)
                    # EDU: Example: "0x02400003" from the line above
                    window_id = line.split()[0]

                    # EDU: The window title starts from the 4th element (index 3) onwards
                    # EDU: I use " ".join() to put the title back together with spaces
                    # EDU: because the title might contain spaces that were split apart
                    # EDU: Example: from "desktop file-browser - /home/user/Documents"
                    # EDU: I want "file-browser - /home/user/Documents"
                    window_title = " ".join(line.split()[3:])

                    # EDU: Now I need to check if this Nautilus window is showing my target directory
                    # EDU: There are different ways the directory might appear in the window title:
                    # EDU:
                    # EDU: First, I get just the folder name (last part of the path)
                    # EDU: Path(path).name returns "Documents" from "/home/user/Documents"
                    # EDU: This helps me match windows that might not show the full path
                    folder_name = Path(resolved_dir).name

                    # NOTE: Check multiple title formats for matching
                    # EDU: I check three conditions to see if this window matches my target:
                    if (resolved_dir in window_title or          # Full path is in title
                        folder_name in window_title or        # Just folder name is in title
                        window_title.endswith(folder_name)):  # Title ends with folder name

                        # EDU: I found a matching window! Instead of opening a new one,
                        # EDU: I will bring this existing window to the front (raise it)
                        # EDU:
                        # EDU: wmctrl can also control windows, not just list them
                        # EDU: -i: "use window ID" - I am giving it a window ID number (0x02400003)
                        # EDU: instead of a window title/name (more reliable than titles)
                        # EDU: -a: "activate window" - bring the window to front and give it focus
                        # EDU: (like clicking on it in the taskbar)
                        # EDU: window_id: the window ID I extracted earlier (like 0x02400003)
                        subprocess.run(["wmctrl", "-i", "-a", window_id])
                        return

        except subprocess.CalledProcessError:
            # EDU: wmctrl command failed (maybe not installed, or no X11 session)
            # EDU: Continue to launch new instance - this is not a critical error
            pass

        # EDU: STEP 2: If I get here, it means I did not find any existing Nautilus window
        # EDU: with my target directory, so I need to open a new one
        # EDU:
        # EDU: subprocess.Popen() starts a new process without waiting for it to finish
        # EDU: This is perfect for GUI applications because:
        # EDU: 1. I don't want my Python script to hang waiting for Nautilus to close
        # EDU: 2. The user should be able to use Nautilus independently
        # EDU: 3. My script can continue with other tasks
        # EDU:
        # EDU: I pass the target directory as an argument to nautilus so it opens there
        subprocess.Popen(["nautilus", resolved_dir])

    return wrapper



