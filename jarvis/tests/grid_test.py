"""
NAME: grid_test.py
DESCRIPTION: Stream Deck Grid Test Script
AUTHOR: NhoaKing (pseudonym for privacy)
VERSION: 1.0
This script tests all keys on a Stream Deck by lighting them up with different colors.
With this script I can verify that:
1. The Stream Deck device is properly detected and connected
2. All keys are functional and can display colors 
3. The device communication is working
"""

from StreamDeck.DeviceManager import DeviceManager #From forked repo
from StreamDeck.ImageHelpers import PILHelper #From forked repo
from PIL import Image #From PIL module
from typing import Any, Union, Tuple # For type hints

# Import decorator functions for enhanced terminal output
import sys # Provides access to system-specific parameters and functions, used for system exit to terminate the program
from pathlib import Path # Object-oriented filesystem paths, more robust than os.path.

# Add the parent jarvis directory to the path so we can import utils, actions, ui, etc. In v1.0 I just
# implemented color testing, so no need to import other modules yet apart from utils
sys.path.append(str(Path(__file__).parent.parent))
# - __file__ is the current test file (grid_test.py)
# - .parent gets the tests directory
# - .parent once more gets the jarvis directory
# - This path is then added to sys.path, making all modules in jarvis/ importable

from utils.terminal_prints import print_information_type, TerminalStyles # Terminal output decorators for enhance formatting

def create_color_key(deck: Any, color: Union[str, Tuple[int, int, int]]) -> bytes:
    """
    Create a solid color image for a key of the stream deck.

    This function creates a PIL Image with the specified color and converts it
    to the native format required by the Stream Deck hardware, with
    key_image_format and to_native_format from the forked repo.

    Arguments:
    deck: The Stream Deck device object
    color: Color name in string or an RGB tuple. Defines the color for the key background
    Returns:
    bytes: Image data in Stream Deck's native format
    """
    # Get the dimensions of the key before creating the image to display, in this case a colored background
    key_format = deck.key_image_format() # key_image_format() is a method of the StreamDeck class in the forked repo
    # key_format will store a dictionary with keys like: 'size', 'format', 'flip' and 'rotation'
    # since we want to access the size of the image, we use key_format["size"]
    image_size = key_format["size"] # image_size returns (96,96), so a tuple
    #print_information_type("detail", f"Key image size: {image_size}") # commented out to reduce verbosity

    # Create a new image with the specified color and size
    image = Image.new("RGB", image_size, color) # colors are defined in the main function

    # Convert the image to native format for the stream deck
    native_image = PILHelper.to_native_format(deck, image)
    #print_information_type("detail", "Successfully created native format image") #commented out to reduce verbosity

    return native_image

def reset_close_deck(deck: Any) -> None:
    """
    Reset to clear all keys and close the connection to the deck.

    This function clears all button images and resets the device to its
    default state (for me it shows elgato logo spread across the layout).
    It uses the reset() and close() methods from the forked repo (from DeviceManager class) 
    but I added some print statements to indicate the actions performed.

    Arguments:
    deck: The Stream Deck device object to reset, as defined in the forked repo
    """
    deck.reset()
    print_information_type("progress", "Clean up complete")
    deck.close()
    print_information_type("progress", "Connection closed.")


def main() -> None:
    """
    Main function for the testing of the deck.
    """
    print_information_type("title", "STREAM DECK GRID TEST FOR STREAM DECK XL", color=TerminalStyles.PINK)
    print_information_type("info", "This script will test all keys by lighting them up.")
    device_manager = DeviceManager()
    decks = device_manager.enumerate()

    if decks:
        deck = decks[0] # Use the first detected deck. I only have one device connected, the stream deck XL,
        # so this is fine for now. In the future I can add a selection mechanism if multiple devices are connected
        print_information_type("step", f"Searching for {deck.deck_type()}...", step_number=1)
        print_information_type("step", f"Found {deck.deck_type()}", step_number=2)
        print_information_type("step", f"Opening connection to {deck.deck_type()}", step_number=3)

        try:
            deck.open()
            print_information_type("info", f"Retrieving {deck.deck_type()} information...")
            print_information_type("info", f"Serial number: {deck.get_serial_number()}")
            print_information_type("info", f"Firmware version: {deck.get_firmware_version()}")
            print_information_type("info", f"Number of keys: {deck.key_count()}")

            # Reset the device to clear any previous state before starting the keys test
            deck.reset()

            brightness_level = 100
            deck.set_brightness(brightness_level)
            print_information_type("info", f"Brightness set to {brightness_level}%")

        except Exception as e:
            print_information_type("error", f"Failed to initialize Stream Deck: {e}")
            exit(1)

        print_information_type("step", f"Testing all {deck.key_count()} keys with color background...", step_number=4)

        # Only eight colors for now to cycle through, one for each column of the deck
        key_colors = ["red", "blue", "green", "yellow", "orange", "purple", "pink", "white"]

        # Loop through keys. There are 32 keys on the XL, indexed from 0 to 31
        for key_index in range(deck.key_count()):
            # Using modulo operator to cycle through colors, so every row has the same color order. Grid of 8x4 for XL
            color = key_colors[key_index % len(key_colors)]

            print(f"Setting key {key_index + 1:2d}/{deck.key_count()} to {color}")

            try: # Try-except block to handle any errors when setting key images, so the script can continue testing other keys
                # Create the colored key image
                key_image = create_color_key(deck, color)

                # Set the image on the physical key
                deck.set_key_image(key_index, key_image)
                #print(f"  Key {key_index + 1} updated") # commented out to reduce verbosity

            except Exception as e:
                print_information_type("error", f"Failed to set key {key_index + 1}: {e}")
                # key_index + 1 to show key number to the user

        print_information_type("step", "All keys have been updated.", step_number=5)
        print() # Blank line for better readability
        print()

        print_information_type("title", "VISUAL CHECK:", color=TerminalStyles.YELLOW)
        print_information_type("detail", "Please visually inspect the following:", color=TerminalStyles.YELLOW)
        print_information_type("detail", "All keys are filled with a background color", color=TerminalStyles.YELLOW)
        print_information_type("detail", "No keys are black", color=TerminalStyles.YELLOW)
        print_information_type("detail", "No flickering or display issues", color=TerminalStyles.YELLOW)

        # Pause execution
        input("\nPress ENTER when you finish the check, and you are ready to reset the keys to original state\n")
      
        try:
            print_information_type("info", "Cleaning up deck and closing connection...\n")
            # Reset all keys to original layout
            reset_close_deck(deck)

        except Exception as e:
            print(f"Warning during cleanup: {e}")

        print()
        print_information_type("title", "STREAM DECK GRID TEST COMPLETE :D", color=TerminalStyles.GREEN)
        
    else:
        print_information_type("step", "Searching for Stream Deck devices...", step_number=1)
        print_information_type("error", "No stream decks found!\nPlease check:\n- Device is connected via USB\n- udev rule is set up\n- Stream Deck is not in use by another application\n- Stream deck is installed via pip install -e . in the jarvis-streamdeck directory")
        exit(1)
    
if __name__ == "__main__":
    main()
