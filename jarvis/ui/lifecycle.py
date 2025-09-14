"""
UI lifecycle management for StreamDeck.
This module handles resource cleanup and graceful shutdown.
"""

import subprocess
import sys

# Global state - will be set by the main module
YDOTOOL_PATH = None
KEYCODES = None

def initialize_lifecycle(ydotool_path, keycodes):
    """Initialize the lifecycle module with required configuration."""
    global YDOTOOL_PATH, KEYCODES
    YDOTOOL_PATH = ydotool_path
    KEYCODES = keycodes

def release_all_keys():
    """
    In case of sticky keys, this function releases all keys.
    It is called when the script exits or crashes. Second bug I found with ydotool >.<
    """
    if YDOTOOL_PATH is None or KEYCODES is None:
        raise RuntimeError("Lifecycle module not initialized. Call initialize_lifecycle() first.")

    releases = [f"{code}:0" for code in KEYCODES.values()]
    subprocess.Popen(
        [YDOTOOL_PATH, "key"] + releases
    )

# Flag to prevent multiple cleans of sticky keys. Set to false initially because clean up is not yet performed.
clean_stickykeys = False

def cleanup(deck=None):
    global clean_stickykeys
    if clean_stickykeys:
        return
    clean_stickykeys = True # the flag changes to true as all keys have been released.
    try:
        print("\nCleaning up...")
        release_all_keys()
        if deck and deck.is_open():
            deck.reset()
            deck.close()
    except Exception as e:
        print(f"(cleanup ignored error: {e})")

def safe_exit(deck=None):
    cleanup(deck)
    sys.exit(0)