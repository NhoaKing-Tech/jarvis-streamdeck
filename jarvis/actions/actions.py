"""
Action functions for the Stream Deck Jarvis application.
This module contains all the action functions that are triggered by Stream Deck key presses.
"""

import subprocess
import time
import os
from ui.render import render_keys #My render module

# Configuration constants (will be set by the main module)
YDOTOOL_PATH = None
SNIPPETS_DIR = None
BASHSCRIPTS_DIR = None
KEYCODES = None

def initialize_actions(ydotool_path, snippets_dir, bashscripts_dir, keycodes):
    """Initialize the actions module with required constants from the main module."""
    global YDOTOOL_PATH, SNIPPETS_DIR, BASHSCRIPTS_DIR, KEYCODES
    YDOTOOL_PATH = ydotool_path
    SNIPPETS_DIR = snippets_dir
    BASHSCRIPTS_DIR = bashscripts_dir
    KEYCODES = keycodes


def type_text(text):
    """
    Function to type text using ydotool. Includes "--" to handle if text starts with "-"
    I could use now xdotool instead of ydotool after switching to X11. But I already 
    have ydotool installed because I was running on Wayland previously. 
    It seems to still be working fine.
    If I get issues later with it, I will switch to xdotool.
    Returns a callable function for use in layout definitions.
    """
    def execute():
        if YDOTOOL_PATH is None:
            raise RuntimeError("Call initialize_actions() from main first.")
        subprocess.Popen([YDOTOOL_PATH, "type", "--", text])
    return execute


def insert_snippet(snippet_name):
    """
    Function to insert desired code snippet or boilerplate.
    Similar to type_text but for code snippets stored as txt files.
    Instead of wrapping it in lambda, I use a wrapper function as in switch_layout of run_jarvis.py
    """
    def execute():
        if SNIPPETS_DIR is None or YDOTOOL_PATH is None:
            raise RuntimeError("Call initialize_actions() from main first.")
        snippet_path = os.path.join(SNIPPETS_DIR, snippet_name + ".txt")
        if not os.path.exists(snippet_path):
            print(f"Snippet {snippet_name} not found at {snippet_path}")
            return
        with open(snippet_path, "r") as f:
            snippet = f.read()
        subprocess.Popen([YDOTOOL_PATH, "type", "--", snippet])
    return execute


def hot_keys(*keys):
    """
    Function to simulate hotkeys (press and release of keys) using ydotool
    """
    if KEYCODES is None or YDOTOOL_PATH is None:
        raise RuntimeError("Call initialize_actions() from main first.")
    seq = []
    for key in keys:
        seq.append(f"{KEYCODES[key]}:1") # press
    for key in reversed(keys):
        seq.append(f"{KEYCODES[key]}:0") # release, essential to release in reverse order and avoid sticky keys. This was my first bug when I started using ydotool >.<
    subprocess.Popen([YDOTOOL_PATH, "key"] + seq)


def open_vscode(project_path):
    """
    Open VSCode with a specified project and terminal toggle after 2 seconds.
    To control the terminal directory and environment,
    I set up a .vscode/settings.json file in each project.
    I could have used a function instead of a lambda, but I decided to stick to the
    lambda method for consistency with other actions.
    """
    return lambda: (
        subprocess.Popen(["code", project_path]),
        time.sleep(2),
        hot_keys("CTRL", "GRAVE")
    )


def open_obsidian(vault_path):
    """
    Open obsidian to my Zenith vault.
    Obsidian supports command line argument to open specific vaults (--vault)
    """
    vault_name = os.path.basename(os.path.normpath(vault_path)) # extract the vault name
    def wrapper():
        try:
            # here same procedure as for nautilus_path action
            wmctrl_output = subprocess.check_output(["wmctrl", "-l"], text=True)
            for line in wmctrl_output.splitlines():
                if "Obsidian" in line and vault_name in line:
                    # Found the vault window, activate it
                    window_id = line.split()[0]
                    subprocess.run(["wmctrl", "-i", "-a", window_id])
                    return
        except subprocess.CalledProcessError:
            pass

        # If not found, launch an obsidian window with the vault opened
        subprocess.Popen(["obsidian", "--vault", vault_name]) # I forgot to add the --vault argument >.<

    return wrapper

