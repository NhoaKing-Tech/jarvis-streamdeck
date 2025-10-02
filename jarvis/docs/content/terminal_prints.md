---
title: terminal_prints
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-21
---

# terminal_prints

-- GENERAL INFORMATION --
AUTHOR: NhoaKing
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: terminal_prints.py
-- DESCRIPTION --
This script provides functions for printing styled messages to the terminal to enhance console formatting.
This is used in the setup_config.py script. I will likely use it in other scripts as well, for example in the git_commit_workflow.sh script.

## Classes

- [[#TerminalStyles|TerminalStyles]]

## Functions

- [[#print_information_type|print_information_type()]]

## TerminalStyles

```python
class TerminalStyles:
```

ANSI color codes and styles for terminal output styling.

## print_information_type

```python
def print_information_type():
```

Print information with styling based on the information type specified.

**Args:**
    info_type: Type of information ("error", "warning", "success", "info", "title", "step", "progress", "detail").
        If the info_type is not recognized, it defaults to plain text output with no special styling.
    message: The message to print.
    **kwargs: Additional (optional) argument box to provide parameters (that are specific to certain information types) like:
                - color: Custom color for all message types (in case we want to override the default color for an information type).
                - step_number: Step number for "step" type. If not provided, defaults to 1.
                - prefix: Custom prefix for "progress" and "detail" types. If not provided, defaults to '+' for "progress" and '-' for "detail".
                - border_char: Border character for "title" type. If not provided, defaults to '='.
                - width: Border width for "title" type. If not provided, defaults to 70 characters.

**Returns:** 
    None (it prints directly to the terminal as the function executes)

## Additional Code Context

Other contextual comments from the codebase:

- **Line 14:** Colors (a bunch I will likely never use, but still nice to have them here)
- **Line 27:** Text styles (bold, underline, etc.)
- **Line 52:** Normalize to lowercase for consistency, in case I mess up the info_type label
- **Line 54:** TITLE label: displayed with top and bottom borders, in bold, and optionally in a custom color (otherwise blue by default)
- **Line 57:** Default border character is '='
- **Line 58:** Default width of 70 characters
- **Line 68:** ERROR label: includes borders for emphasis, it is displayed in red and includes the "ERROR" keyword at the start of the print
- **Line 78:** WARNING label: displayed in yellow with a "WARNING" keyword at the start of the print, in bold letters
- **Line 79:** and optionally in a custom color (otherwise yellow by default)
- **Line 84:** SUCCESS label: displayed in green with a "SUCCESS" keyword at the start of the print, in bold letters
- **Line 85:** and optionally in a custom color (otherwise green by default)
- **Line 90:** INFO label: displayed in blue with an "INFO" keyword at the start of the print, in bold letters
- **Line 91:** and optionally in a custom color (otherwise blue by default)
- **Line 96:** STEP label: displayed in bold with the step_number as especified at the start of the print,
- ... and 8 more contextual comments
