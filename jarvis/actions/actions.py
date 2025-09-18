"""
--GENERAL INFORMATION --
AUTHOR: NhoaKing (pseudonym for privacy)
NAME: actions.py
DESCRIPTION: Python module containing all the actions triggered by key press events on the stream deck XL from ElGato
FINISH DATE: September 18th 2025 (Thursday)
"""

"""
-- BRIEF DESCRIPTION --
This module bridges key events (key presses) with system operations.

CONFIGURATION FLOW (How Dependencies Get Here):
===============================================
1. systemd service loads config.env via 'EnvironmentFile' directive
2. run_jarvis.py reads those environment variables using os.getenv()
3. run_jarvis.py passes the loaded values to this module via initialize_actions()
4. This module stores them in global variables for use by action functions

This is called the Dependency Injection (DI) pattern.

WHY NOT READ ENVIRONMENT VARIABLES DIRECTLY HERE?
=================================================
We could have each action function call os.getenv() directly, but we chose
dependency injection instead because:
- Keeps configuration loading centralized in run_jarvis.py
- Makes dependencies explicit (you can see what each module needs)
- Easier to test (can pass mock values instead of real environment variables)
- Better separation of concerns (run_jarvis.py handles config, this handles actions)

The .env file provides the configuration, not the logic itself.
Configuration flows: config.env → systemd → run_jarvis.py → actions.py

It handles so far the following topics. Function names are listed for each.
1. Opening of URLs in default browser. In my case, Goggle Chrome. Functions here are:
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
- type_keyring (Type and enter passwords without exposing them in your codebase. 
The password can be stored in config.env)
7. Open obsidian with a given vault path. It supports the possibility to open multiple vaults at a time.
- open_obsidian
8. Execute bash scripts
- execute_bash
- Example of usage in terminal_env_jarvis and terminal_env_busybee for basic scripts
- Example of 
9. Open nautilus windows with a target path. If that path is already open in another window, 
simply raise it, to avoid multiple nautilus windows with the same path..... 
which happens often if this check is not in place before opening the window
"""

"""
-- TO DO --
- Generalize nautilus_path function to work with other applications too (for obsidian is already done)
- Handle positioning and sizing of windows, at the moment everything opens correctly but super randomly placed and sized...
"""

# Standard library imports for system interaction
import subprocess  # Execute external commands like ydotool, wmctrl, applications
import time        # Time delays for application startup coordination
import os          # File system operations and path manipulation
from pathlib import Path  # Object-oriented filesystem paths

# Import from our UI module for dynamic key rendering
# Note: render_keys import moved inside toggle_mic function to avoid circular import
# This was: actions -> ui.render -> ui.logic -> actions
# Now render_keys is imported only when needed, breaking the cycle

# Module-level configuration variables (initialized via dependency injection)
# These variables are set by initialize_actions() called from run_jarvis.py
# Using None as default allows us to detect uninitialized state and provide helpful errors

# Path to ydotool executable for keyboard/mouse input simulation
YDOTOOL_PATH = None     # Will be set to system ydotool path or custom path from config

# Directory paths for various asset types
SNIPPETS_DIR = None     # Directory containing code snippet text files
BASHSCRIPTS_DIR = None  # Directory containing executable bash scripts
PROJECTS_DIR = None     # User's main projects directory (usually ~/Zenith)

# Keycode mapping dictionary for ydotool input simulation
KEYCODES = None         # Dictionary mapping key names to Linux input event codes

# User credentials (handled securely via environment variables)
KEYRING_PW = None       # Password for keyring/password manager access

# DESIGN PATTERN: Dependency Injection
# Rather than importing these values or reading config files directly,
# we receive them as parameters. This approach provides:
# 1. TESTABILITY: Easy to mock configuration for unit tests
# 2. FLEXIBILITY: Can be configured differently for different environments
# 3. CLARITY: Dependencies are explicit rather than hidden imports
# 4. ERROR HANDLING: Can detect and report missing configuration

