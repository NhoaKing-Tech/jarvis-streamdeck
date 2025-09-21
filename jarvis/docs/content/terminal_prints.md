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
AUTHOR: NhoaKing (pseudonym for privacy)
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: terminal_prints.py
-- DESCRIPTION --
This script provides functions for printing styled messages to the terminal to enhance console formatting.

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

Print information with styling based on the type specified.

**Args:**
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
**Returns:** None (it prints directly to the terminal as the function executes)

## Additional Code Context

Other contextual comments from the codebase:

- **Line 13:** Colors (a bunch I will likely never use but whatever)
- **Line 26:** Text styles (bold, underline, etc.)
- **Line 50:** Normalize to lowercase for consistency, in case I mess up the info_type label
- **Line 52:** TITLE label: displayed with top and bottom borders, in bold, and optionally in a custom color (otherwise blue by default)
- **Line 55:** Default border character is '='
- **Line 56:** Default width of 70 characters
- **Line 64:** ERROR label: includes borders for emphasis, it is displayed in red and includes the "ERROR" keyword at the start of the print
- **Line 74:** WARNING label: displayed in yellow with a "WARNING" keyword at the start of the print, in bold letters
- **Line 75:** and optionally in a custom color (otherwise yellow by default)
- **Line 80:** SUCCESS label: displayed in green with a "SUCCESS" keyword at the start of the print, in bold letters
- **Line 81:** and optionally in a custom color (otherwise green by default)
- **Line 86:** INFO label: displayed in blue with an "INFO" keyword at the start of the print, in bold letters
- **Line 87:** and optionally in a custom color (otherwise blue by default)
- **Line 92:** STEP label: displayed in bold with the step_number as especified at the start of the print,
- ... and 8 more contextual comments
