import sys
import subprocess
from StreamDeck.DeviceManager import DeviceManager

# Optional: same KEYCODES dictionary from your workflow
KEYCODES = {
    "CTRL": 29, "SHIFT": 42, "ALT": 56, "SUPER": 125,
    "C": 46, "V": 47,  # add more if needed
}

def release_all_keys():
    releases = [f"{code}:0" for code in KEYCODES.values()]
    subprocess.run(
        ["/home/nhoaking/ydotool/build/ydotool", "key"] + releases,
        check=False
    )

def reset_all_streamdecks():
    decks = DeviceManager().enumerate()
    if not decks:
        print("No Stream Decks found.")
        return

    for deck in decks:
        try:
            deck.open()
            deck.reset()
            deck.close()
            print(f"✅ Reset Stream Deck: {deck.id()}")
        except Exception as e:
            print(f"⚠️ Could not reset Stream Deck: {e}")

if __name__ == "__main__":
    print("Releasing any stuck keys...")
    release_all_keys()

    print("Resetting Stream Deck(s)...")
    reset_all_streamdecks()

    print("Done.")
    sys.exit(0)