def initialize_actions(ydotool_path, snippets_dir, bashscripts_dir, projects_dir, keycodes, keyring_pw):
    """Initialize the actions module with required configuration from the main module.

    This function implements the Dependency Injection (DI) pattern where the actions
    module receives its dependencies from the outside rather than creating or finding
    them itself. This approach provides better separation of concerns, testability,
    and flexibility.

    Args:
        ydotool_path (str): Path to ydotool executable for input simulation
        snippets_dir (str): Directory containing code snippet text files
        bashscripts_dir (str): Directory containing executable bash scripts
        projects_dir (Path): User's main projects directory
        keycodes (dict): Mapping of key names to Linux input event codes
        keyring_pw (str): Password for keyring/password manager access

    Design Pattern - Dependency Injection:
        Instead of reading environment variables directly in this module, we receive
        all dependencies as parameters. This provides:

        - **Separation of Concerns**: actions.py focuses on WHAT to do (actions),
          while run_jarvis.py focuses on HOW to configure things
        - **Testability**: Easy to test action functions by passing mock values
        - **Flexibility**: Same functions work with different configurations
        - **Explicit Dependencies**: Clear what each module needs to function

    Performance:
        This function runs once at startup, so any validation or preprocessing
        done here doesn't affect runtime performance.

    Note:
        This function must be called before any action functions are used,
        typically during application startup in run_jarvis.py.
    """

    # WHAT ARE GLOBAL VARIABLES? (For Beginners)
    # ==========================================
    # Global variables are variables that can be accessed from anywhere in the module.
    # They exist at the "module level" - outside of any function or class.
    #
    # WHY USE GLOBAL VARIABLES HERE?
    # ==============================
    # The StreamDeck library calls our action functions directly when keys are pressed.
    # We can't change the function signatures (parameters) that StreamDeck expects.
    # So we need a way for all action functions to access the configuration.
    #
    # EXAMPLE: When you press key 5, StreamDeck calls toggle_mic() with no parameters.
    # But toggle_mic() needs YDOTOOL_PATH and KEYCODES to work. Global variables
    # let us store these values once and access them from any function.

    # The 'global' keyword tells Python: "I want to modify the module-level variables,
    # not create new local variables inside this function"
    global YDOTOOL_PATH, SNIPPETS_DIR, BASHSCRIPTS_DIR, PROJECTS_DIR, KEYCODES, KEYRING_PW

    # Store each parameter in its corresponding global variable
    # This is like putting ingredients in labeled containers that any chef can access
    YDOTOOL_PATH = ydotool_path        # Store path to ydotool for input simulation
    SNIPPETS_DIR = snippets_dir        # Store directory for code snippets
    BASHSCRIPTS_DIR = bashscripts_dir  # Store directory for bash scripts
    PROJECTS_DIR = projects_dir        # Store user's projects directory
    KEYCODES = keycodes                # Store keycode mapping dictionary
    KEYRING_PW = keyring_pw            # Store password for secure access

    # DESIGN DECISION EXPLANATION:
    # ============================
    # We considered these alternatives but chose the current approach:
    #
    # 1. CLASS-BASED APPROACH:
    #    - Create an ActionManager class with config as attributes
    #    - PRO: More "object-oriented", encapsulates data and behavior
    #    - CON: More complex, StreamDeck callbacks would need class instance
    #
    # 2. CONTEXT OBJECT:
    #    - Pass a config dictionary to each action function
    #    - PRO: Very explicit about dependencies
    #    - CON: StreamDeck callback signatures are fixed, can't add parameters
    #
    # 3. IMPORT FROM MAIN:
    #    - Import configuration directly from run_jarvis module
    #    - PRO: No need for initialization function
    #    - CON: Creates circular dependencies, harder to test
    #
    # 4. ENVIRONMENT VARIABLES EVERYWHERE:
    #    - Read os.getenv() in every action function that needs config
    #    - PRO: No global state, very explicit
    #    - CON: Duplicate code, slower (multiple getenv calls), scattered configuration
    #
    # We chose GLOBAL VARIABLES WITH DEPENDENCY INJECTION because:
    # - StreamDeck callback functions have fixed signatures (can't pass extra params)
    # - Configuration is read-only after initialization (no mutation concerns)
    # - Simpler than creating a dependency injection framework
    # - Performance: No parameter passing overhead on every action call
    # - Clear separation: run_jarvis.py handles config, actions.py handles actions

