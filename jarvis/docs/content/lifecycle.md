---
title: lifecycle
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-21
---

# lifecycle

-- GENERAL INFORMATION --
AUTHOR: NhoaKing
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: lifecycle.py
-- DESCRIPTION -- 
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
1. core.application calls config.initialization.init_jarvis()
2. init_jarvis() uses init_module() to set global variables in this module
3. Global variables (YDOTOOL_PATH, KEYCODES) are used by cleanup functions

This module uses the centralized initialization pattern for consistent configuration management.

## Functions

- [[#release_all_keys|release_all_keys()]]
- [[#cleanup|cleanup()]]
- [[#safe_exit|safe_exit()]]

## release_all_keys

```python
def release_all_keys():
```

Release all keyboard keys to prevent "sticky key" problems.

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

**Raises:**
    RuntimeError: If lifecycle module not initialized

**Note:**
    Validates initialization but doesn't handle ydotool execution errors
    because this is typically called during shutdown when error handling
    options are limited.

## cleanup

```python
def cleanup():
```

Perform complete application cleanup and resource release.

This function handles all necessary cleanup operations when jarvis shuts down.
It's designed to be safe to call multiple times and from different contexts
(normal exit, signal handlers, exception handlers).

**Args:**
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

**Note:**
    Uses a global flag to prevent duplicate cleanup from multiple triggers.
    Cleanup errors are reported but don't prevent other cleanup steps.

## safe_exit

```python
def safe_exit():
```

Perform cleanup and exit the application gracefully.

This function provides a single point for graceful application shutdown.
It ensures all cleanup operations are performed before terminating the
Python process.

**Args:**
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

**Note:**
    This function does not return - it terminates the Python process.

## Additional Code Context

Other contextual comments from the codebase:

- **Line 30:** Standard library imports for system interaction and process control
- **Line 31:** Execute ydotool commands for key release
- **Line 32:** System exit functions for controlled shutdown
- **Line 35:** ==================== MODULE CONFIGURATION ====================
- **Line 36:** Global configuration variables - set by config.initialization.init_module()
- **Line 37:** These are initialized to None and set during application startup via centralized initialization
- **Line 39:** Path to ydotool executable for keyboard input simulation
- **Line 40:** Path to ydotool for key release operations
- **Line 42:** Dictionary mapping key names to Linux input event codes
- **Line 43:** Keycode mapping for release_all_keys() function
- **Line 45:** CENTRALIZED INITIALIZATION PATTERN:
- **Line 46:** Rather than importing these values or reading config directly,
- **Line 47:** they are set via config.initialization.init_module(). This provides:
- **Line 48:** 1. CONSISTENCY: Uses same configuration pattern as all jarvis modules
- **Line 49:** 2. TESTABILITY: Easy to mock for unit tests
- ... and 118 more contextual comments
