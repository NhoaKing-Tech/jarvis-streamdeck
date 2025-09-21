---
title: grid_test
tags:
  - jarvis
  - python
  - documentation
date: 2025-09-21
---

# grid_test

-- GENERAL INFORMATION --
AUTHOR: NhoaKing (pseudonym for privacy)
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: grid_test.py
-- DESCRIPTION --
Stream Deck Grid Test Script. This script tests all keys on a Stream Deck by lighting them up with different colors.
With this script I can verify that:
1. The Stream Deck device is properly detected and connected
2. All keys are functional and can display colors 
3. The device communication is working

## Functions

- [[#create_color_key|create_color_key()]]
- [[#reset_close_deck|reset_close_deck()]]
- [[#main|main()]]

## create_color_key

```python
def create_color_key():
```

Create a solid color image for a key of the stream deck.

This function creates a PIL Image with the specified color and converts it
to the native format required by the Stream Deck hardware, with
key_image_format and to_native_format from the forked repo.

Arguments:
deck: The Stream Deck device object
color: Color name in string or an RGB tuple. Defines the color for the key background
**Returns:**
bytes: Image data in Stream Deck's native format

## reset_close_deck

```python
def reset_close_deck():
```

Reset to clear all keys and close the connection to the deck.

This function clears all button images and resets the device to its
default state (for me it shows elgato logo spread across the layout).
It uses the reset() and close() methods from the forked repo (from DeviceManager class) 
but I added some print statements to indicate the actions performed.

Arguments:
deck: The Stream Deck device object to reset, as defined in the forked repo

## main

```python
def main():
```

Main function for the testing of the deck.

## Additional Code Context

Other contextual comments from the codebase:

- **Line 14:** From forked repo
- **Line 15:** From forked repo
- **Line 16:** From PIL module
- **Line 17:** For type hints
- **Line 19:** Import decorator functions for enhanced terminal output
- **Line 20:** Provides access to system-specific parameters and functions, used for system exit to terminate the program
- **Line 21:** Object-oriented filesystem paths, more robust than os.path.
- **Line 23:** Add the parent jarvis directory to the path so we can import utils, actions, ui, etc. In v1.0 I just
- **Line 24:** implemented color testing, so no need to import other modules yet apart from utils
- **Line 26:** - __file__ is the current test file (grid_test.py)
- **Line 27:** - .parent gets the tests directory
- **Line 28:** - .parent once more gets the jarvis directory
- **Line 29:** - This path is then added to sys.path, making all modules in jarvis/ importable
- **Line 31:** Terminal output decorators for enhance formatting
- **Line 47:** Get the dimensions of the key before creating the image to display, in this case a colored background
- ... and 23 more contextual comments
