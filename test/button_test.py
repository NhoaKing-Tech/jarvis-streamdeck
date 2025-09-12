from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from PIL import ImageDraw

# Open the streamDeck
deck = DeviceManager().enumerate()[0] #there is only one for me
deck.open()

# Create a new key image using PILHelper from the repo
image = PILHelper.create_image(deck)

# Set the first button to blue with the text "Test"
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, image.width, image.height), fill="blue")
draw.text((35, 20), "Test", fill="white")

# Convert the image to StreamDeck native format for first button, as done in the example 
deck.set_key_image(0, PILHelper.to_native_format(deck, image))
#hint: deck.set_key_image(key, image) from example_basic.py

# Line to make the script wait so I can see the key
input("Press enter to reset the stream deck...")

deck.reset()
deck.close()