# 1. URLs:
def url_freecodecamp():
    """Open freeCodeCamp website in the default web browser.

    Quick access to freeCodeCamp learning platform for coding tutorials,
    challenges, and educational content.

    EDUCATIONAL WORKFLOW:
    Having quick access to learning platforms supports continuous learning
    and skill development during coding sessions.
    """
    # Open freeCodeCamp website with system default browser
    subprocess.Popen(["xdg-open", "https://www.freecodecamp.org/"])

def url_youtube():
    """Open YouTube in the default web browser.

    Simple utility function to quickly access YouTube using the system's
    default web browser via xdg-open standard.

    DESIGN CONSISTENCY:
    Follows same pattern as other web-opening functions for consistency
    and predictable behavior across all web-based StreamDeck actions.
    """
    # Open YouTube homepage with system default browser
    subprocess.Popen(["xdg-open", "https://www.youtube.com/"])

def url_github():
    """Open GitHub profile in the default web browser.

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
    """
    # Use xdg-open to open URL with system default browser
    # xdg-open is the freedesktop.org standard for opening files/URLs
    subprocess.Popen(["xdg-open", "https://github.com/NhoaKing-Tech"])

    # BROWSER COMPATIBILITY:
    # xdg-open works with all major browsers:
    # - Chrome/Chromium: google-chrome
    # - Firefox: firefox
    # - Edge: microsoft-edge
    # - Safari: (not available on Linux)
    # - Brave: brave-browser
    # - Opera: opera

    # SECURITY CONSIDERATIONS:
    # - URL is hardcoded and safe (no user input injection)
    # - xdg-open is a trusted system utility
    # - No browser automation or remote control involved
    # - Browser handles HTTPS validation and security

def url_claude():
    """Open Claude AI in the default web browser.

    Provides quick access to Anthropic's Claude AI assistant for coding help,
    analysis, and development support.

    AI WORKFLOW INTEGRATION:
    Having multiple AI assistants available allows choosing the best tool
    for specific tasks (Claude for analysis, ChatGPT for coding, etc.).
    """
    # Open Claude AI website with system default browser
    subprocess.Popen(["xdg-open", "https://claude.ai/"])

def url_chatgpt():
    """Open ChatGPT in the default web browser.

    Provides quick access to ChatGPT for coding assistance, problem-solving,
    and AI-powered development support during coding sessions.

    AI INTEGRATION WORKFLOW:
    Quick access to AI assistants supports modern development practices
    where AI tools are used for code review, debugging, and learning.
    """
    # Open ChatGPT website with system default browser
    subprocess.Popen(["xdg-open", "https://chatgpt.com/"])

# 2. Spotify
def spotify():
    """Smart Spotify control: launch if not running, otherwise toggle play/pause.

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
    """
    # Check if Spotify process is currently running
    # pgrep flags: -x (exact match), searches for process name "spotify"
    # capture_output=True prevents command output from appearing in terminal
    spotify_check = subprocess.run(["pgrep", "-x", "spotify"], capture_output=True)

    # Check return code: 0 = found process, non-zero = process not found
    if spotify_check.returncode == 0:
        # Spotify is running - toggle play/pause state
        # playerctl flags: --player=spotify (target specific player), play-pause (toggle command)
        subprocess.Popen(["playerctl", "--player=spotify", "play-pause"])

        # ALTERNATIVE PLAYERCTL COMMANDS:
        # - "play" - force play state
        # - "pause" - force pause state
        # - "next" - skip to next track
        # - "previous" - go to previous track
        # - "stop" - stop playback

    else:
        # Spotify not running - launch the application
        # This will start Spotify in the background
        subprocess.Popen(["spotify"])

        # SPOTIFY LAUNCH ALTERNATIVES:
        # - Flatpak: flatpak run com.spotify.Client
        # - Snap: snap run spotify
        # - Web player: xdg-open https://open.spotify.com
        #
        # Using simple "spotify" command works with most installation methods
        # as they typically create a symlink in PATH

    # PERFORMANCE OPTIMIZATION OPPORTUNITIES:
    # - Cache Spotify running state to avoid repeated pgrep calls
    # - Use D-Bus to communicate directly with Spotify (more efficient)
    # - Implement timeout for Spotify launch detection
    # - Add visual feedback on StreamDeck key for current state

    # ERROR HANDLING CONSIDERATIONS:
    # - pgrep might fail if procfs is not available
    # - playerctl might fail if no MPRIS session exists
    # - spotify command might fail if not in PATH
    # Current implementation gracefully handles these by allowing subprocess errors

