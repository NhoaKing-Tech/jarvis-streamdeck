"""
Main entry point for the Jarvis StreamDeck application.

This module serves as the primary entry point and delegates to the core
application logic in core.application.

Usage:
    python -m jarvis              # Run from project root

This is executed when:
    - Running via command line: python -m jarvis
    - Running via systemd service: main.sh calls python -m jarvis
    - Running via alias: jarvis-test uses python -m jarvis
"""

from jarvis.core.application import main

if __name__ == "__main__":
    main()
