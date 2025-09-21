"""
-- GENERAL INFORMATION --
AUTHOR: NhoaKing (pseudonym for privacy)
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: terminal_prints.py
-- DESCRIPTION --
This script provides functions for printing styled messages to the terminal to enhance console formatting.
"""

class TerminalStyles:
    """ANSI color codes and styles for terminal output styling."""

    # Colors (a bunch I will likely never use but whatever)
    RED = '\033[91m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    ORANGE = '\033[38;5;208m'
    PURPLE = '\033[38;5;129m'
    PINK = '\033[38;5;213m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'
    WHITE = '\033[97m'

    # Text styles (bold, underline, etc.)
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    ITALIC = '\033[3m'

    # Reset
    RESET = '\033[0m'

def print_information_type(info_type: str, message: str, **kwargs) -> None:
    """Print information with styling based on the type specified.

    Args:
        info_type: Type of information ("error", "warning", "success", "info",
                  "title", "step", "progress", "detail")
        message: The message to print
        **kwargs: Additional (optional) argument box to provide parameters 
        (that are specific to certain informaiton types) like:
                    - color: Custom color for all message types (overrides default colors)
                    - step_number: Step number for "step" type
                    - prefix: Custom prefix for "progress" and "detail" types
                    - border_char: Border character for "title" type
                    - width: Border width for "title" type
    Returns: None (it prints directly to the terminal as the function executes)
    """
    info_type = info_type.lower() # Normalize to lowercase for consistency, in case I mess up the info_type label

    # TITLE label: displayed with top and bottom borders, in bold, and optionally in a custom color (otherwise blue by default)
    if info_type == "title":
        color = kwargs.get('color', TerminalStyles.BLUE)
        border_char = kwargs.get('border_char', '=') # Default border character is '='
        width = kwargs.get('width', 70) # Default width of 70 characters
        border = border_char * width
        print(f"{color}{TerminalStyles.BOLD}")
        print(border)
        print(message)
        print(border)
        print(f"{TerminalStyles.RESET}")

    # ERROR label: includes borders for emphasis, it is displayed in red and includes the "ERROR" keyword at the start of the print
    elif info_type == "error":
        color = kwargs.get('color', TerminalStyles.RED)
        border = "=" * 70
        print(f"{color}{TerminalStyles.BOLD}")
        print(border)
        print(f"ERROR: {message}")
        print(border)
        print(f"{TerminalStyles.RESET}")

    # WARNING label: displayed in yellow with a "WARNING" keyword at the start of the print, in bold letters
    # and optionally in a custom color (otherwise yellow by default)
    elif info_type == "warning":
        color = kwargs.get('color', TerminalStyles.YELLOW)
        print(f"{color}{TerminalStyles.BOLD}WARNING: {TerminalStyles.RESET}{color}{message}{TerminalStyles.RESET}")

    # SUCCESS label: displayed in green with a "SUCCESS" keyword at the start of the print, in bold letters
    # and optionally in a custom color (otherwise green by default)
    elif info_type == "success":
        color = kwargs.get('color', TerminalStyles.GREEN)
        print(f"{color}{TerminalStyles.BOLD}SUCCESS: {TerminalStyles.RESET}{color}{message}{TerminalStyles.RESET}")

    # INFO label: displayed in blue with an "INFO" keyword at the start of the print, in bold letters
    # and optionally in a custom color (otherwise blue by default)
    elif info_type == "info":
        color = kwargs.get('color', TerminalStyles.WHITE)
        print(f"{color}{TerminalStyles.BOLD}INFO: {TerminalStyles.RESET}{color}{message}{TerminalStyles.RESET}")

    # STEP label: displayed in bold with the step_number as especified at the start of the print, 
    # and optionally in a custom color (otherwise blue by default)
    elif info_type == "step":
        color = kwargs.get('color', TerminalStyles.BLUE)
        step_number = kwargs.get('step_number', 1) # Default step number is 1 if not provided
        print(f"{color}{TerminalStyles.BOLD}{step_number}. {message}{TerminalStyles.RESET}")

    # DETAIL label: displayed with a prefix at the start of the print, and optionally in a custom color (otherwise blue by default)
    elif info_type == "detail":
        prefix = kwargs.get('prefix', '-') # Default prefix is '-' if not provided
        color = kwargs.get('color', TerminalStyles.BLUE) # Default color is blue if not provided
        print(f"{color}{prefix} {message}{TerminalStyles.RESET}")

    # PROGRESS label: displayed in green with a prefix at the start of the print, and optionally in a custom color (otherwise green by default)
    elif info_type == "progress":
        color = kwargs.get('color', TerminalStyles.GREEN)
        prefix = kwargs.get('prefix', '+') # Default prefix is '+' if not provided
        print(f"{color}{prefix} {message}{TerminalStyles.RESET}")

    else:
        # Default to plain text in case type not recognized, to handle errors gracefully
        print(message)