# 3. Microphone state function and toggle ON/OFF
def is_mic_muted():
    """Check if the microphone is currently muted using amixer.

    This function uses the ALSA amixer command to query the current state
    of the Capture (microphone) audio device.

    Returns:
        bool: True if microphone is muted ("[off]" in output), False if active

    Note:
        Requires amixer to be installed and the Capture device to be available.
        This is the standard microphone control on most Linux systems.
    """
    result = subprocess.run(
        ["amixer", "get", "Capture"],
        capture_output=True,
        text=True
    )
    return "[off]" in result.stdout

def toggle_mic(deck, key):
    """Create a function that toggles microphone mute and updates the StreamDeck icon.

    This function implements a factory pattern that returns a callable which,
    when executed, will toggle the microphone mute state and immediately update
    the corresponding StreamDeck key with appropriate visual feedback.

    Args:
        deck: StreamDeck device object for updating key appearance
        key (int): Key number (0-31) to update with new icon and label

    Returns:
        callable: Function that performs the mic toggle when called

    Visual Feedback:
        - Muted: Shows "OFF" label with "mic-off.png" icon
        - Active: Shows "ON" label with "mic-on.png" icon

    Note:
        Uses amixer to control the Capture device. Requires ALSA to be configured.
    """
    def wrapper():
        # Import render_keys here to avoid circular import
        from ui.render import render_keys

        subprocess.run(["amixer", "set", "Capture", "toggle"])
        muted = is_mic_muted()
        render_keys(deck, key,
                   label="OFF" if muted else "ON",
                   icon="mic-off.png" if muted else "mic-on.png")

    return wrapper

# 4. Hotkeys
def hot_keys(*keys):
    """Simulate a hotkey combination using ydotool.

    This function presses multiple keys simultaneously (like Ctrl+C, Alt+Tab, etc.)
    and releases them in the correct order to avoid "sticky key" issues.

    Args:
        *keys: Variable number of key names (e.g., "CTRL", "C" for Ctrl+C)

    Technical Details:
        - Keys are pressed in the order specified (left to right)
        - Keys are released in reverse order (right to left) to prevent sticky keys
        - Each key event is formatted as "keycode:state" (1=press, 0=release)
        - All events are sent in a single ydotool command for atomic execution

    Examples:
        - hot_keys("CTRL", "C") → Press Ctrl, press C, release C, release Ctrl
        - hot_keys("CTRL", "SHIFT", "T") → Press Ctrl+Shift+T properly
        - hot_keys("ALT", "TAB") → Alt+Tab window switching

    Raises:
        RuntimeError: If actions module not initialized
        ValueError: If unknown key name provided

    Note:
        Reverse release order prevents modifier keys from remaining "stuck"
        after the hotkey sequence completes.
    """
    # Verify module initialization
    if KEYCODES is None or YDOTOOL_PATH is None:
        raise RuntimeError("Actions module not initialized. Call initialize_actions() from main first.")

    # Build sequence of key events
    sequence = []

    # Press all keys in forward order
    for key in keys:
        # Look up the Linux input event code for this key name
        if key not in KEYCODES:
            raise ValueError(f"Unknown key: {key}. Available keys: {list(KEYCODES.keys())}")

        # Format as "keycode:1" for key press event
        sequence.append(f"{KEYCODES[key]}:1")

    # Release all keys in reverse order (essential for proper modifier key handling)
    for key in reversed(keys):
        # Format as "keycode:0" for key release event
        sequence.append(f"{KEYCODES[key]}:0")

    # Give ydotool daemon time to wake up from idle state
    # First command after idle needs a moment to initialize properly
    subprocess.run([YDOTOOL_PATH, "key", "29:1", "29:0"])  # Press and release CTRL key (truly harmless)
    time.sleep(0.05)  # Small delay to ensure completion
    subprocess.run([YDOTOOL_PATH, "key"] + sequence)

    # DEBUGGING TIP:
    # If hotkeys aren't working, try running this manually:
    # ydotool key 29:1 46:1 46:0 29:0  # Ctrl+C example
    # This helps verify that ydotool is working and the keycodes are correct

