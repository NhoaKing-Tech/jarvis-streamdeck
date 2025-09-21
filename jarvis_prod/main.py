"""
Main entry point for the Jarvis StreamDeck application.

This module serves as the primary entry point and delegates to the core
application logic in core.run_jarvis.

Usage:
    python jarvis/main.py
    python -m jarvis
"""

from core.application import main

if __name__ == "__main__":
    main()