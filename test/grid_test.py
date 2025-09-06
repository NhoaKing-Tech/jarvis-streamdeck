from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from PIL import Image, ImageDraw

# Generate a solid color image for a button
def create_color_key(deck, color):
    image = Image.new("RGB", deck.key_image_format()["size"], color)
    return PILHelper.to_native_format(deck, image)

# Reset function (clear all keys)
def reset_deck(deck):
    deck.reset()

# Main
decks = DeviceManager().enumerate()
if not decks:
    print("No Stream Decks found.")
    exit(1)

deck = decks[0]
deck.open()
deck.reset()
deck.set_brightness(50)

try:
    # Fill all keys with different colors
    colors = ["red", "green", "blue", "yellow", "purple", "orange",
              "cyan", "magenta", "pink", "lime", "teal", "white"]
    for i in range(deck.key_count()):
        color = colors[i % len(colors)]
        deck.set_key_image(i, create_color_key(deck, color))

    print("Deck is lit up with colors. Press CTRL+C to quit...")

    # Keep the script running until user interrupts
    while True:
        pass

except KeyboardInterrupt:
    print("\nExiting...")

finally:
    reset_deck(deck)
    deck.close()