def hk_terminal():
    """Open a new terminal window using the standard Linux desktop hotkey.

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

    Note:
        This is preferred over direct terminal commands because it uses the
        desktop environment's configured default rather than hardcoding a
        specific terminal emulator.
    """
    # Send the standard Linux terminal hotkey combination
    # This is recognized by virtually all Linux desktop environments
    hot_keys("CTRL", "ALT", "T")

    # PERFORMANCE NOTE:
    # Hotkey simulation is faster than process discovery and launching
    # The desktop environment handles terminal selection and configuration

def hk_copy():
    """Copy selected text to clipboard using Ctrl+C hotkey.

    Simple demonstration of the hot_keys function that sends the standard
    copy-to-clipboard keyboard shortcut.

    Note:
        This is a basic example of hotkey usage. The selected text in the
        currently focused application will be copied to the system clipboard.
    """
    hot_keys("CTRL", "C")

# 5. Open VSCode application with a given project path
def open_vscode(project_path):
    """Create a function that opens Visual Studio Code with a specific project.

    This function returns a callable that opens VSCode, waits for initialization,
    then automatically opens the integrated terminal for immediate development use.

    Args:
        project_path (str): Absolute path to the project directory to open

    Returns:
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

    Note:
        Uses lambda for inline definition. For complex workflows, a dedicated
        function would be more maintainable.
    """
    return lambda: (
        # Launch VSCode with the project path as argument
        # VSCode will open the directory and load workspace settings
        subprocess.Popen(["code", project_path]),

        # Wait for VSCode to fully initialize before sending hotkeys
        # This prevents the terminal hotkey from being ignored
        time.sleep(2),

        # Open VSCode integrated terminal using Ctrl+` (grave/backtick)
        # This provides immediate access to command line in project context
        hot_keys("CTRL", "GRAVE")
    )

    # PERFORMANCE OPTIMIZATION OPPORTUNITIES:
    # - Check if VSCode is already running and has the project open
    # - Use VSCode's command line API to open terminal directly
    # - Make delay configurable based on system performance
    # - Use VSCode extensions API for more precise control
    #
    # ALTERNATIVE APPROACHES:
    # - Use VSCode's --command flag: code --command workbench.action.terminal.new
    # - Use VSCode's remote development features for containerized projects
    # - Integrate with VSCode's workspace API for session management

# 6. Type text and snippets
def type_text(text):
    """Create a function that types the specified text using ydotool.

    This function returns a callable that simulates typing the given text into
    the currently focused application using ydotool for low-level input events.

    Args:
        text (str): The text to type when the returned function is called

    Returns:
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

    Raises:
        RuntimeError: If actions module not initialized
    """
    def execute():
        # Verify module has been properly initialized
        if YDOTOOL_PATH is None:
            raise RuntimeError("Actions module not initialized. Call initialize_actions() from main first.")

        # Execute ydotool command to type the text
        # Arguments:
        # - YDOTOOL_PATH: Path to ydotool executable
        # - "type": ydotool subcommand for typing text
        # - "--": Indicates end of options, prevents text starting with "-" being interpreted as flags
        # - text: The actual text to type
        subprocess.Popen([YDOTOOL_PATH, "type", "--", text])

        # ALTERNATIVE TOOLS CONSIDERED:
        # - xdotool: More mature but X11-only, doesn't work on Wayland
        # - PyAutoGUI: Cross-platform but has dependency issues and less precise timing
        # - Direct X11/Wayland APIs: More complex and platform-specific
        # - Clipboard + Ctrl+V: Faster for large text but modifies clipboard state

    return execute  # Return the inner function for later execution