def open_spotify():
    """
    Open Spotify if not running, otherwise toggle play/pause.
    I do this with playerctl which is a command line utility to control media players.
    Since this function takes no arguments, it does not need to be wrapped in a lambda
    as the previous functions.
    """
    not_open = subprocess.run(["pgrep", "-x", "spotify"], capture_output=True)
    if not_open.returncode == 0:
        # Spotify is running, then the button runs either play or pause
        subprocess.Popen(["playerctl", "--player=spotify", "play-pause"])
    else:
        # Spotify not running, the starts the app.
        subprocess.Popen(["spotify"])


def open_terminal_env():
    if BASHSCRIPTS_DIR is None:
        raise RuntimeError("Call initialize_actions() from main first.")
    subprocess.Popen([os.path.join(BASHSCRIPTS_DIR, "open_jarvisbusybee_env_T.sh")])
    #subprocess.Popen(["/home/nhoaking/Zenith/jarvis-streamdeck/jarvis/assets/bash_scripts/open_jarvisbusybee_env_T.sh"])


def open_terminal():
    """
    The linux shortcut to open a new terminal window
    """
    hot_keys("CTRL", "ALT", "T")


def open_github():
    """
    Open my GitHub profile default web browser, in my case Chrome.
    I could have used webbrowser.open() but I prefer xdg-open for better compatibility.
    I wanted to also check if the browseer had already a tab with the url open, and if so, just focus that tab instead of opening a new one. I looked into the Chrome DevTools Protocol (CDP) which allows controlling Chrome/Chromium browsers via command line. It seemes too complex for this simple task, so I decided to just open a new tab with xdg-open instead. Furthermore, there seems to be some significant security risks. Since I am no expert in this, better to
    completely avoid it. Therefore, devTools approach will be discared entirely.
    """
    subprocess.Popen(["xdg-open", "https://github.com/NhoaKing-Tech"])


def open_youtube():
    """
    Open youtube in default web browser, in my case Chrome.
    """
    subprocess.Popen(["xdg-open", "https://www.youtube.com/"])


def open_freecodecamp():
    """
    Open freecodecamp website in default web browser, in my case Chrome.
    """
    subprocess.Popen(["xdg-open", "https://www.freecodecamp.org/"])


def open_chat():
    """
    Open ChatGPT in default web browser, in my case Chrome.
    """
    subprocess.Popen(["xdg-open", "https://chatgpt.com/"])


def open_claude():
    """
    Open Claude in default web browser, in my case Chrome.
    """
    subprocess.Popen(["xdg-open", "https://claude.ai/"])


# Microphone control and state check functions
def toggle_output_mute():
    """
    Function to toggle system audio output mute using amixer
    """
    subprocess.Popen(["amixer", "set", "Master", "toggle"])


def is_mic_muted():
    """
    Function to check microophone mute status using amixer
    """
    result = subprocess.run(
        ["amixer", "get", "Capture"],
        capture_output=True,
        text=True
    )
    return "[off]" in result.stdout  # True if mic muted


def toggle_mic(deck, key):
    """
    Function to toggle microphone mute and update the StreamDeck button icon.
    Returns a lambda function for use in layout definitions.
    """

    return lambda: (
        subprocess.run(["amixer", "set", "Capture", "toggle"]),
        render_keys(deck, key,
                   label="OFF" if is_mic_muted() else "ON",
                   icon="mic-off.png" if is_mic_muted() else "mic-on.png")
    )


# -------------------- Wrapper functions to simplify action definitions in keys
def type_message():
    type_text("Hello World! :)")


def copy():
    """
    Super simple example for using hotkeys function
    """
    hot_keys("CTRL", "C")


