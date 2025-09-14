import sys
import subprocess
import os
from StreamDeck.DeviceManager import DeviceManager
from pathlib import Path

# Load configuration from config.env file
def load_config():
    config_path = Path(__file__).parent / "config.env"
    if config_path.exists():
        with open(config_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_config()

YDOTOOL_PATH = os.getenv('YDOTOOL_PATH', 'ydotool')

# Optional: same KEYCODES dictionary from your workflow
KEYCODES = {
    "CTRL": 29, "SHIFT": 42, "ALT": 56, "SUPER": 125,
    "C": 46, "V": 47,  # add more if needed
}

def release_all_keys():
    releases = [f"{code}:0" for code in KEYCODES.values()]
    subprocess.run(
        [YDOTOOL_PATH, "key"] + releases,
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
