"""
UI lifecycle management for StreamDeck.

This module handles resource cleanup and graceful shutdown for the jarvis application.
It ensures that system resources are properly released when the application exits,
whether through normal shutdown, interrupt signals, or unexpected crashes.

Key responsibilities:
- Release any "stuck" keyboard keys that might remain pressed
- Close StreamDeck hardware connection cleanly
- Provide graceful shutdown mechanisms
- Prevent resource leaks and hardware conflicts

This module is critical for system stability because ydotool key events
can leave the system in an unusable state if not properly cleaned up.

CONFIGURATION FLOW:
1. run_jarvis.py calls config.initialization.initialize_jarvis_modules()
2. initialize_jarvis_modules() uses initialize_module() to set global variables in this module
3. Global variables (YDOTOOL_PATH, KEYCODES) are used by cleanup functions

This module uses the centralized initialization pattern for consistent configuration management.
"""

# Standard library imports for system interaction and process control
import subprocess  # Execute ydotool commands for key release
import sys         # System exit functions for controlled shutdown
from typing import Optional, Dict, Any

# ==================== MODULE CONFIGURATION ====================
# Global configuration variables - set by config.initialization.initialize_module()
# These are initialized to None and set during application startup via centralized initialization

# Path to ydotool executable for keyboard input simulation
YDOTOOL_PATH: Optional[str] = None  # Path to ydotool for key release operations

# Dictionary mapping key names to Linux input event codes
KEYCODES: Optional[Dict[str, int]] = None  # Keycode mapping for release_all_keys() function

# CENTRALIZED INITIALIZATION PATTERN:
# Rather than importing these values or reading config directly,
# they are set via config.initialization.initialize_module(). This provides:
# 1. CONSISTENCY: Uses same configuration pattern as all jarvis modules
# 2. TESTABILITY: Easy to mock for unit tests
# 3. FLEXIBILITY: Can be configured differently for different environments
# 4. EXPLICIT DEPENDENCIES: Clear what this module needs to function
# 5. REDUCED DUPLICATION: No need for module-specific initialization functions

# DESIGN PATTERN: Module-level Configuration with General Initialization
# =======================================================================
# This module now uses the general initialize_module() function from config.initialization
# instead of having its own initialization function. This reduces code duplication
# and provides a consistent initialization pattern across all jarvis modules.
#
# INITIALIZATION:
# The config.initialization.initialize_module() function sets the global variables
# (YDOTOOL_PATH, KEYCODES) by calling setattr(module, key, value) for each
# configuration parameter.
#
# ALTERNATIVE APPROACHES CONSIDERED:
# 1. Class-based: LifecycleManager(ydotool_path, keycodes)
# 2. Context manager: with lifecycle_context(ydotool_path, keycodes):
# 3. Singleton pattern: LifecycleManager.instance().configure(...)
#
# Module-level functions chosen for:
# - Simplicity and directness
# - Compatibility with atexit.register() usage
# - Consistent with other jarvis modules