# TO DO: Generalize the next function to work with other applications and to handle positioning and sizing of windows.
def nautilus_path(target_dir):
    """
    I want this function to open file manager windows or raise them if there is
    already one open with my target directory. Instead of always opening a new Nautilus window,
    I will first check if there is already one open with my target directory.
    If there is, I will just bring it to the front (raise it).
    This prevents window clutter and gives me a better user experience. :)
    """

    # I need to convert the target directory to an absolute path because:
    # 1. Relative paths like "../folder" or "./folder" can be ambiguous
    # 2. os.path.abspath() converts these to full paths like "/home/user/folder"
    # 3. This ensures I am comparing the same format when checking window titles later
    # 4. It also resolves any symbolic links to their actual paths
    #    (Symbolic links are like shortcuts - they point to another file/directory.
    #     os.path.abspath() follows the shortcut to get the real location)
    target_dir = os.path.abspath(target_dir)

    # STEP 1: I need to check if Nautilus is already open with my target directory

    # wmctrl is a command-line tool that lets me interact with X11 windows in Linux
    # The "-lx" flags mean:
    # -l: list all windows
    # -x: include the WM_CLASS property (this helps me identify the application type)
    #
    # subprocess.check_output() runs this command and captures its text output
    # text=True ensures I get a string back instead of bytes
    wmctrl_output = subprocess.check_output(["wmctrl", "-lx"], text=True)

    # The wmctrl output looks like this (one line per window):
    # 0x02400003  0 org.gnome.Nautilus.org.gnome.Nautilus desktop file-browser - /home/user/Documents
    # 0x02600004  0 firefox.Firefox          desktop Firefox
    #
    # Each line contains: window_id, desktop_number, WM_CLASS, hostname, window_title
    # I need to parse each line to extract the information I need
    for line in wmctrl_output.splitlines():
        # I only care about Nautilus windows, so I check if "org.gnome.Nautilus"
        # is in the line. This is the WM_CLASS identifier for Nautilus windows.
        if "org.gnome.Nautilus" in line:

            # Now I need to extract the window ID and title from this line
            # line.split() breaks the line into parts separated by whitespace
            # The window ID is always the first part (index 0)
            # Example: "0x02400003" from the line above
            window_id = line.split()[0]

            # The window title starts from the 4th element (index 3) onwards
            # I use " ".join() to put the title back together with spaces
            # because the title might contain spaces that were split apart
            # Example: from "desktop file-browser - /home/user/Documents"
            # I want "file-browser - /home/user/Documents"
            window_title = " ".join(line.split()[3:])

            # Now I need to check if this Nautilus window is showing my target directory
            # There are different ways the directory might appear in the window title:

            # First, I get just the folder name (last part of the path)
            # os.path.basename("/home/user/Documents") returns "Documents"
            # This helps me match windows that might not show the full path
            folder_name = os.path.basename(target_dir)

            # I check three conditions to see if this window matches my target:
            if (target_dir in window_title or          # Full path is in title
                folder_name in window_title or        # Just folder name is in title
                window_title.endswith(folder_name)):  # Title ends with folder name

                # I found a matching window! Instead of opening a new one,
                # I will bring this existing window to the front (raise it)
                # print(f"Raising existing Nautilus window for {target_dir}")

                # wmctrl can also control windows, not just list them
                # -i: "use window ID" - I am giving it a window ID number (0x02400003)
                # instead of a window title/name (more reliable than titles)
                # -a: "activate window" - bring the window to front and give it focus
                # (like clicking on it in the taskbar)
                # window_id: the window ID I extracted earlier (like 0x02400003)
                subprocess.run(["wmctrl", "-i", "-a", window_id])

                # I found and raised the window, so I am done - return early
                # This prevents the function from continuing to Step 2
                return

    # STEP 2: If I get here, it means I did not find any existing Nautilus window
    # with my target directory, so I need to open a new one

    # print(f"Opening new Nautilus at {target_dir}")

    # subprocess.Popen() starts a new process without waiting for it to finish
    # This is perfect for GUI applications because:
    # 1. I don't want my Python script to hang waiting for Nautilus to close
    # 2. The user should be able to use Nautilus independently
    # 3. My script can continue with other tasks
    #
    # I pass the target directory as an argument to nautilus so it opens there
    subprocess.Popen(["nautilus", target_dir])