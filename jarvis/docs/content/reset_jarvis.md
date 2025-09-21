---
title: reset_jarvis
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-21
---

# reset_jarvis

-- GENERAL INFORMATION --
AUTHOR: NhoaKing (pseudonym for privacy)
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: reset_jarvis.py
-- DESCRIPTION --
This script resets the deck to a clean state.
With this script I can reset the deck if jarvis crashes or becomes unresponsive.
It also works when jarvis.service is stopped with the terminal.
It handles cleanup of both software state and hardware resources without requiring the main
application to be running.

Functions:
- Release any stuck keyboard keys via ydotool
- Reset the stream deck to original state
- Clear application state and hardware connections
- Recover from most error conditions

Usage:
From the jarvis-env run: python reset_jarvis.py

Design:
This script is designed to be completely independent of the main jarvis
application and can recover from most error states, including situations
where the main application has crashed or become unresponsive.

When to Use:
- Keys appear "stuck" after jarvis crash (though this should not happen as this is handled in core.application)
- StreamDeck shows incorrect/frozen display (this happens when the jarvis.service is stopped through the terminal)
- System becomes unresponsive
- Before troubleshooting jarvis problems

## Functions

- [[#load_config|load_config()]]
- [[#release_all_keys|release_all_keys()]]
- [[#reset_streamdeck|reset_streamdeck()]]

## load_config

```python
def load_config():
```

Load configuration from config.env file for reset operations.

This function reads the same configuration file used by the main jarvis
application to ensure reset operations use the correct tool paths and
settings.

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

## reset_streamdeck

```python
def reset_streamdeck():
```

Reset all connected StreamDeck devices to blank state.

This function discovers all connected StreamDeck devices and resets
them to a clean state with no icons or text displayed.

Process:
1. Discover the connected stream deck devices
2. Open connection to my device (I only have one)
3. Reset device display (clear all keys)
4. Close connection cleanly

Error Handling:
Handles individual device errors gracefully, attempting to reset
as many devices as possible even if some fail.

**Note:**
Reports success/failure.

## Additional Code Context

Other contextual comments from the codebase:

- **Line 42:** Letter keys (QWERTY layout positions, not alphabetical)
- **Line 50:** Number row keys (1-9, 0)
- **Line 54:** Function keys (F1-F12)
- **Line 59:** Modifier keys (both left and right variants)
- **Line 60:** Left-side modifiers
- **Line 61:** Right-side modifiers
- **Line 62:** Super/Windows/Cmd key
- **Line 64:** Special keys
- **Line 68:** Navigation keys (arrow keys and related)
- **Line 73:** Symbol/punctuation keys
- **Line 74:** - and = keys
- **Line 75:** [ and ] keys
- **Line 76:** \ and ; keys
- **Line 77:** ' and ` keys
- **Line 78:** , . and / keys
- ... and 6 more contextual comments
