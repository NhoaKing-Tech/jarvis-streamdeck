---
title: reset_jarvis
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-18
---

# reset_jarvis

Emergency reset script for jarvis StreamDeck application.

This script provides emergency reset functionality for when jarvis becomes
unresponsive or leaves the system in an unusable state. It handles cleanup
of both software state and hardware resources without requiring the main
application to be running.

Key Functions:
    - Release any stuck keyboard keys via ydotool
    - Reset all connected StreamDeck devices to blank state
    - Clear application state and hardware connections
    - Recover from most error conditions

Usage:
    python reset_jarvis.py

Design:
    This script is designed to be completely independent of the main jarvis
    application and can recover from most error states, including situations
    where the main application has crashed or become unresponsive.

When to Use:
    - Keys appear "stuck" after jarvis crash
    - StreamDeck shows incorrect/frozen display
    - System becomes unresponsive due to jarvis issues
    - Before troubleshooting jarvis problems

## Functions

- [[#load_config|load_config()]]
- [[#release_all_keys|release_all_keys()]]
- [[#reset_all_streamdecks|reset_all_streamdecks()]]

## load_config

```python
def load_config():
```

Load configuration from config.env file for reset operations.

This function reads the same configuration file used by the main jarvis
application to ensure reset operations use the correct tool paths and
settings.

**Note:**
    Uses the same configuration loading logic as the main application
    to maintain consistency in tool paths and settings.

## release_all_keys

```python
def release_all_keys():
```

Release all potentially stuck keyboard keys.

This function sends key release events for common keys that might be
stuck in pressed state after a jarvis crash or unexpected exit.

Keys Released:
    Common modifier and control keys that could cause system issues
    if left in pressed state.

**Note:**
    Uses ydotool to send low-level key release events. Safe to call
    even if keys are not actually stuck.

## reset_all_streamdecks

```python
def reset_all_streamdecks():
```

Reset all connected StreamDeck devices to blank state.

This function discovers all connected StreamDeck devices and resets
them to a clean state with no icons or text displayed.

Process:
    1. Enumerate all connected StreamDeck devices
    2. Open connection to each device
    3. Reset device display (clear all keys)
    4. Close connection cleanly

Error Handling:
    Handles individual device errors gracefully, attempting to reset
    as many devices as possible even if some fail.

**Note:**
    Reports success/failure for each device found.