def type_keyring():
    """Type the configured password followed by Enter key.

    This function types the password stored in the KEYRING_PW configuration
    variable, followed by a newline character to submit forms or authenticate.

    Returns:
        callable: Function that types the password when called

    Security Note:
        The password is stored in environment variables via config.env.
        While more secure than hardcoding, consider using proper password
        managers for production systems.

    Raises:
        RuntimeError: If KEYRING_PW not configured in initialization
    """
    if KEYRING_PW is None:
        raise RuntimeError("KEYRING_PW not initialized. Call initialize_actions() from main first.")
    return type_text(KEYRING_PW + "\n")

def type_snippet(snippet_name):
    """
    Create a function that inserts a code snippet from a text file.

    This function loads a code snippet from the snippets directory and types it
    into the currently focused application. Snippets are stored as .txt files
    and can contain boilerplate code, templates, commonly used commands, etc.

    Args:
        snippet_name (str): Name of the snippet file (without .txt extension)

    Returns:
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
    """
    def execute():
        # Verify required configuration is available
        if SNIPPETS_DIR is None or YDOTOOL_PATH is None:
            raise RuntimeError("Actions module not initialized. Call initialize_actions() from main first.")

        # Construct path to snippet file
        snippet_path = os.path.join(SNIPPETS_DIR, snippet_name + ".txt")

        # Check if snippet file exists before trying to read it
        if not os.path.exists(snippet_path):
            print(f"Warning: Snippet '{snippet_name}' not found at {snippet_path}")
            return  # Exit early without typing anything

        # Read snippet content from file
        # Using context manager (with statement) ensures file is properly closed
        try:
            with open(snippet_path, "r", encoding="utf-8") as f:
                snippet_content = f.read()
        except IOError as e:
            print(f"Error reading snippet file {snippet_path}: {e}")
            return

        # Type the snippet content using ydotool
        # Same approach as type_text() function
        subprocess.Popen([YDOTOOL_PATH, "type", "--", snippet_content])

        # DESIGN DECISION: File-based storage vs Database
        # We use text files instead of a database because:
        # 1. SIMPLICITY: Easy to edit snippets with any text editor
        # 2. VERSION CONTROL: Can track snippet changes in git
        # 3. PORTABILITY: No database setup required
        # 4. TRANSPARENCY: Users can see exactly what will be typed

    return execute  # Return the execution function

# 7. Open obsidian with a given vault path
def open_obsidian(vault_path):
    """
    Create a function that opens Obsidian with a specific vault.

    This function implements smart window management - it first checks if Obsidian
    is already open with the target vault, and if so, brings it to focus instead
    of opening a new instance. This prevents window clutter and improves UX.

    Args:
        vault_path (str): Path to the Obsidian vault directory

    Returns:
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
    """
    # Extract vault name from the full path for window matching and URI construction
    # os.path.normpath() removes trailing slashes, os.path.basename() gets final component
    vault_name = os.path.basename(os.path.normpath(vault_path))

    def wrapper():
        # STEP 1: Check if Obsidian is already open with this vault
        try:
            # Use wmctrl to list all open windows with their titles
            # wmctrl -l output format: window_id desktop_num client_machine window_title
            wmctrl_output = subprocess.check_output(["wmctrl", "-l"], text=True)

            # Search through each window to find Obsidian with our vault
            for line in wmctrl_output.splitlines():
                # Look for lines containing both "Obsidian" and our vault name
                # This matches window titles like "Obsidian - vault_name" or "vault_name - Obsidian"
                if "Obsidian" in line and vault_name in line:
                    # Extract window ID (first column in wmctrl output)
                    window_id = line.split()[0]  # Format: 0x01234567

                    # Activate the existing window (bring to front and focus)
                    # wmctrl flags: -i (use window ID), -a (activate window)
                    subprocess.run(["wmctrl", "-i", "-a", window_id])
                    return  # Exit early - we found and activated the window

        except subprocess.CalledProcessError:
            # wmctrl command failed (maybe not installed, or no X11 session)
            # Continue to launch new instance - this is not a critical error
            pass

        # STEP 2: No existing window found, launch new Obsidian instance
        # Use Obsidian's URI scheme for clean vault opening
        # Format: obsidian://open?vault=vault_name
        uri = f"obsidian://open?vault={vault_name}"

        # Use xdg-open to handle the URI scheme
        # xdg-open is the standard Linux way to open files/URIs with default applications
        subprocess.Popen(["xdg-open", uri])

        # ALTERNATIVE LAUNCH METHODS CONSIDERED:
        # - Direct obsidian command: obsidian --vault /path/to/vault
        # - Flatpak: flatpak run md.obsidian.Obsidian --vault /path/to/vault
        # - AppImage: ./Obsidian.AppImage --vault /path/to/vault
        #
        # URI scheme approach is preferred because:
        # - Works regardless of Obsidian installation method
        # - Handled by system's default application launcher
        # - More reliable across different Linux distributions

    return wrapper  # Return the wrapper function for later execution

    # PERFORMANCE CONSIDERATIONS:
    # - wmctrl window search is fast (typically <10ms)
    # - URI opening is handled by desktop environment, also fast
    # - Could cache window list to avoid repeated wmctrl calls
    # - Could implement window title fuzzy matching for better reliability

