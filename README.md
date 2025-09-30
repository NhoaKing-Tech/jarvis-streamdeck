# Jarvis StreamDeck Automation System

[![Documentation](https://img.shields.io/badge/docs-comprehensive-blue.svg)](DOCUMENTATION.md)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Extended from [python-elgato-streamdeck](https://github.com/abcminiuser/python-elgato-streamdeck)*

> **Technical Writing Portfolio:** I built this hardware integration system as both a productivity tool and a documentation showcase. The repository demonstrates API documentation, user guides, multi-audience content strategy, and automated documentation generation through git hooks.

> [View Documentation System](#documentation-philosophy)

---
## What is Jarvis?

Jarvis is my personal automation system that transforms an Elgato StreamDeck XL into a powerful Linux productivity control center. I built this on top of the python-elgato-streamdeck library, extending it with custom workflow automation capabilities.

### Why I Built This

I wanted a physical control panel for my development workflow - launching projects, executing commands, managing applications - all at the press of a button. But beyond just making it work, I wanted to build it **the right way** with comprehensive documentation, clean architecture, and automated tooling.

### Documentation Highlights (What Makes This Special)

- 📚 **50+ Documented Functions** - Every function has detailed docstrings explaining what, why, and how
- 📖 **Step-by-Step Guides** - Installation, configuration, and troubleshooting written for actual humans
- 🏗️ **Architecture Documentation** - I explain my design decisions and the trade-offs I considered
- 🤖 **Automated Doc Generation** - Git hooks + Python scripts keep docs synced with code automatically
- 👥 **Multi-Audience Strategy** - Custom comment system (PROD/DEV/ARCH/EDU) for different readers
- ✅ **Production-Ready** - Runs as a systemd service with proper lifecycle management

### Technical Features

- **Custom Action System**: Programmable button actions for system control, application launching, and workflow automation
- **Multi-Layout Support**: Dynamic layout switching for different contexts (git tools, conda commands, etc.)
- **Deep Linux Integration**: Works with ydotool, wmctrl, playerctl, systemd, and other system tools
- **Visual Customization**: Custom icon rendering with text overlays and dynamic button states
- **Service Integration**: Designed to run as a systemd service from startup
- **Configuration Management**: Environment-based config system that's actually easy to set up

---

## Project Status

**🚧 Active Development** - This project is not considered finished. The core functionality works great, but I'm constantly adding features as new requirements emerge. Current implementation provides solid StreamDeck automation, but additional features are planned.

**What works right now:**
- All core StreamDeck functionality (buttons, layouts, actions)
- Systemd service integration
- Custom layouts and actions
- Documentation automation system

**Known Issues:**
- Snippet typing adds extra indentation not present in source files (investigating ydotool behavior)

**What I'm working on:**
- Fixing snippet indentation bug
- Other custom actions based on my workflow needs
- Enhanced testing coverage
- Better error handling
- Publish the docs of this project as part of my portfolio GitHub pages with Quartz.

---

## Quick Links

| For Users | For Contributors | For Technical Writers |
|-----------|-----------------|---------------------|
| [Quick Start](#quick-start) | [Project Structure](#project-structure) | [Writing Samples](docs/WRITING_SAMPLES.md) |
| [Full Setup](#detailed-installation) | [Architecture](DOCUMENTATION.md) | [Documentation System](#documentation-philosophy) |
| [Troubleshooting](#troubleshooting) | [Contributing](CONTRIBUTING.md) | [API Reference](docs/API_REFERENCE.md) |

---

## System Requirements

**What I developed and tested on:**
- **OS**: Ubuntu 24.04.3 LTS (Noble Numbat) - other Linux-based distros could work but I haven't tested them.
- **Display Server**: X11 - Wayland is not supported because I had to switch to X11 due to limitations on permissions. It also has window management tool limitations, which I have not implemented yet, but will revisit soon.
- **Python**: 3.11.4 - I use conda for environment management because I use this at work, but venv will work too.
- **Hardware**: Elgato StreamDeck XL (32-key version) - other models might work but I only have the XL to test with.

**Why X11 instead of Wayland?**
I originally started developing on Wayland, which is why I use ydotool (Wayland-compatible). However, I encountered one issue that made me switch to X11:
- Window management tools (wmctrl) don't work on Wayland, limiting functionality like smart window focusing that I use in nautilus and Obsidian actions.

Rather than rewrite everything, I switched to X11 and kept ydotool since it already worked. I might revisit Wayland support in the future when I have more experience...

---

## Quick Start

**Time needed:** 15-30 minutes for basic test of streamdeck connection.

**What you'll need:**
- Linux machine with X11. If you have Wayland per default, switch to X11 from the user login screen. You can check your current display server with:
  ```bash
  echo $XDG_SESSION_TYPE
  ```
  It should print `x11`. If it prints `wayland`, you need to log out and select X11 from the login screen options.
- Python 3.11+.
- Elgato StreamDeck XL.
- Patience for the udev and systemd setup steps, they can be tricky the first time!

### Minimal Setup (For Testing)

Set up a udev rule to allow your user to access the StreamDeck without `sudo`, install the Python dependencies, and run a quick test script to verify the connection.

```bash
# Create udev rule for StreamDeck access
sudo nano /etc/udev/rules.d/60-jarvis.rules
```

Add this content (adjust `idProduct` for your StreamDeck model):
```
SUBSYSTEM=="usb", ATTR{idVendor}=="0fd9", ATTR{idProduct}=="008f", MODE="0666"
```

**How to find your idProduct:**
```bash
lsusb | grep -i elgato
# Example output: Bus 001 Device 005: ID 0fd9:008f Elgato Systems GmbH Stream Deck XL
#                                      ^^^^  ^^^^
#                                    vendor product
```

Reload udev rules:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

```bash
# 1. Clone the repository
git clone https://github.com/NhoaKing-Tech/jarvis-streamdeck.git
cd jarvis-streamdeck

# 2. Set up Python environment
# I use conda because maybe I'll need this for data science workflows later. My environment is called jarvis-busybee, as it is paired with another project. If you want to name it differently, just remember to update the bash scripts later that use the jarvis-busybee environment.
conda create -n jarvis-busybee python=3.11.4
conda activate jarvis-busybee

# You can also use venv if you prefer, but you will need to modify the bash scripts accordingly, as they assume conda, and are set up for an environment named "jarvis-busybee".
# python3.11 -m venv jarvis-busybee
# source jarvis-busybee/bin/activate

# 3. Install Python dependencies
pip install -e .  # Install StreamDeck library in development mode
pip install "pillow>=9.0.0" hidapi

# 4. Install system dependencies
sudo apt install libhidapi-libusb0 libhidapi-hidraw0

# 5. Run configuration setup from the original repo
cd jarvis && python config/setup_config.py

# 6. Test it out
cd jarvis/tests
python grid_test.py
```

**⚠️ Important:** This minimal setup lets you test that the connection to the streamdeck is working, but you'll need the [full setup](#detailed-installation) for custom actions and layouts.

**Next Steps:**
- If it works → Continue to [Full Setup](#detailed-installation)
- If it doesn't work → Check [Troubleshooting](#troubleshooting)

---

## Project Structure

Here's how I organized everything:

```
jarvis-streamdeck/
|-- jarvis/                         # Main application code
|   |-- actions/                    # Action handlers for key presses
|   |   |-- actions.py              # 50+ documented action functions
|   |-- config/                     # Configuration management
|   |   |-- initialization.py       # Centralized module initialization
|   |   |-- setup_config.py         # Interactive config setup
|   |   |-- config.env              # Your personal config (generated)
|   |-- core/                       # Application core
|   |   |-- application.py          # Main entry point & lifecycle
|   |   |-- logic.py                # Event handling & layout switching
|   |   |-- lifecycle.py            # Resource cleanup & management
|   |-- ui/                         # User interface layer
|   |   |-- layouts.py              # StreamDeck layout definitions
|   |   |-- render.py               # Visual rendering engine
|   |-- utils/                      # Utilities
|   |   |-- reset_jarvis.py         # Deck reset utility (use if layout gets stuck)
|   |   |-- terminal_prints.py      # Formatted console output
|   |-- docs_utils/                 # ⭐ Documentation automation system
|   |   |-- annotation_system.py    # Multi-audience comment classification
|   |   |-- quartz_markdown.py      # Auto-generate docs from docstrings
|   |   |-- branch_manager.py       # Dev/production workflow management
|   |-- assets/                     # Icons, fonts, scripts, snippets
|   |   |-- jarvisicons/            # Custom StreamDeck button icons
|   |   |-- bash_scripts/           # Executable bash scripts
|   |   |-- snippets/               # Code snippet text files
|   |-- tests/                      # Testing utilities
|   |-- main.py                     # Python entry point
|   |-- main.sh                     # Shell entry point (for systemd service)
|
|-- src/                      # Forked StreamDeck library
|-- docs/                     # Generated documentation
|-- .git/hooks/               # Documentation automation hooks
|-- README.md                 # Traditional README (detailed setup)
```

### Recent Structure Changes

I recently reorganized the project structure for better maintainability. Here's what changed and why:

**What Changed:**
- Added `config/` directory for centralized configuration.
- Moved `lifecycle.py` and `logic.py` from `ui/` to new `core/` directory.
- Renamed `run_jarvis.py` → `application.py` (clearer naming).
- Renamed `run_jarvis.sh` → `main.sh` (consistency with main.py).
- Created `main.py` as clean entry point that delegates to `core.application`.
- Moved `reset_jarvis.py` to `utils/` (it's a utility, not core code).

**Why These Changes:**
- **Better Separation of Concerns**: Core logic in `core/`, UI code in `ui/`, config in `config/`, utilities in `utils/`.
- **Consistent Entry Points**: Both `main.py` and `main.sh` are at the same level.
- **Clearer Naming**: `application.py` describes what it does better than `run_jarvis.py`.
- **Logical Grouping**: Config files grouped together makes more sense.
- **Standard Python Structure**: Follows Python package conventions.
- **Future-Proof**: Easier to extend and maintain.
- **Documentation Clarity**: Easier for new contributors to understand the project layout.

---

## Detailed Installation

Okay, let's do the full setup properly. This will take 45 minutes to an hour for the complete installation.

### Step 1: Environment Setup

#### 1.1 System Dependencies

```bash
sudo apt update && sudo apt upgrade
# Make sure to install HID device access libraries (required for StreamDeck communication) if you did not do it with the Quick Start Guide.
sudo apt install libhidapi-libusb0 libhidapi-hidraw0

# Install tools that jarvis uses for system integration
sudo apt install wmctrl playerctl alsa-utils xdg-utils

# Install ydotool build dependencies
sudo apt install git cmake build-essential libevdev-dev scdoc
```

**What these do:**
- `wmctrl` - Window management (for smart Obsidian/Nautilus window handling)
- `playerctl` - Media player control (so Spotify integration works)
- `alsa-utils` - Audio control (provides `amixer` for microphone toggle)
- `nautilus` - File manager (GNOME's default file browser)
- `gnome-terminal` - Terminal emulator (for bash script execution)
- `xdg-utils` - Desktop integration (provides `xdg-open` for opening URLs)

#### 1.3 Build ydotool

ydotool to automate key presses (or mouse movements) in Linux. I used ydotool in this project to let jarvis simulate hotkeys. I have an example in actions.py, the super simple copy action... but it is just so that you can customize it with more complex hotkeys. You need to build it from source. You can follow the documentation for that [here](https://gabrielstaples.com/ydotool-tutorial/#gsc.tab=0).

```bash
# In the same terminal where you build ydotool from source (cloning the repo), note the full path - you'll need this later for configuration
# Should be something like: /home/user/ydotool/build/ydotool
pwd  # Print your current path
```

**Why build from source instead of using a package?**
Normal installation does not work with Jarvis because it needs to run as a background daemon (`ydotoold`). A daemon is a program with a unique purpose. They are utility programs that run silently in the background to monitor and take care of certain subsystems to ensure that the operating system runs properly.

**Why ydotool instead of xdotool?**
I originally started this project on Wayland, where xdotool doesn't work. After changing to X11 due to the headaches I was getting with Wayland, I tried it out, and ydotool works on both Wayland and X11. Therefore, I kept it even after switching to X11. This way, I keep my options open for future Wayland support without having to rewrite everything.

#### 1.2 Python Environment

```bash
# I use conda, but you can use venv or whatever you prefer. 
# You need of course to have miniconda installed first.
conda create -n jarvis-busybee python=3.11.4
conda activate jarvis-busybee

# If you prefer venv, you can use it, but you will need to modify the bash scripts accordingly, as they assume conda, and are set up for an environment named "jarvis-busybee".
# python3.11 -m venv jarvis-busybee
# source jarvis-busybee/bin/activate
```

**Why conda?** I use conda because I might want this environment to support data science workflows later. Plus, it handles package dependencies really well. venv should work fine too if that's what you're comfortable with and if you do not need complex dependencies. You might not even need a virtual environment if you want to install everything globally, but I recommend using one to avoid dependency conflicts.

#### 1.4 Python Dependencies

```bash
# Navigate back to the jarvis-streamdeck directory
cd /path/to/jarvis-streamdeck

# Install the StreamDeck library in editable mode
pip install -e .

# Install other Python dependencies
pip install "pillow>=9.0.0" hidapi
```

**Why editable install (`-e`)?**
The `-e` flag installs the StreamDeck library in "development mode", which means any changes I make to the library code are immediately available without reinstalling. This is essential since I forked the repository and might need to modify it.

**Why not `python setup.py install`?**
That's deprecated! Modern Python development uses `pip install -e .` instead because:
- It handles dependencies properly
- It's easy to uninstall (`pip uninstall streamdeck`)
- It's virtual environment aware
- It's what professional Python developers use

---

### Step 2: Hardware Setup

Now let's make sure your user can access the StreamDeck and ydotool without needing `sudo` every time.

#### 2.1 User Permissions

```bash
# Add your user to the uinput group (required for ydotool)
sudo usermod -a -G uinput $USER

# ⚠️ IMPORTANT: Log out and log back in for this to take effect
# Seriously, you need to log out and log back in. Just restarting the terminal won't work.
```

**Verify it worked:**
```bash
groups $USER | grep uinput  # Should show "uinput" in the output
```

#### 2.2 udev Rules (Making Device Access Work)

udev rules tell Linux to give your user permission to access devices without `sudo`. We need three rules:

##### Rule 1: StreamDeck Permission Rule

```bash
sudo nano /etc/udev/rules.d/60-jarvis.rules
```

Add this content (adjust `idProduct` for your StreamDeck model):
```
SUBSYSTEM=="usb", ATTR{idVendor}=="0fd9", ATTR{idProduct}=="008f", MODE="0666"
```

**How to find your idProduct:**
```bash
lsusb | grep -i elgato
# Example output: Bus 001 Device 005: ID 0fd9:008f Elgato Systems GmbH Stream Deck XL
#                                      ^^^^  ^^^^
#                                    vendor product
```

**Common StreamDeck device IDs:**
- StreamDeck XL: `008f` (that's mine)
- StreamDeck Original: `0060`
- StreamDeck Mini: `0063`

##### Rule 2: ydotool udev Rule

```bash
sudo nano /etc/udev/rules.d/99-uinput.rules
```

Add this content:
```
KERNEL=="uinput", MODE="0660", GROUP="uinput", OPTIONS+="static_node=uinput"
```

##### Rule 3: Jarvis Auto-Start Rule (Optional but Recommended)

This makes jarvis start automatically when you plug in your StreamDeck, otherwise you have to run the main.sh script manually every time.

```bash
sudo nano /etc/udev/rules.d/99-jarvis-autostart.rules
```

Add this content (adjust `idProduct` to match your StreamDeck):
```
ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0fd9", ATTR{idProduct}=="008f", TAG+="systemd", ENV{SYSTEMD_USER_WANTS}+="jarvis.service"
ACTION=="remove", SUBSYSTEM=="usb", ATTR{idVendor}=="0fd9", ATTR{idProduct}=="008f", TAG+="systemd", ENV{SYSTEMD_USER_STOP}+="jarvis.service"
```

**What this does:** When you plug in the StreamDeck, jarvis starts automatically. When you unplug it, jarvis stops.

#### 2.3 Reload udev Rules

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger

# In case, this does not work, unplug your StreamDeck and plug it back in for the changes to take effect, or reboot.
```

**Why the weird numbering (60-, 99-)?**
udev processes rules in numerical order. Lower numbers run first, higher numbers run later. I use 60 for the StreamDeck permission rule (needs to run early) and 99 for the auto-start rule (needs to run after permissions are set). This ensures everything happens in the right order.

---

### Step 3: Service Configuration

Now let's set up systemd services so jarvis runs automatically at startup.

#### 3.1 ydotool Service

ydotool needs to run as a background daemon. A daemon is just a program that runs continuously in the background. Let's set that up:

```bash
# Create the systemd user service directory if it doesn't exist
mkdir -p ~/.config/systemd/user

# Create the ydotool service file
nano ~/.config/systemd/user/ydotoold.service
```

Service file content:
```
[Unit]
Description=ydotoold daemon (Wayland key injection)

[Service]
ExecStart=/home/user/ydotool/build/ydotoold
Restart=always

[Install]
WantedBy=default.target
```

**⚠️ Replace `/home/user/ydotool/build/ydotoold` with your actual path!**

You can find your path by:
```bash
cd ~/ydotool/build && pwd  # Shows full path
```

#### 3.2 Jarvis Service

```bash
nano ~/.config/systemd/user/jarvis.service
```

Service file content:
```
[Unit]
Description=Jarvis StreamDeck Service
After=graphical.target

[Service]
Type=simple
EnvironmentFile=/home/user/projects/jarvis-streamdeck/jarvis/config/config.env
WorkingDirectory=/home/user/projects/jarvis-streamdeck/jarvis
ExecStartPre=/bin/sleep 10
ExecStart=/home/user/projects/jarvis-streamdeck/jarvis/main.sh
Restart=on-failure

[Install]
WantedBy=default.target
```

**⚠️ Update all the paths to match your system:**
- `EnvironmentFile` - Where your `config.env` file is
- `WorkingDirectory` - Your jarvis directory
- `ExecStart` - Path to `main.sh`

**Why the 10-second sleep?**
The `ExecStartPre=/bin/sleep 10` gives the system time to fully boot before jarvis starts. Otherwise, sometimes the StreamDeck isn't ready yet and jarvis fails to start. I learned this the hard way after jarvis kept failing on boot, and I tried various things before realizing a simple delay fixed it.

#### 3.3 Configure main.sh

The `main.sh` script activates your conda environment and runs jarvis:

```bash
nano /path/to/jarvis-streamdeck/jarvis/main.sh
```

Update the conda environment name to match yours:
```bash
# Change this line:
conda activate jarvis-busybee

# To whatever you named your environment:
conda activate jarvis
```

Make it executable:
```bash
chmod u+x /path/to/jarvis-streamdeck/jarvis/main.sh
```

**Why use a shell script instead of running Python directly?**
Because systemd services run in a clean environment without your shell configuration. The shell script loads conda properly and activates the environment before running Python. Without this, the service would fail because it wouldn't find the conda environment.

#### 3.4 Enable and Start Services

```bash
# Reload systemd to recognize the new service files
systemctl --user daemon-reload

# Enable and start ydotool
systemctl --user enable ydotoold.service
systemctl --user start ydotoold.service

# Enable and start jarvis
systemctl --user enable jarvis.service
systemctl --user start jarvis.service

# Check that everything started correctly
systemctl --user status ydotoold.service
systemctl --user status jarvis.service
```

**What you should see:**
- Both services should show `active (running)` in green
- No error messages in the status output

**If something's wrong:**
```bash
# View detailed logs for jarvis
journalctl --user -u jarvis.service -n 50

# View detailed logs for ydotool
journalctl --user -u ydotoold.service -n 50

# Follow logs in real-time (helpful for debugging)
journalctl --user -u jarvis.service -f
```

#### 3.5 Service Management Commands

Here are the commands I use all the time while I develop and customize jarvis:

```bash
# Restart jarvis after making changes to code or layouts
systemctl --user restart jarvis.service

# Stop jarvis temporarily (useful for debugging, in which case I need to then run jarvis/utils/reset_jarvis.py to reset the deck. Then I run main.py manually to see any errors)
systemctl --user stop jarvis.service

# If the main.py script works as I expect, I can then start the service again. Do not run main.py while the service is running, as it will conflict because the service is already using the StreamDeck. Also, DO NOT RUN WITHINTEGRATED TERMINAL IN VSCODE, as it messes up the environment. Always use a native terminal, as the script will not run the same as it does in a native terminal, and you will waste hours debugging like I did, when actually there is no problem with the code... when running from native terminal, it works fine.
systemctl --user start jarvis.service

# View live logs (Ctrl+C to exit, useful for debugging)
journalctl --user -u jarvis.service -f

# View last 50 log lines
journalctl --user -u jarvis.service -n 50
```

**Protip (optional but recommended):** If you'll be modifying jarvis frequently, add these aliases to save typing. You'll use `jarvis-restart` constantly when changing layouts or actions, `jarvis-logs` for debugging when things break, and `jarvis-status` for quick health checks:

```bash
# Open your .bashrc file
nano ~/.bashrc

# Scroll to the end and add these lines:
alias jarvis-restart='systemctl --user restart jarvis.service'
alias jarvis-logs='journalctl --user -u jarvis.service -f'
alias jarvis-status='systemctl --user status jarvis.service'

# Save (Ctrl+X, then Y, then Enter) and reload:
source ~/.bashrc
# or close the terminal and open a new one

# Now you can use them:
jarvis-restart  # Instead of the full systemctl command, that you will use dozens of times. One might think that you would memorize the full command after using it so many times... but I honestly never remember and I have to look it up every time, so this saves me a lot of time.
```

**When you'll use these:**
- `jarvis-restart` - After every code/layout change.
- `jarvis-logs` - When debugging issues or watching real-time output
- `jarvis-status` - Quick check if jarvis is running

**Important:** Just running `alias` in the terminal only works for that session. You need to add it to `~/.bashrc` to make it permanent (available in every new terminal).

If you're just setting jarvis up once and rarely changing it, skip these. But if you're actively developing (like for this portfolio), they're huge time-savers.

---

### Step 4: Configuration

Almost there! Now let's configure jarvis with your personal settings.

#### 4.1 Interactive Configuration

I built an interactive setup script to make this easier:

```bash
cd /path/to/jarvis-streamdeck/jarvis
python config/setup_config.py
```

**It will ask you for:**

1. **ydotool path** - The path to your built ydotool binary
   - Example: `/home/yourname/ydotool/build/ydotool`
   - You can find this with: `cd ~/ydotool/build && pwd`

2. **Projects directory** - Where you keep your code projects
   - Default: `/home/yourname/projects`
   - This is used for the "open project in VSCode" buttons

3. **Obsidian vaults** (optional) - If you use Obsidian for note-taking
   - You can leave these empty if you don't use Obsidian
   - I have two vaults: one for my journal, one for documentation with Quartz

4. **Keyring password** (optional) - For the "type password" button
   - ⚠️ **Security warning:** This gets stored in plain text. I know this isn't ideal - I'm currently researching secure credential management solutions (Linux keyring or password managers) and plan to refactor this feature. For now, please use this only for non-sensitive passwords or leave it empty.
   - See [security note](#security-note-about-passwords) below

**What this creates:**
A `config/config.env` file with your settings. Example:
```bash
YDOTOOL_PATH=/home/yourname/ydotool/build/ydotool
PROJECTS_DIR=/home/yourname/projects
OBSIDIAN_VAULT_journal=/home/yourname/vaults/journal
OBSIDIAN_VAULT_quartz=/home/yourname/vaults/quartz
KEYRING_PW=your_password_here (not secure, see note below, better leave this empty for now!!)
```

#### 4.2 Manual Configuration (Alternative)

If you prefer to edit the config file manually:

```bash
nano jarvis/config/config.env
```

See [`config/config_example.env`](jarvis/config/config_example.env) for a complete template with detailed explanations.

#### Security Note About Passwords

⚠️ **Important:** The `KEYRING_PW` setting stores your password in plain text, which creates security risks:
- Visible to any process running as your user
- Included in system backups
- Could be accidentally committed to git (though config.env is gitignored)

**Better alternatives I should implement:**
- Password managers

I know storing passwords in plain text is a dummy move. I built the keyring password feature when I was first learning, and I plan to refactor it. For now, treat this file with the same care as you would any sensitive credential. Don't use important passwords here, or better yet, leave it empty for now. I just set this up to demonstrate what a button can do, and I certainly need to revisit a correct implementation later.

I think I can implement a solution for introducing passwords that is secure, there are passwords that are honestly very inconvenient to type, and I want to have a button for that. I will revisit this later when I learn how to do it properly.

---

### Step 5: Verify Everything Works

Let's test each component to make sure everything is set up correctly:

```bash
# 1. Test ydotool
~/ydotool/build/ydotool type "hello world"
# This should type "hello world" into whatever window has focus

# 2. Test StreamDeck detection
lsusb | grep -i elgato
# Should show your StreamDeck device

# 3. Test Python environment
python -c "import hidapi; print('HID access OK')" # or python3 if running from system python
# Should print "HID access OK" without errors

# 4. Test jarvis manually (use native terminal, not VSCode!)
cd jarvis && python main.py
# Your StreamDeck should light up with the main layout
# Press Ctrl+C to stop

# 5. Test jarvis service
systemctl --user status jarvis.service
# Should show "active (running)" in green
```

**⚠️ Important about VSCode terminal:**
If you run `python main.py` from VSCode's integrated terminal, it might not work properly. This is because VSCode's terminal has a different environment than your native terminal. System tools like ydotool and wmctrl sometimes don't work correctly in VSCode's terminal. Always test from a native terminal (gnome-terminal, konsole, xterm, etc.).

I learned this after spending two hours debugging why nothing worked in VSCode but worked fine everywhere else. Don't make the same mistake I did!

---

## Customization

### How to Modify Layouts

All the button layouts are defined in `jarvis/ui/layouts.py`. This is where you customize what each button looks like and what it does.

**Basic layout structure:**
```python
main_layout = {
    0: {"icon": "spotify.png", "action": actions.spotify},
    1: {"label": "Terminal", "color": "#fff200ff", "action": actions.hk_terminal},
    2: {"icon": "github.png", "action": actions.url_github},
}
```

**Key components:**
- `icon` - PNG filename from `assets/jarvisicons/`
- `label` - Text to display on the button
- `color` - Background color in hex format
- `action` - Function to execute when button is pressed

**Example customizations:**

```python
# Add a button to open your favorite project
0: {"icon": "myproject.png", "action": actions.open_vscode("/home/you/projects/myproject")}

# Add a button with text instead of icon
1: {"label": "Build", "color": "#ff6b6b", "action": actions.execute_bash("build.sh")}

# Add a button that types a command
2: {"label": "ssh server", "action": actions.type_text("ssh user@server.com\n")}
```

**After making changes:**
```bash
systemctl --user restart jarvis.service
```

or if you set up the alias:
```bash
jarvis-restart
```

### How to Add Custom Actions

Actions are functions in `jarvis/actions/actions.py`. Each action does something when a button is pressed.

**Example: Add a custom action to open Firefox:**

```python
def open_firefox() -> None:
    """Open Firefox browser"""
    subprocess.Popen(["firefox"])
```

Then use it in layouts.py:
```python
5: {"icon": "firefox.png", "action": actions.open_firefox}
```

**For actions that need parameters, use the factory pattern:**

The factory pattern is a programming design pattern where a function creates and returns another function, in my case what I called "wrapper". If you write functions with parameters, then when calling them in layouts.py, you need a way to pass those parameters without calling the function immediately. The factory pattern solves this by creating a function that returns another function with the parameters set. The other option is to use `functools.partial` or have lambdas everywhere needed, but I find the factory pattern more explicit and easier to understand for beginners, and easier to set up in the layouts.py file. Otherwise you would have to write lambdas in some places in layouts.py, depending on the specific action, and that would be inconsistent and confusing, and I usually do not remember which actions I wrote that need a lambda and which do not, so I would have to look it up every time. For functions that take parameters, I always use the factory pattern now.

```python
def open_custom_app(app_path: str) -> Callable[[], None]:
    """Open a custom application

    Args:
        app_path: Full path to the application executable

    Returns:
        Function that opens the application when called
    """
    def wrapper():
        subprocess.Popen([app_path])
    return wrapper
```

Then use it in layouts.py:
```python
5: {"icon": "myapp.png", "action": actions.open_custom_app("/usr/bin/myapp")} #no need for lambda here
```

**Why this pattern?**
If your action needs parameters (like a file path), you need to wrap it in a function that returns another function. I explain this pattern in detail in the comments in `actions.py` - check out the PATTERN 1 and PATTERN 2 examples.

---

## Troubleshooting

### Permission Denied Errors

**Problem:** Getting "Permission denied" when trying to access StreamDeck or ydotool

**Solutions:**
```bash
# 1. Check if you're in the uinput group
groups $USER | grep uinput
# If you don't see "uinput", you need to add yourself to the group:
sudo usermod -a -G uinput $USER
# Then log out and log back in (seriously, you have to log out)

# 2. Check if udev rules exist
ls -la /etc/udev/rules.d/ | grep -E "jarvis|uinput"
# Should see: 60-jarvis.rules, 99-uinput.rules, 99-jarvis-autostart.rules

# 3. Reload udev rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# 4. Unplug and replug StreamDeck
# Sometimes udev needs this to recognize the new rules
```

---

### Service Fails to Start

**Problem:** `systemctl --user status jarvis.service` shows "failed" or "inactive"

**Diagnosis steps:**

```bash
# 1. Check the logs (this usually tells you what's wrong)
journalctl --user -u jarvis.service -n 50

# 2. Try running jarvis manually to see the actual error
cd /path/to/jarvis-streamdeck/jarvis
python main.py
```

**Common issues:**

**Wrong paths in service file:**
```bash
# Check that all paths in your service file are correct
cat ~/.config/systemd/user/jarvis.service

# Common mistakes:
# - Wrong path to main.sh
# - Wrong path to config.env
# - Wrong WorkingDirectory
```

**Conda environment not found:**
```bash
# Check that your conda environment exists
conda env list | grep jarvis

# Check that main.sh has the correct environment name
cat /path/to/jarvis-streamdeck/jarvis/main.sh | grep "conda activate"
```

**VSCode terminal environment issue:**
```bash
# If it works from native terminal but not as a service, check that:
# 1. main.sh properly loads conda
# 2. All dependencies are installed in the conda environment
# 3. PROJECTS_DIR environment variable is set correctly in config.env
```

---

### StreamDeck Not Detected

**Problem:** Getting "Stream Deck not found" error

**Solutions:**

```bash
# 1. Check if StreamDeck is connected via USB
lsusb | grep -i elgato
# Should show something like: "ID 0fd9:008f Elgato Systems GmbH Stream Deck XL"

# 2. Check device permissions
ls -l /dev/hidraw* /dev/usb/hiddev*
# Your user should be able to read these devices

# 3. Try different USB port
# Some USB hubs can cause issues. Try connecting directly to your computer.

# 4. Check if another process is using the StreamDeck
# If you have the official Elgato software or another StreamDeck program running, stop it

# 5. Unplug, wait 5 seconds, plug back in
# Sometimes the device just needs a reset
```

---

### ydotool Not Working

**Problem:** Hotkeys and text typing don't work

**Solutions:**

```bash
# 1. Check if ydotoold service is running
systemctl --user status ydotoold.service
# Should show "active (running)"

# 2. Test ydotool manually
~/ydotool/build/ydotool type "test"
# Should type "test" into focused window

# 3. Check user groups
groups $USER | grep uinput
# Must show "uinput"

# 4. Check udev rule for uinput
cat /etc/udev/rules.d/99-uinput.rules
# Should contain: KERNEL=="uinput", MODE="0660", GROUP="uinput", OPTIONS+="static_node=uinput"

# 5. Restart ydotoold service
systemctl --user restart ydotoold.service
```

---

### Layout Changes Don't Show Up

**Problem:** You modified `layouts.py` but StreamDeck still shows old layout

**Solution:**
```bash
# Restart jarvis service
systemctl --user restart jarvis.service

# If that doesn't work, check for Python syntax errors
cd jarvis && python -m py_compile ui/layouts.py

# Watch logs while restarting to see any errors
journalctl --user -u jarvis.service -f
# In another terminal:
systemctl --user restart jarvis.service
```

---

### Button Icons Don't Display

**Problem:** Keys show colored background but no icon

**Solutions:**

```bash
# 1. Check if icon file exists
ls jarvis/assets/jarvisicons/your_icon.png

# 2. Check icon path in layouts.py
grep "your_icon.png" jarvis/ui/layouts.py

# 3. Verify icon is PNG format
file jarvis/assets/jarvisicons/your_icon.png
# Should say "PNG image data"

# 4. Check icon isn't too large
# StreamDeck XL buttons are 96x96 pixels
# Icons should be 96x96 or smaller

# 5. Restart jarvis after adding new icons
systemctl --user restart jarvis.service
```

---

### StreamDeck Stuck on Old Layout

**Problem:** Stopped jarvis service but StreamDeck still shows last layout

**Solution:**
```bash
# Use the reset utility
cd /path/to/jarvis-streamdeck/jarvis
python utils/reset_jarvis.py

# This clears the StreamDeck and resets it to blank state
```

I built this utility because when you stop the jarvis service, the StreamDeck hardware keeps showing whatever was last displayed. The reset script clears it properly.

---

## Documentation Philosophy

### Multi-Audience Comment System

One of the things I'm most proud of in this project is the documentation system. I created a custom comment annotation system that lets me write documentation for four different audiences in the same codebase:

```python
# PROD: Essential production comment

# DEV: Detailed development explanation
# For developers working on the code

# ARCH: Architecture decision rationale
# Design choices and trade-offs explained

# EDU: Educational content
# Teaching CS concepts for learners
```

**Why I built this:**
I was frustrated with documentation always drifting out of sync with code. Separate documentation files get stale, but too many code comments make the code hard to read, and I documented for myself while I learn programming concepts, but I also want to share knowledge with others. Someone new to programming can read the EDU comments, a developer can read the DEV comments, and teams can focus on PROD comments. I wanted a system that scales with the audience.

I wanted a system where:
1. Documentation lives with the code (never out of sync). I can update code and docs together, and be as much detailed as I want without cluttering the code, because I can filter by audience. I still get locally a full codebase with all the full comments and educational content, without actually having to separate this into different files, which is a nightmare to maintain (I speak from experience).
2. Different readers get different levels of detail.
3. It's easy for other contributors to follow the pattern.
4. I can automatically generate docs for different audiences.

**How it works:**
I have a docs_utils module that processes the codebase and extracts comments by their prefix. It generates markdown documentation files for each audience. Then the markdown files are stored in `jarvis/docs/content/` and can be viewed with any markdown viewer. I use Obsidian for this, but you can use any markdown viewer. Then to publish the docs, I use Quartz, which is a static site generator for markdown files. I will set up a GitHub Pages site for this later, as I am joining the documentation for this project with the documentation for my transition into tech writing, which I am building with Quartz and Obsidian. Since the GitHub pages site is not ready yet, I will update this README later with the link to the docs site, which will include the documentation for this project, plus all the educational content I am building for myself while I learn programming concepts. The scripts in the docs_utils module are:
- `annotation_system.py` classifies comments by prefix
- `quartz_markdown.py` generates markdown docs from docstrings
- Git pre-commit hooks automatically update docs
- `branch_manager.py` manages dev vs production documentation. I call production documentation to what I push now to GitHub, and dev documentation is what I keep locally with all the educational content, and the bible of knowledge I am building for myself while I learn programming concepts.

For more details, see [DOCUMENTATION.md](DOCUMENTATION.md).

### Automated Documentation Generation

My git hooks automatically generate documentation before every commit. I discovered recently git hooks and I am hooked (pun intended). This is a game-changer for keeping documentation in sync with code. I know developers already know this, but I never used git hooks before this project, and I am amazed at how powerful they are.

```bash
# .git/hooks/pre-commit
#!/usr/bin/env bash
python3 jarvis/docs_utils/quartz_markdown.py
git add jarvis/docs/content/
```

**What this means:**
- Documentation is always up-to-date
- I never have to manually copy docstrings
- Changes to codebase automatically update docs
- No more "forgot to update the docs" commits or writing the docs weeks later, when you don't remember the details anymore, which is what always happened to me before.
- It is important to assume that you have amnesia when writing code and documentation, because you will forget the details later, especially if you are learning new concepts and you are not an expert.

---

## Dependencies

### Python Packages

| Package | Version | What I use it for |
|---------|---------|-------------------|
| streamdeck | 0.9.8 | StreamDeck hardware interface (from my fork) |
| Pillow | ≥9.0.0 | Image processing for button rendering |
| hidapi | latest | USB HID device communication |

### System Tools

| Tool | Package | What I use it for |
|------|---------|-------------------|
| ydotool | (build from source) | Keyboard/mouse input simulation |
| wmctrl | wmctrl | Window management for smart window handling |
| playerctl | playerctl | Spotify media controls |
| alsa-utils | alsa-utils | Microphone toggle (via amixer) |
| nautilus | nautilus | File manager integration |
| gnome-terminal | gnome-terminal | Opening terminals with scripts |
| xdg-utils | xdg-utils | Opening URLs and files (via xdg-open) |

---

## Contributing

I'm open to contributions! If you want to add features, fix bugs, or improve documentation, stay tuned! I will set up a CONTRIBUTING.md file someday with guidelines.

---

## License

Released under the [MIT license](LICENSE).

Do whatever you want with this code! I'd love to hear if you build something cool with it, and make jarvis really a productive tool for a lot of people in the community!!

---

## Credits

### Jarvis Project

Author: NhoaKing (2025)

Special thanks to my instant coffee for keeping me awake during those late-night sessions, and of course to the original repo by abcminiuser for the foundational work on the StreamDeck library.

### Upstream Library

Built on top of [python-elgato-streamdeck](https://github.com/abcminiuser/python-elgato-streamdeck) by Dean Camera.

Thanks to Alex Van Camp for the reverse engineering notes that made the original library possible.

Thanks to all the contributors to the upstream StreamDeck library (see the original repository for the full list).

---

## Questions?

If you run into issues:
1. Check the [Troubleshooting](#troubleshooting) section
2. Look at the logs: `journalctl --user -u jarvis.service -n 50`
3. I will try to implement an GitHub issue tracker soon, but for now, feel free to reach out via email:

nhoakingtec@gmail.com

---

**Last updated:** 2025-09-30