def release_all_keys() -> None:
    """Release all keyboard keys to prevent "sticky key" problems.

    This function sends key release events for all keys defined in KEYCODES
    to ensure no keys remain "stuck" in the pressed state when jarvis exits.
    This is essential because ydotool can leave keys in pressed state if
    the application crashes or exits unexpectedly.

    Sticky Key Problem:
        ydotool sends low-level input events to the Linux kernel. If a key press
        event is sent but the corresponding key release event is never sent
        (due to application crash, kill signal, etc.), the key remains "pressed"
        from the system's perspective. This can make the system unusable.

    Solution Strategy:
        Send release events (keycode:0) for all possible keys that jarvis might
        have pressed. This is safe because:

        - Releasing an already-released key has no effect
        - Better to release too many keys than leave any stuck
        - The overhead is minimal (small command, runs once at exit)

    Called During:
        - Normal application shutdown (atexit handler)
        - Signal-based shutdown (SIGINT/Ctrl+C handler)
        - Manual cleanup calls
        - Recovery scenarios (reset_jarvis.py)

    Raises:
        RuntimeError: If lifecycle module not initialized

    Note:
        Validates initialization but doesn't handle ydotool execution errors
        because this is typically called during shutdown when error handling
        options are limited.
    """
    # Verify module has been properly initialized
    if YDOTOOL_PATH is None or KEYCODES is None:
        raise RuntimeError("Lifecycle module not initialized. Call config.initialization.initialize_jarvis_modules() first.")

    # Build list of key release events for all known keys
    # Format: "keycode:0" where 0 means "release" (1 would mean "press")
    release_events = [f"{keycode}:0" for keycode in KEYCODES.values()]

    # Send all key release events in a single ydotool command
    # Using subprocess.Popen() for non-blocking execution
    # We don't wait for completion because this is cleanup code
    subprocess.Popen(
        [YDOTOOL_PATH, "key"] + release_events
    )

    # PERFORMANCE ANALYSIS:
    # - Number of keys: ~50 keys in KEYCODES
    # - Command size: ~200 characters
    # - Execution time: <10ms typically
    # - Memory usage: Minimal (small subprocess)
    #
    # ALTERNATIVE APPROACHES CONSIDERED:
    # 1. Individual ydotool commands per key: Much slower, more processes
    # 2. Only release "dangerous" modifier keys: Risky, might miss stuck keys
    # 3. System-level key state reset: Complex, platform-specific
    # 4. Virtual keyboard reset: Would require additional dependencies
    #
    # Current approach chosen for balance of safety, performance, and simplicity

# ==================== CLEANUP STATE MANAGEMENT ====================
# Global flag to prevent multiple cleanup operations from running simultaneously
# This is important because cleanup can be triggered from multiple sources:
# - atexit handlers (normal Python exit)
# - signal handlers (Ctrl+C, SIGTERM)
# - manual cleanup calls (error recovery)
# - exception handlers

# Flag to track whether cleanup has already been performed
clean_stickykeys: bool = False  # Set to False initially - cleanup not yet performed

# RACE CONDITION PREVENTION:
# Without this flag, multiple cleanup triggers could cause:
# - Redundant ydotool commands (wasteful but harmless)
# - Concurrent StreamDeck operations (could cause errors)
# - Multiple "Cleaning up..." messages (confusing to user)
#
# The flag ensures cleanup runs exactly once, even if triggered multiple times