# 8. Execute bash scripts for automating stuff
def execute_bash(bash_script, *args, in_terminal=False):
    """
    Arguments are optional
    in_terminal=True when scripts need to be run in terminal for interactivity
    """
    # Verify module initialization
    def wrapper():
        # Verify module initialization
        if BASHSCRIPTS_DIR is None:
            raise RuntimeError("Actions module not initialized. Call initialize_actions() from main first.")

        # Execute the jarvis environment setup script
        # os.path.join() provides cross-platform path construction
        script_path = os.path.join(BASHSCRIPTS_DIR, bash_script)
        # Check if script exists
        if not os.path.exists(script_path):
            #print(f"Script not found: {script_path}")
            return

        # Auto-fix permissions if not executable.
        if not os.access(script_path,os.X_OK):
            try:
                # The bash script should be executable (chmod +x)
                os.chmod(script_path,0o755)  # rwxr-xr-x permissions
                #print(f"Made script executable: {script_path}")
            except Exception as e:
                #print(f"Failed to make script executable: {e}")
                return

        # Execute the script with arguments
        try:
            if in_terminal:
                # Build command for terminal execution
                cmd_str = f"bash '{script_path}'"
                if args:
                    escaped_args = [f"'{arg}'" for arg in args]
                    cmd_str += " " + " ".join(escaped_args)
                subprocess.Popen([
                    "gnome-terminal", "--", "bash", "-c", cmd_str
                ])
            else:
                # Direct execution
                cmd = [script_path] + list(args)
                subprocess.Popen(cmd)
        except Exception as e:
            print(f"Failed to execute script: {e}")

    return wrapper()

def terminal_env_jarvis():
    """Open a terminal with jarvis/busybee conda environment activated.

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

    Note:
        The script file must exist in the configured BASHSCRIPTS_DIR.
    """
    execute_bash("open_jarvisbusybee_env_T.sh")

def terminal_env_busybee():
    """Open a terminal with busybee conda environment activated.

    Similar to terminal_env_jarvis() but specifically for the busybee project
    environment. Executes the "open_busybee_env_T.sh" script.

    Note:
        See terminal_env_jarvis() for detailed workflow explanation.
    """
    execute_bash("open_busybee_env_T.sh")

def defaultbranch_commit():
    """
    Executes a git commit workflow using a bash script with interactivity.
    That is why in_terminal=True.
    Takes 'PROJECTS_DIR' as an argument
    Prompts user for project name, then navigates to PROJECTS_DIR/PROJECT_NAME
    and runs git status, git add ., and git commit with user prompts between each step.
    User can exit at any point using CTRL+C.
    """
    execute_bash("git_commit_workflow.sh", PROJECTS_DIR, in_terminal=True)

