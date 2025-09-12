import subprocess, atexit, time, os
import signal
import sys
from StreamDeck.DeviceManager import DeviceManager # Class DeviceManager from the original repo
from StreamDeck.ImageHelpers import PILHelper
from PIL import Image, ImageDraw, ImageFont

# Directories for assets: code snippets and icons to display in the keys of the steamdeck
FONT_DIR = os.path.join(os.path.dirname(__file__), "jarvisassets", "font", "Roboto-Regular.ttf")
ICONS_DIR = os.path.join(os.path.dirname(__file__), "jarvisassets", "jarvisicons")
SNIPPETS_DIR = os.path.join(os.path.dirname(__file__), "jarvisassets", "snippets")

# Dictionary to hold different layouts
layouts = {}

# Keycode mapping for ydotool
KEYCODES = {
    # Letters
    "A": 30, "B": 48, "C": 46, "D": 32, "E": 18,
    "F": 33, "G": 34, "H": 35, "I": 23, "J": 36,
    "K": 37, "L": 38, "M": 50, "N": 49, "O": 24,
    "P": 25, "Q": 16, "R": 19, "S": 31, "T": 20,
    "U": 22, "V": 47, "W": 17, "X": 45, "Y": 21,
    "Z": 44,
    # Numbers
    "1": 2, "2": 3, "3": 4, "4": 5, "5": 6,
    "6": 7, "7": 8, "8": 9, "9": 10, "0": 11,
    # Function
    "F1": 59, "F2": 60, "F3": 61, "F4": 62,
    "F5": 63, "F6": 64, "F7": 65, "F8": 66,
    "F9": 67, "F10": 68, "F11": 87, "F12": 88,
    # Modifiers
    "CTRL": 29, "SHIFT": 42, "ALT": 56,
    "RIGHTCTRL": 97, "RIGHTSHIFT": 54, "RIGHTALT": 100,
    "SUPER": 125,
    # Special
    "ESC": 1, "TAB": 15, "CAPSLOCK": 58,
    "SPACE": 57, "ENTER": 28, "BACKSPACE": 14,
    # Navigation
    "UP": 103, "DOWN": 108, "LEFT": 105, "RIGHT": 106,
    "HOME": 102, "END": 107, "PAGEUP": 104, "PAGEDOWN": 109,
    "INSERT": 110, "DELETE": 111,
    # Symbols
    "MINUS": 12, "EQUAL": 13,
    "LEFTBRACE": 26, "RIGHTBRACE": 27,
    "BACKSLASH": 43, "SEMICOLON": 39,
    "APOSTROPHE": 40, "GRAVE": 41,
    "COMMA": 51, "DOT": 52, "SLASH": 53,
}

def insert_snippet(snippet_name):
    """
    Function to open desired snippet and type the content calling type_text function.
    """
    snippet_path = os.path.join(SNIPPETS_DIR, snippet_name + ".txt")
    if not os.path.exists(snippet_path):
        print(f"Snippet {snippet_name} not found at {snippet_path}")
        return  
    with open(snippet_path, "r") as f:
        content = f.read()
    type_text(content)

def hot_keys(*keys):
    """
    Function to simulate hotkeys (press and release of keys) using ydotool
    """
    seq = []
    for key in keys:
        seq.append(f"{KEYCODES[key]}:1")
    for key in reversed(keys):
        seq.append(f"{KEYCODES[key]}:0")
    subprocess.Popen(["/home/nhoaking/ydotool/build/ydotool", "key"] + seq)

def type_text(text):
    """
    Function to type text using ydotool. Includes "--" to handle if text starts with "-" 
    """
    subprocess.Popen(
        ["/home/nhoaking/ydotool/build/ydotool", "type", "--", text]
    )