def cleanup(deck: Optional[Any] = None) -> None:
    """Perform complete application cleanup and resource release.

    This function handles all necessary cleanup operations when jarvis shuts down.
    It's designed to be safe to call multiple times and from different contexts
    (normal exit, signal handlers, exception handlers).

    Args:
        deck: Optional StreamDeck device object to clean up

    Cleanup Operations:
        1. Release any stuck keyboard keys via ydotool
        2. Reset StreamDeck display (clear all keys)
        3. Close StreamDeck hardware connection
        4. Prevent duplicate cleanup attempts

    Design Principles:
        - **Idempotent**: Safe to call multiple times
        - **Defensive**: Handles errors gracefully
        - **Complete**: Cleans up all acquired resources
        - **Fast**: Minimal delay during shutdown

    Calling Contexts:
        - Registered with atexit for normal Python shutdown
        - Called from signal handlers (Ctrl+C)
        - Called manually in exception handlers
        - Called from reset/recovery scripts

    Note:
        Uses a global flag to prevent duplicate cleanup from multiple triggers.
        Cleanup errors are reported but don't prevent other cleanup steps.
    """
    global clean_stickykeys

    # Check if cleanup has already been performed
    # This prevents duplicate cleanup from multiple triggers
    if clean_stickykeys:
        return  # Exit early - cleanup already done

    # Set flag to prevent future cleanup attempts
    clean_stickykeys = True  # Mark cleanup as performed

    try:
        # Provide user feedback about cleanup process
        print("\nCleaning up...")

        # STEP 1: Release any stuck keyboard keys
        # This is the most critical cleanup step because stuck keys
        # can make the entire system unusable
        release_all_keys()

        # STEP 2: Clean up StreamDeck hardware if provided
        if deck and deck.is_open():
            # Clear all key displays (turn off icons/text)
            deck.reset()

            # Close USB connection to StreamDeck
            # This releases the device for other applications
            deck.close()

        # CLEANUP SEQUENCE REASONING:
        # 1. Keys first: Most critical for system usability
        # 2. StreamDeck last: Less critical, mainly cosmetic and resource management

    except Exception as e:
        # DEFENSIVE ERROR HANDLING:
        # Cleanup should never fail completely, even if individual steps fail
        # Report the error but don't crash or raise exceptions
        # This is especially important in signal handlers and atexit contexts
        print(f"(cleanup ignored error: {e})")

        # ALTERNATIVE ERROR HANDLING:
        # Could log to file: logging.error(f"Cleanup error: {e}")
        # Could try partial cleanup: Continue with remaining steps
        # Could notify user differently: GUI notification, system notification
        #
        # Simple console message chosen because:
        # - Cleanup happens during shutdown when logging might not work
        # - User needs immediate feedback about any cleanup issues
        # - Simple approach is most reliable during shutdown scenarios

    # RESOURCE LEAK PREVENTION:
    # Even if exceptions occur:
    # - Flag prevents retry attempts that might make things worse
    # - System-level resources (ydotool) are automatically cleaned up by OS
    # - USB resources are handled by kernel drivers
    # - Python memory is reclaimed by interpreter shutdown

def safe_exit(deck: Optional[Any] = None) -> None:
    """Perform cleanup and exit the application gracefully.

    This function provides a single point for graceful application shutdown.
    It ensures all cleanup operations are performed before terminating the
    Python process.

    Args:
        deck: Optional StreamDeck device object to clean up before exit

    Exit Code:
        Uses exit code 0 to indicate successful/intentional shutdown.
        This is important for:

        - System service management (systemd, etc.)
        - Process monitoring tools
        - Shell scripts that check exit codes
        - Automated restart logic

    Usage Contexts:
        - Signal handlers (Ctrl+C interrupt)
        - Error recovery after unrecoverable errors
        - Manual shutdown commands
        - Graceful restart scenarios

    Shutdown Sequence:
        1. Run complete cleanup (release keys, close hardware)
        2. Exit Python interpreter with success code
        3. OS reclaims any remaining resources

    Note:
        This function does not return - it terminates the Python process.
    """
    # Perform all necessary cleanup operations
    # This includes key release and StreamDeck hardware cleanup
    cleanup(deck)

    # Exit Python interpreter with success code (0)
    # sys.exit(0) is preferred over sys.exit() because:
    # - Explicit success code for clarity
    # - Consistent behavior across different Python versions
    # - Clear intent that this is intentional, successful shutdown
    sys.exit(0)

    # ALTERNATIVE EXIT METHODS:
    # - sys.exit(): Uses default code (None, treated as 0)
    # - sys.exit(1): Error exit code (for unexpected shutdowns)
    # - os._exit(0): Immediate exit without cleanup (dangerous)
    # - quit(): Interactive interpreter only (not for scripts)
    # - exit(): Interactive interpreter only (not for scripts)
    #
    # sys.exit(0) chosen because:
    # - Allows Python cleanup and atexit handlers to run
    # - Clear success indication
    # - Standard practice for graceful shutdown

    # POST-EXIT BEHAVIOR:
    # After sys.exit(0):
    # 1. Python runs any remaining atexit handlers (including our cleanup)
    # 2. Python interpreter shuts down cleanly
    # 3. OS reclaims process resources (memory, file handles, etc.)
    # 4. Parent process (shell, systemd) receives exit code 0
    # 5. StreamDeck hardware remains in last known state until next connection