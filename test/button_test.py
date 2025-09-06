from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from PIL import ImageDraw

# Open the first StreamDeck
deck = DeviceManager().enumerate()[0]
deck.open()
deck.reset()

# Create a new key image using PILHelper
image = PILHelper.create_image(deck)

# Draw a red rectangle with "Hi"
draw = ImageDraw.Draw(image)
draw.rectangle((0, 0, image.width, image.height), fill="red")
draw.text((20, 20), "Hi", fill="white")

# Convert the image to StreamDeck native format and set key 0
deck.set_key_image(0, PILHelper.to_native_format(deck, image))

input("Press Enter to reset and close...")

deck.reset()
deck.close()