# Button rendering function.
def paint_button(deck, key, label=None, icon=None, color=str("black")):
    """
    Function to handle aesthetics of the buttons/keys on the StreamDeck.
    Parameters:
    deck: the StreamDeck device
    key: the key index (0-31 in my case for the ElGato XL StreamDeck)
    label: optional text label to display on the button
    icon: optional icon filename to display on the button
    color: background color (used as fallback when icon not found, or as background for icons)
    """
    # If an icon is provided, load it and scale it. Otherwise, use a solid color. If the icon is not found, fall back to color.
    if icon:
        icon_path = os.path.join(ICONS_DIR, icon) # Path to the icon file
        if os.path.exists(icon_path): # Check if the icon file exists
            icon_img = Image.open(icon_path) # Load the icon image
            # Scale and center the icon with margins. # margin = (top, right, bottom, left)
            # No margins if no label, but more bottom margin if there is a label, so that the label text doesn't overlap the icon.
            margins = (0, 0, 0, 0) if not label else (0, 0, 20, 0)
            key_image = PILHelper.create_scaled_key_image( # Create the key image with the icon using PILHelper from the original repo
                deck, icon_img, margins=margins, background=color # Background black by default
            )
        else:
            print(f"Warning: icon {icon_path} not found, falling back to color") # If executing from a service, this will not appear anywhere. It is here for debugging if the script is executed from a terminal.
            key_image = PILHelper.create_key_image(deck, background="red") # Fallback to red background if icon not found
    else:
        # Just a background if no icon
        key_image = PILHelper.create_key_image(deck, background=color) # Use specified color

    # Include label if provided with the ImageDraw module from PIL
    if label:
        draw = ImageDraw.Draw(key_image)
        try:
            font = ImageFont.truetype(FONT_DIR, 16)  # adjust size of font here
        except OSError:
            print("Could not load the font, check the font path and the font format (it must be .ttf).")
            font = ImageFont.load_default() #fallback to default font if custom font not found

        # Center text at bottom
        draw.text(
            (key_image.width / 2, key_image.height - 5),
            text=label,
            font=font,
            anchor="ms",  # middle-south
            fill="white"
        )

    # Convert to native format and set the key image on the deck
    deck.set_key_image(key, PILHelper.to_native_key_format(deck, key_image))


