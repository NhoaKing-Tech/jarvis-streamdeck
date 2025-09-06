from StreamDeck.DeviceManager import DeviceManager

decks = DeviceManager().enumerate()
print("Found {} Stream Deck(s).".format(len(decks)))

for index, deck in enumerate(decks):
    deck.open()
    deck.reset()
    print("Opened '{}' - serial: {}".format(deck.deck_type(), deck.get_serial_number()))
    deck.close()