# 9. Open nautilus windows with a target path. If that path is already open in another window, simply raise it, to avoid multiple nautilus windows with the same path..... which happens often if this check is not in place before opening the window
def nautilus_path(target_dir):
    """
    I want this function to open file manager windows or raise them if there is
    already one open with my target directory. Instead of always opening a new Nautilus window,
    I will first check if there is already one open with my target directory.
    If there is, I will just bring it to the front (raise it).
    This prevents window clutter and gives me a better user experience. :)
    """

    # I need to convert the target directory to an absolute path because:
    # 1. Relative paths like "../folder" or "./folder" can be ambiguous
    # 2. os.path.abspath() converts these to full paths like "/home/user/folder"
    # 3. This ensures I am comparing the same format when checking window titles later
    # 4. It also resolves any symbolic links to their actual paths
    #    (Symbolic links are like shortcuts - they point to another file/directory.
    #     os.path.abspath() follows the shortcut to get the real location)
    target_dir = os.path.abspath(target_dir)

    # STEP 1: I need to check if Nautilus is already open with my target directory

    # wmctrl is a command-line tool that lets me interact with X11 windows in Linux
    # The "-lx" flags mean:
    # -l: list all windows
    # -x: include the WM_CLASS property (this helps me identify the application type)
    #
    # subprocess.check_output() runs this command and captures its text output
    # text=True ensures I get a string back instead of bytes
    wmctrl_output = subprocess.check_output(["wmctrl", "-lx"], text=True)

    # The wmctrl output looks like this (one line per window):
    # 0x02400003  0 org.gnome.Nautilus.org.gnome.Nautilus desktop file-browser - /home/user/Documents
    # 0x02600004  0 firefox.Firefox          desktop Firefox
    #
    # Each line contains: window_id, desktop_number, WM_CLASS, hostname, window_title
    # I need to parse each line to extract the information I need
    for line in wmctrl_output.splitlines():
        # I only care about Nautilus windows, so I check if "org.gnome.Nautilus"
        # is in the line. This is the WM_CLASS identifier for Nautilus windows.
        if "org.gnome.Nautilus" in line:

            # Now I need to extract the window ID and title from this line
            # line.split() breaks the line into parts separated by whitespace
            # The window ID is always the first part (index 0)
            # Example: "0x02400003" from the line above
            window_id = line.split()[0]

            # The window title starts from the 4th element (index 3) onwards
            # I use " ".join() to put the title back together with spaces
            # because the title might contain spaces that were split apart
            # Example: from "desktop file-browser - /home/user/Documents"
            # I want "file-browser - /home/user/Documents"
            window_title = " ".join(line.split()[3:])

            # Now I need to check if this Nautilus window is showing my target directory
            # There are different ways the directory might appear in the window title:

            # First, I get just the folder name (last part of the path)
            # os.path.basename("/home/user/Documents") returns "Documents"
            # This helps me match windows that might not show the full path
            folder_name = os.path.basename(target_dir)

            # I check three conditions to see if this window matches my target:
            if (target_dir in window_title or          # Full path is in title
                folder_name in window_title or        # Just folder name is in title
                window_title.endswith(folder_name)):  # Title ends with folder name

                # I found a matching window! Instead of opening a new one,
                # I will bring this existing window to the front (raise it)
                # print(f"Raising existing Nautilus window for {target_dir}")

                # wmctrl can also control windows, not just list them
                # -i: "use window ID" - I am giving it a window ID number (0x02400003)
                # instead of a window title/name (more reliable than titles)
                # -a: "activate window" - bring the window to front and give it focus
                # (like clicking on it in the taskbar)
                # window_id: the window ID I extracted earlier (like 0x02400003)
                subprocess.run(["wmctrl", "-i", "-a", window_id])

                # I found and raised the window, so I am done - return early
                # This prevents the function from continuing to Step 2
                return

    # STEP 2: If I get here, it means I did not find any existing Nautilus window
    # with my target directory, so I need to open a new one

    # print(f"Opening new Nautilus at {target_dir}")

    # subprocess.Popen() starts a new process without waiting for it to finish
    # This is perfect for GUI applications because:
    # 1. I don't want my Python script to hang waiting for Nautilus to close
    # 2. The user should be able to use Nautilus independently
    # 3. My script can continue with other tasks
    #
    # I pass the target directory as an argument to nautilus so it opens there
    subprocess.Popen(["nautilus", target_dir])