########
def get_nautilus_windows():
    """
    Get all Nautilus windows and their current directories.
    Returns a list of tuples: (window_id, current_directory)
    """
    try:
        # Use gdbus to query Nautilus windows through D-Bus
        result = subprocess.run([
            'gdbus', 'call', '--session',
            '--dest', 'org.gnome.Nautilus',
            '--object-path', '/org/gnome/Nautilus',
            '--method', 'org.gtk.Application.ListWindows'
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode != 0:
            return []
            
        # Parse the result to get window information
        # This returns window object paths that we can query further
        windows = []
        
        # Alternative approach: use wmctrl-like functionality through gsettings/dconf
        # Check running Nautilus processes and their working directories
        ps_result = subprocess.run([
            'ps', 'aux'
        ], capture_output=True, text=True)
        
        nautilus_processes = [line for line in ps_result.stdout.split('\n') 
                            if 'nautilus' in line and not 'grep' in line]
        
        return nautilus_processes
        
    except subprocess.TimeoutExpired:
        return []
    except Exception as e:
        print(f"Error getting Nautilus windows: {e}")
        return []

def focus_nautilus_window():
    """
    Attempt to focus an existing Nautilus window using multiple methods.
    Returns True if successful, False otherwise.
    """
    methods_tried = []
    
    # Method 1: Use D-Bus to activate Nautilus application
    try:
        result = subprocess.run([
            'gdbus', 'call', '--session',
            '--dest', 'org.gnome.Nautilus',
            '--object-path', '/org/gnome/Nautilus',
            '--method', 'org.gtk.Application.Activate',
            '{}'  # Empty dictionary for platform_data
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            methods_tried.append("D-Bus activation: SUCCESS")
            return True
        else:
            methods_tried.append(f"D-Bus activation: FAILED ({result.stderr})")
            
    except Exception as e:
        methods_tried.append(f"D-Bus activation: ERROR ({e})")
    
    # Method 2: Use desktop file activation
    try:
        result = subprocess.run([
            'gtk-launch', 'org.gnome.Nautilus'
        ], capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            methods_tried.append("GTK launch: SUCCESS")
            return True
        else:
            methods_tried.append(f"GTK launch: FAILED")
            
    except Exception as e:
        methods_tried.append(f"GTK launch: ERROR ({e})")
    
    # Method 3: Try ydotool (native Wayland automation tool)
    try:
        # First check if ydotool is available
        subprocess.run(['which', 'ydotool'], check=True, capture_output=True)
        
        # Use ydotool to focus Nautilus window
        # Method 3a: Try Alt+Tab to cycle to Nautilus window
        result = subprocess.run([
            'ydotool', 'key', 'alt+Tab'
        ], capture_output=True, text=True, timeout=3)
        
        if result.returncode == 0:
            # Give the system a moment to process
            time.sleep(0.2)
            methods_tried.append("ydotool Alt+Tab: SUCCESS")
            return True
        else:
            methods_tried.append("ydotool Alt+Tab: FAILED")
            
    except subprocess.CalledProcessError:
        methods_tried.append("ydotool: Not available")
    except Exception as e:
        methods_tried.append(f"ydotool: ERROR ({e})")
    
    # Method 4: Use ydotool with Super key to open activities and search for Nautilus
    try:
        # This method opens GNOME activities and searches for Nautilus
        subprocess.run(['ydotool', 'key', 'Super_L'], timeout=2)
        time.sleep(0.3)
        subprocess.run(['ydotool', 'type', 'nautilus'], timeout=2)
        time.sleep(0.3)
        subprocess.run(['ydotool', 'key', 'Return'], timeout=2)
        
        methods_tried.append("ydotool Super search: SUCCESS")
        return True
        
    except Exception as e:
        methods_tried.append(f"ydotool Super search: ERROR ({e})")
    
    print("Focus methods tried:")
    for method in methods_tried:
        print(f"  - {method}")
    
    return False

def is_nautilus_running_with_directory(target_dir):
    """
    Check if Nautilus is running and if any window shows the target directory.
    Returns True if found, False otherwise.
    """
    target_path = os.path.abspath(os.path.expanduser(target_dir))
    
    try:
        # Check if Nautilus is running
        result = subprocess.run([
            'pgrep', '-f', 'nautilus'
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            return False  # Nautilus not running
        
        # Method 1: Check recent files/directories in Nautilus
        # Nautilus stores recent locations in dconf
        try:
            recent_result = subprocess.run([
                'dconf', 'read', '/org/gnome/nautilus/window-state/initial-size'
            ], capture_output=True, text=True, timeout=3)
            # This is a basic check - Nautilus is running
            
        except Exception:
            pass
        
        # Method 2: Use lsof to check open file descriptors
        try:
            lsof_result = subprocess.run([
                'lsof', '+D', target_path
            ], capture_output=True, text=True)
            
            if 'nautilus' in lsof_result.stdout:
                return True
                
        except Exception:
            pass
        
        # Method 3: Check Nautilus process working directories
        pids = result.stdout.strip().split('\n')
        for pid in pids:
            if pid:
                try:
                    cwd_path = f'/proc/{pid}/cwd'
                    if os.path.exists(cwd_path):
                        actual_cwd = os.readlink(cwd_path)
                        if os.path.samefile(actual_cwd, target_path):
                            return True
                except (OSError, FileNotFoundError):
                    continue
        
        return False
        
    except Exception as e:
        print(f"Error checking Nautilus status: {e}")
        return False

def open_nautilus_smart(target_directory="/home/nhoaking"):
    """
    Smart Nautilus opener that focuses existing window or creates new one.
    
    Args:
        target_directory (str): Directory to open/focus
    """
    target_dir = os.path.expanduser(target_directory)
    
    print(f"Smart opening directory: {target_dir}")
    
    # Check if target directory exists
    if not os.path.exists(target_dir):
        print(f"Error: Directory {target_dir} does not exist!")
        return False
    
    # Check if Nautilus is already showing this directory
    if is_nautilus_running_with_directory(target_dir):
        print("Nautilus already showing target directory - attempting to focus...")
        if focus_nautilus_window():
            print("Successfully focused existing Nautilus window")
            return True
        else:
            print("Could not focus existing window, opening new one...")
    else:
        print("No Nautilus window found with target directory")
    
    # Open new Nautilus window with the target directory
    try:
        print(f"Opening new Nautilus window for: {target_dir}")
        process = subprocess.Popen([
            "nautilus", target_dir
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Give it a moment to start
        time.sleep(0.5)
        
        print(f"Nautilus opened successfully (PID: {process.pid})")
        return True
        
    except Exception as e:
        print(f"Error opening Nautilus: {e}")
        return False

# Convenience function with your original signature
def open_nautilus():
    """Original function signature for backward compatibility"""
    return open_nautilus_smart("/home/nhoaking")


###########################
# --- Actions ---
def open_vscode_busybee():
    project_path = "/home/nhoaking/Zenith/busybee"
    subprocess.Popen([
        "code", project_path,
    ])
    time.sleep(2)
    hot_keys("CTRL", "SHIFT", "GRAVE")


def open_obsidian():
    subprocess.Popen(["obsidian"])

def open_vscode_jarvis():
    project_path = "/home/nhoaking/Zenith/jarvis-streamdeck"
    subprocess.Popen([
        "code", project_path,
    ])
    time.sleep(2)
    hot_keys("CTRL", "GRAVE")
    
def open_spotify():
    not_open = subprocess.run(["pgrep", "-x", "spotify"], capture_output=True)
    if not_open.returncode == 0:
        # Spotify is running, then the button runs either play or pause
        subprocess.Popen(["playerctl", "--player=spotify", "play-pause"])
    else:
        # Spotify not running, the starts the app.
        subprocess.Popen(["spotify"])  

#def open_nautilus():
#    subprocess.Popen(["nautilus", "/home/nhoaking"])

def open_terminal_env():
    subprocess.Popen(["/home/nhoaking/Zenith/jarvis-streamdeck/test/open_jarvisbusybee_env_T.sh"])

def open_terminal():
    hot_keys("CTRL", "ALT", "T")

def open_github():
    subprocess.Popen(["xdg-open", "https://github.com/NhoaKing-Tech"])

def open_shine():
    subprocess.Popen(["xdg-open", "https://www.youtube.com/watch?v=x53OGmkT-eM&list=RDx53OGmkT-eM&start_radio=1"])

def open_chat():
    subprocess.Popen(["xdg-open", "https://chatgpt.com/g/g-p-68b9273a9e488191b335ed4477655eeb-zenith/project"])

def open_claude():
    subprocess.Popen(["xdg-open", "https://claude.ai/project/01993cb6-a107-7274-8d75-4368cc08d1b1"])

def toggle_output_mute():
    subprocess.Popen(["amixer", "set", "Master", "toggle"])

def is_mic_muted():
    result = subprocess.run(
        ["amixer", "get", "Capture"],
        capture_output=True,
        text=True
    )
    return "[off]" in result.stdout  # True if mic muted


def toggle_mic(deck, key):
    # Toggle mute
    subprocess.run(["amixer", "set", "Capture", "toggle"])

    # Check new state
    muted = is_mic_muted()

    # Update button icon
    if muted:
        paint_button(deck, key, label="OFF", icon="mic-off.png")
    else:
        paint_button(deck, key, label="ON", icon="mic-on.png")

def type_message():
    type_text("Hello from StreamDeck!")

def insert_snippet_action(snippet_name):
    return lambda: insert_snippet(snippet_name)

def copy():
    hot_keys("CTRL", "C")

def paste():
    hot_keys("CTRL", "V")

def type_hola():
    type_text("Hola!")

def release_all_keys():
    releases = [f"{code}:0" for code in KEYCODES.values()]
    subprocess.Popen(
        ["/home/nhoaking/ydotool/build/ydotool", "key"] + releases
    )

def switch_page(page_name):
    global current_page
    current_page = page_name
    render_page(layouts[page_name])

def render_page(page):
    if deck and deck.is_open():
        deck.reset()  # clear old icons
        deck.set_brightness(50)
    for key, props in page.items():
        paint_button(
            deck,
            key,
            props.get("label"),
            props.get("icon"),
            props.get("color")
        )

current_page = "main"

# 0,1,2,3,4,5,6,7
# 8,9,10,11,12,13,14,15
# 16,17,18,19,20,21,22,23
# 24,25,26,27,28,29,30,31

# Main page layout
layouts["main"] = {
    0: {"icon": "spotify.png", "action": open_spotify},
    1: {"icon": "obsidian.png", "action": open_obsidian},
    8: {"icon": "chatgpt.png", "action": open_chat},
    9: {"icon": "claude.png", "action": open_claude},
    
    4: {"icon": "github.png", "color": "#2f3036", "action": open_github},
    5: {"icon": "jarviscode.png", "action": open_vscode_jarvis},
    6: {"icon": "busybeecode.png", "action": open_vscode_busybee},
    7: {"icon": "busybee.png", "action": lambda: switch_page("busybee")}, #icon <a href="https://www.flaticon.com/free-icons/bee" title="bee icons">Bee icons created by Indielogy - Flaticon</a>
    8: {"icon": "terminal.png", "action": open_terminal},
    9: {"icon": "terminalenv.png", "action": open_terminal_env},
    10: {"icon": "python.png", "action": lambda: switch_page("python")},
    11: {"icon": "git.png", "color": "#2f3036", "action": lambda: switch_page("git")},
    12: {"icon": "terminal_layout.png", "action": lambda: switch_page("terminal_layout")},
    13: {"icon": "nautilus.png", "action": open_nautilus}, # <a href="https://www.flaticon.com/free-icons/files-and-folders" title="files and folders icons">Files and folders icons created by juicy_fish - Flaticon</a>
    #9: {"label": "Text", "color": "pink", "action": type_message},
    #10: {"label": "Copy", "color": "blue", "action": copy},
    #11: {"label": "Paste", "color": "pink", "action": paste},
    #12: {"label": "Hola", "color": "blue", "action": type_hola},
    #13: {"label": "More", "color": "purple", "action": lambda: switch_page("terminal")},
    #14: {"icon": "shine.png", "action": open_shine},
    
    31: {"icon": "mic-fill.png", "action": lambda: toggle_mic(deck, 31)},
}

# Terminal page layout
layouts["terminal"] = {
    0: {"label": "Go Back", "icon": "back.png", "color": "grey", "action": lambda: switch_page("main")},
    1: {"label": "Run LS", "color": "pink", "action": lambda: type_text("ls\n")},
    2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet_action("hello")},
    3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet_action("python_boilerplate")},
}

layouts["busybee"] = {
    0: {"label": "Go Back", "icon": "back.png", "color": "grey", "action": lambda: switch_page("main")},
    1: {"label": "Run LS", "color": "pink", "action": lambda: type_text("ls\n")},
    2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet_action("hello")},
    3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet_action("python_boilerplate")},
}

layouts["python"] = {
    0: {"label": "Go Back", "icon": "back.png", "color": "grey", "action": lambda: switch_page("main")},
    1: {"label": "Run LS", "color": "pink", "action": lambda: type_text("ls\n")},
    2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet_action("hello")},
    3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet_action("python_boilerplate")},
}

layouts["git"] = {
    0: {"label": "Go Back", "icon": "back.png", "color": "grey", "action": lambda: switch_page("main")},
    1: {"label": "Run LS", "color": "pink", "action": lambda: type_text("ls\n")},
    2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet_action("hello")},
    3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet_action("python_boilerplate")},
}

layouts["terminal_layout"] = { #<div> Icons made by <a href="https://www.flaticon.com/authors/icon-hubs" title="Icon Hubs"> Icon Hubs </a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com'</a></div>
    0: {"label": "Go Back", "icon": "back.png", "color": "grey", "action": lambda: switch_page("main")},
    1: {"label": "Run LS", "color": "pink", "action": lambda: type_text("ls\n")},
    2: {"label": "Simple Snippet", "color": "cyan", "action": insert_snippet_action("hello")},
    3: {"label": "Python Boilerplate", "color": "orange", "action": insert_snippet_action("python_boilerplate")},
}



# --- Cleanup ---
_cleaned_up = False
def cleanup(deck=None):
    global _cleaned_up
    if _cleaned_up:
        return
    _cleaned_up = True
    try:
        print("\nCleaning up...")
        release_all_keys()
        if deck and deck.is_open():
            deck.reset()
            deck.close()
    except Exception as e:
        print(f"(cleanup ignored error: {e})")

def safe_exit(deck=None):
    cleanup(deck)
    sys.exit(0)

# --- Event handler ---
def key_change(deck, key, state):
    if state and key in layouts[current_page]:
        try:
            layouts[current_page][key]["action"]()
        except:
            pass

# --- Main with retry loop ---
max_attempts = 60   # retry for ~5 minutes
interval = 5
attempts = 0

deck = None
while attempts < max_attempts:
    decks = DeviceManager().enumerate()
    if decks:
        deck = decks[0]
        print("Stream Deck found!")
        break
    else:
        print(f"No Stream Deck found, retrying in {interval}s...")
        time.sleep(interval)
        attempts += 1
else:
    print("Stream Deck not found. Exiting.")
    sys.exit(1)

deck.open()
deck.reset()

# Render buttons
render_page(layouts[current_page])

# Register key handler
deck.set_key_callback(key_change)

# Handle exit signals
signal.signal(signal.SIGINT, lambda s, f: safe_exit(deck))
atexit.register(cleanup, deck)

print("Stream Deck active. Press CTRL+C to quit.")
signal.pause()
