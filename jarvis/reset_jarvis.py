#!/usr/bin/env python3
"""Emergency reset script for jarvis StreamDeck application.

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
"""

import sys
import subprocess
import os
from StreamDeck.DeviceManager import DeviceManager
from pathlib import Path
from typing import Dict

def load_config() -> None:
    """Load configuration from config.env file for reset operations.

    This function reads the same configuration file used by the main jarvis
    application to ensure reset operations use the correct tool paths and
    settings.

    Note:
        Uses the same configuration loading logic as the main application
        to maintain consistency in tool paths and settings.
    """
    config_path = Path(__file__).parent / "config.env"
    if config_path.exists():
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Load configuration immediately when module is imported
# This ensures configuration is available for all reset operations
load_config()

# Tool path configuration with fallback to system PATH
# Uses same configuration approach as main jarvis application
YDOTOOL_PATH: str = os.getenv('YDOTOOL_PATH', 'ydotool')  # Path to ydotool for key release operations

# Optional: same KEYCODES dictionary from your workflow
KEYCODES: Dict[str, int] = {
    "CTRL": 29, "SHIFT": 42, "ALT": 56, "SUPER": 125,
    "C": 46, "V": 47,  # add more if needed
}

def release_all_keys() -> None:
    """Release all potentially stuck keyboard keys.

    This function sends key release events for common keys that might be
    stuck in pressed state after a jarvis crash or unexpected exit.

    Keys Released:
        Common modifier and control keys that could cause system issues
        if left in pressed state.

    Note:
        Uses ydotool to send low-level key release events. Safe to call
        even if keys are not actually stuck.
    """
    releases = [f"{code}:0" for code in KEYCODES.values()]
    subprocess.run(
        [YDOTOOL_PATH, "key"] + releases,
        check=False
    )

def reset_all_streamdecks() -> None:
    """Reset all connected StreamDeck devices to blank state.

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

    Note:
        Reports success/failure for each device found.
    """
    decks = DeviceManager().enumerate()
    if not decks:
        print("No Stream Decks found.")
        return

    for deck in decks:
        try:
            deck.open()
            deck.reset()
            deck.close()
            print(f"✅ Reset Stream Deck: {deck.id()}")
        except Exception as e:
            print(f"⚠️ Could not reset Stream Deck: {e}")

if __name__ == "__main__":
    """Main execution block for emergency reset operations.

    Performs complete reset sequence:
        1. Release any stuck keyboard keys
        2. Reset all StreamDeck devices
        3. Exit with success status

    Note:
        This block only executes when the script is run directly,
        not when imported as a module.
    """
    print("Releasing any stuck keys...")
    release_all_keys()

    print("Resetting Stream Deck(s)...")
    reset_all_streamdecks()

    print("Done.")
    sys.exit(0)
