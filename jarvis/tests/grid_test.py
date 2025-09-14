"""
=============================
Stream Deck Grid Test Script
=============================
This script tests all keys on a Stream Deck by lighting them up with different colors.
With this script I can verify that:
1. The Stream Deck device is properly detected and connected
2. All keys are functional and can display images
3. The device communication is working correctly
"""

from StreamDeck.DeviceManager import DeviceManager #From original repo
from StreamDeck.ImageHelpers import PILHelper #From original repo
from PIL import Image #From PIL module

def create_color_key(deck, color):
    """
    Generates a solid color image for a key of the stream deck.

    This function creates a PIL Image with the specified color and converts it
    to the native format required by the Stream Deck hardware, with
    key_image_format and to_native_format from the original repo.

    Arguments:
    deck: The Stream Deck device object
    color: Color name (string) or RGB tuple for the key background
    Returns:
    bytes: Image data in Stream Deck's native format
    """
    print(f"+ Creating key image with color: {color}")

    # Get the necessary dimensions of keys for the image
    key_format = deck.key_image_format() # from DeviceManager of the original repo
    image_size = key_format["size"]
    print(f"- Key image size: {image_size}")

    # Create a new image with the specified color and size
    image = Image.new("RGB", image_size, color)

    # Convert the image to native format for the stream deck
    native_image = PILHelper.to_native_format(deck, image)
    print(f"- Successfully created native format image")

    return native_image


def reset_deck(deck):
    """
    Reset the Stream Deck to clear all keys.

    This function clears all button images and resets the device to its
    default state (for me it shows elgato logo spread across the layout).

    Arguments:
    deck: The Stream Deck device object to reset
    """
    print("Clearing all keys...")
    deck.reset()
    print("Stream Deck reset complete")


def main():
    """
    Main function for the testing of the deck.
    """
    print("=" * 50)
    print("STREAM DECK GRID TEST")
    print("=" * 50)

    # Step 1: Enumerate and detect Stream Deck devices
    print("\n1. Searching for Stream Deck devices...")
    device_manager = DeviceManager()
    decks = device_manager.enumerate()

    print(f"Found {len(decks)} Stream Deck device(s)")

    # Check if any devices were found
    if not decks:
        print("ERROR: No Stream Decks found!")
        print("Please check:")
        print("- Device is connected via USB")
        print("- Device drivers are installed")
        print("- Device permissions are correct")
        exit(1)

    # Step 2: Select the first device
    deck = decks[0]
    print(f"\n2. Selected Stream Deck device: {deck.deck_type()}")

    # Step 3: Open and configure the device
    print("\n3. Opening connection to Stream Deck...")
    try:
        deck.open()
        print("Successfully opened Stream Deck connection")

        # Now we can access device information safely
        print(f"   Serial number: {deck.get_serial_number()}")
        print(f"   Firmware version: {deck.get_firmware_version()}")
        print(f"   Number of keys: {deck.key_count()}")

        # Reset the device to ensure clean state
        print("Performing initial reset...")
        deck.reset()

        # Set brightness to a comfortable level (0-100)
        brightness_level = 50
        deck.set_brightness(brightness_level)
        print(f"Set brightness to {brightness_level}%")

    except Exception as e:
        print(f"ERROR: Failed to initialize Stream Deck: {e}")
        exit(1)

    # Step 4: Test all keys with different colors
    print(f"\n4. Testing all {deck.key_count()} keys with colored backgrounds...")

    # Define a variety of colors to cycle through
    key_colors = ["red", "green", "blue", "yellow", "purple", "orange",
                  "pink", "white"]

    print(f"Using {len(key_colors)} different colors (will repeat if more keys than colors)")

    # Loop through all keys and assign colors
    for key_index in range(deck.key_count()):
        # Use modulo to cycle through colors if we have more keys than colors
        color = key_colors[key_index % len(key_colors)]

        print(f"Setting key {key_index + 1:2d}/{deck.key_count()} to {color}")

        try:
            # Create the colored key image
            key_image = create_color_key(deck, color)

            # Set the image on the physical key
            deck.set_key_image(key_index, key_image)
            print(f"  Key {key_index + 1} successfully updated")

        except Exception as e:
            print(f"  ERROR: Failed to set key {key_index + 1}: {e}")

    print(f"\n5. All keys have been updated.")
    print("Check that all keys are filled with colors")

    print("\n")
    print("=" * 50)
    print("CHECK THE FOLLOWING:")
    print("=" * 50)
    print("1. All keys are filled with a background color")
    print("2. No keys are black")
    print("3. No flickering or display issues")

    # Pause execution
    input("\nPress ENTER when you finish the check, and you are ready to reset the keys to original state")

    # Clean up layout and reset the deck
    print("\nCleaning up deck...")
    try:
        # Reset all keys to original layout
        reset_deck(deck)

        # Close the deck connection
        deck.close()
        print("Stream Deck connection closed.")

    except Exception as e:
        print(f"Warning during cleanup: {e}")

    print("\n")
    print("=" * 50)
    print("STREAM DECK GRID TEST COMPLETE :D")
    print("=" * 50)

if __name__ == "__main__":
    main()
