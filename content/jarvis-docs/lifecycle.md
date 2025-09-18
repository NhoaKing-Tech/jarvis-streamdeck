---
title: lifecycle
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-18
---

# lifecycle

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

## Functions

- [[#initialize_lifecycle|initialize_lifecycle()]]
- [[#release_all_keys|release_all_keys()]]
- [[#cleanup|cleanup()]]
- [[#safe_exit|safe_exit()]]

## initialize_lifecycle

```python
def initialize_lifecycle():
```

Initialize the lifecycle module with required configuration.

This function sets up the module with the configuration needed for
cleanup operations. It's called once during application startup to
ensure cleanup tools are available for shutdown scenarios.

**Args:**
    ydotool_path (str): Path to ydotool executable for key operations
    keycodes (dict): Mapping of key names to Linux input event codes

Initialization Timing:
    Called early in the startup sequence, after configuration is loaded
    but before StreamDeck operations begin. This ensures cleanup tools
    are available if needed during startup or shutdown.

Error Handling:
    No validation is performed here because this is called during
    controlled startup with validated config. Invalid configuration
    would be caught during actual cleanup attempts.

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
