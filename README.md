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
- 👥 **Tagged Comment System** - Organized comments (#EDU, #NOTE, #FIXME, etc.) for documentation extraction
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

**Documentation Deployment:**
- 📖 Documentation is automatically deployed to GitHub Pages using Quartz
- 🔗 **View Live Documentation:** [https://nhoaking-tech.github.io/jarvis-streamdeck](https://nhoaking-tech.github.io/jarvis-streamdeck)
- 🎨 Custom dark-mode-only theme with color-coded text (bold=blue, italic=green, links=pink)
- 🤖 Fully automated via GitHub Actions on push to main
- 🔄 Local preview available with `quartz-preview/` setup

---

## Quick Links

| For Users | For Contributors | For Technical Writers |
|-----------|-----------------|---------------------|
| [Quick Start](#quick-start) | [Project Structure](#project-structure) | [Documentation System](#documentation-philosophy) |
| [Full Setup](#detailed-installation) | [Complete Workflow](#complete-workflow-summary) | [Git Hooks Setup](#git-hooks-setup) |
| [Troubleshooting](#troubleshooting) | [Git Workflow Guides](jarvis/git_docs/) | [Quartz Preview](#quartz-documentation-preview) |
| [Customization](#customization) | [Install Hooks](INSTALL_HOOKS.md) | [GitHub Pages Deploy](#github-pages-deployment) |

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

# 2. Run configuration setup from the original repo. You do not need to have an environment in python to run this, as it is just a setup script that generates a config file. But you do need to have the ydotool path ready, so make sure you have built ydotool from source first, as described in the Detailed Installation section.
cd jarvis && python3 config/setup_config.py

# 3. Set up Python environment
# I use conda because maybe I'll need this for data science workflows later. My environment is called jarvis-busybee, as it is paired with another project. If you want to name it differently, just remember to update the bash scripts later that use the jarvis-busybee environment.
conda create -n jarvis-busybee python=3.11.4
conda activate jarvis-busybee

# You can also use venv if you prefer, but you will need to modify the bash scripts accordingly, as they assume conda, and are set up for an environment named "jarvis-busybee".
# python3.11 -m venv jarvis-busybee
# source jarvis-busybee/bin/activate

# 4. Install Python dependencies
pip install -e .  # Install StreamDeck library in development mode
pip install "pillow>=9.0.0" hidapi

# 5. Install system dependencies
sudo apt install libhidapi-libusb0 libhidapi-hidraw0

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
|-- jarvis/                         # Main application package
|   |-- actions/                    # Action handlers for key presses
|   |   |-- __init__.py
|   |   |-- actions.py              # 50+ documented action functions
|   |-- config/                     # Configuration management
|   |   |-- __init__.py
|   |   |-- initialization.py       # Centralized module initialization
|   |   |-- config.env              # Your personal config (generated by setup_config.py)
|   |   |-- config_example.env      # Example configuration file
|   |-- core/                       # Application core logic
|   |   |-- __init__.py
|   |   |-- application.py          # Main application logic & lifecycle
|   |   |-- logic.py                # Event handling & layout switching
|   |   |-- lifecycle.py            # Resource cleanup & management
|   |-- ui/                         # User interface layer
|   |   |-- __init__.py
|   |   |-- layouts.py              # StreamDeck layout definitions
|   |   |-- render.py               # Visual rendering engine
|   |-- utils/                      # Utility modules
|   |   |-- __init__.py
|   |   |-- reset_jarvis.py         # Deck reset utility (use if layout gets stuck)
|   |   |-- terminal_prints.py      # Formatted console output
|   |   |-- extract_comments.py     # ⭐ Extract tagged comments from code
|   |   |-- generate_docs.py        # ⭐ Generate markdown from extracted comments
|   |   |-- strip_comments.py       # ⭐ Strip tagged comments for production
|   |   |-- pre-commit-hook.sh      # ⭐ Pre-commit git hook script
|   |   |-- post-commit-hook.sh     # ⭐ Post-commit git hook script
|   |-- assets/                     # Icons, fonts, scripts, snippets
|   |   |-- jarvisicons/            # Custom StreamDeck button icons
|   |   |-- bash_scripts/           # Executable bash scripts
|   |   |-- snippets/               # Code snippet text files
|   |   |-- font/                   # Font files for key rendering
|   |-- tests/                      # Testing utilities
|   |   |-- grid_test.py            # StreamDeck connection test
|   |-- docs/                       # Auto-generated documentation
|   |   |-- content/                # Markdown documentation files
|   |-- git_docs/                   # Documentation workflow guides
|   |   |-- README.md               # Documentation system overview
|   |   |-- 00-11_*.md              # Detailed workflow guides
|   |-- __init__.py                 # Package initialization
|   |-- __main__.py                 # Module entry point (enables python -m jarvis)
|   |-- main.sh                     # Shell entry point (for systemd service)
|   |-- setup_config.py             # Interactive configuration setup
|   |-- py.typed                    # PEP 561 type marker
|-- src/                      # Forked StreamDeck library (python-elgato-streamdeck)
|-- .git/hooks/               # Documentation automation hooks
|-- README.md                 # This file - comprehensive setup guide
```

### Recent Structure Changes

I recently reorganized the project structure for better maintainability. Here's what changed and why:

**What Changed:**
- Added `config/` directory for centralized configuration.
- Moved `lifecycle.py` and `logic.py` from `ui/` to new `core/` directory.
- Renamed `run_jarvis.py` → `application.py` (clearer naming).
- Renamed `run_jarvis.sh` → `main.sh` for consistency.
- Created `__main__.py` to enable module execution (`python -m jarvis`).
- Moved `reset_jarvis.py` to `utils/` (it's a utility, not core code).

**Why These Changes:**
- **Better Separation of Concerns**: Core logic in `core/`, UI code in `ui/`, config in `config/`, utilities in `utils/`.
- **Standard Python Module**: Using `__main__.py` enables proper package execution.
- **Clearer Naming**: `application.py` describes what it does better than `run_jarvis.py`.
- **Logical Grouping**: Config files grouped together makes more sense.
- **Standard Python Structure**: Follows Python package conventions.
- **Future-Proof**: Easier to extend and maintain.
- **Documentation Clarity**: Easier for new contributors to understand the project layout.

---

## Detailed Installation

Let's do the full setup properly. It can take a bit of time, especially if you're new to Linux system configuration, but I'll guide you through every step. The amount of time you spend configuring your streamdeck for your productivity workflows depends on how complex you want it to be. At the moment I have only a few actions, representative of the kind of workflows you can automate. You can add your custom bash scripts, snippets, and actions as you see fit. You can add git workflows too. At the moment I provided an simple example with a commit action. The productivity gain (and cognitive load reduction) is worth the initial setup time investment.

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
- `EnvironmentFile` - Where your `config.env` file is (used by systemd to set environment variables)
- `WorkingDirectory` - Your jarvis directory
- `ExecStart` - Path to `main.sh`

**Note about config.env loading:**
The `EnvironmentFile` directive makes environment variables available to the systemd service. Additionally, `main.sh` sources the config file, and the Python application also loads it automatically at startup. This redundancy ensures configuration is available regardless of how jarvis is run (systemd service, manual execution, etc.).

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

# Stop jarvis temporarily (useful for debugging, in which case I need to then run jarvis/utils/reset_jarvis.py to reset the deck. Then I run python -m jarvis manually to see any errors)
systemctl --user stop jarvis.service

# If the script works as expected, start the service again. Do not run python -m jarvis while the service is running, as it will conflict because the service is already using the StreamDeck. Also, DO NOT RUN FROM INTEGRATED TERMINAL IN VSCODE, as it messes up the environment. Always use a native terminal, as the script will not run the same as it does in a native terminal, and you will waste hours debugging like I did, when actually there is no problem with the code... when running from native terminal, it works fine.
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
alias jarvis-stop='systemctl --user stop jarvis.service'
alias jarvis-start='systemctl --user start jarvis.service'
alias jarvis-journal='journalctl --user -u jarvis.service -f'
alias jarvis-status='systemctl --user status jarvis.service'
alias jarvis-reset='conda activate jarvis-busybee && python ~/Zenith/jarvis-streamdeck/jarvis/utils/reset_jarvis.py'
# Replace the last alias with the name of your environment and the correct path to reset_jarvis.py. If you do not use conda, just remove the conda activate <env> command, and make sure python points to the correct Python interpreter. In Linux the you may need to use python3 instead of python.
alias jarvis-test='conda activate jarvis-busybee && cd ~/Zenith/jarvis-streamdeck && python -m jarvis'
# Again, replace with your environment name and correct path. This is useful for testing changes to code without starting the service. Make sure the service has not been initialized, or stop it first, before testing your changes with this command, as the service will conflict with this command if it is already running and using the StreamDeck. It is very useful for debugging. Get out of the testing mode with Ctrl+C.
```

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

**How it works:**
The config file is **automatically loaded** by jarvis at startup (see [core/application.py](jarvis/core/application.py) `load_config()` function). You don't need to manually source it - just run `python -m jarvis` and the configuration will be loaded automatically.

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
cd ~/Zenith/jarvis-streamdeck  # or wherever you cloned the repo
python -m jarvis
# Your StreamDeck should light up with the main layout
# Press Ctrl+C to stop

# 5. Test jarvis service
systemctl --user status jarvis.service
# Should show "active (running)" in green
```

**⚠️ Important about VSCode terminal:**
If you run `python -m jarvis` from VSCode's integrated terminal, it might not work properly. This is because VSCode's terminal has a different environment than your native terminal. System tools like ydotool and wmctrl sometimes don't work correctly in VSCode's terminal. Always test from a native terminal (gnome-terminal, konsole, xterm, etc.).

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
# Add a button with an icon.
# Default background color is black if not specified.
<key_index>: {"icon": "project1.png", "action": actions.open_vscode(str(projects_path / 'project_name'))}

# Add a button with a label (text).
# The default for the label color is white if not specified.
# We can specify a background color. 
<key_index>: {"label": "List envs", "color": "#1c2e1c", "action": actions.type_text("conda env list\n")}

# Mix and match: Add a button with label and icon.
# Customize label color and background color (defaults are white and black, respectively).
<key_index>: {"label": "Zenith", "labelcolor": "#000000", "icon": "nautilus.png", "color": "#bbbbbb", "action": lambda: actions.nautilus_path(str(projects_path))}
```

**After making changes:**
```bash
systemctl --user restart jarvis.service
```

or if you set up the alias:
```bash
jarvis-restart
```

You can also add your custom actions in `jarvis/actions/actions.py` and then use them in layouts.py (see [How to Add Custom Actions](#how-to-add-custom-actions) below). Also, you can modify the icons in `assets/jarvisicons/` to customize the look of your buttons (see [How to Modify Icons](#how-to-modify-icons) below).

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

### How to Modify Icons

You can also modify the icons in `assets/jarvisicons/` to customize the look of your buttons.
I use mainly [Flatikon](https://www.flaticon.com/) for icons, as they have a huge selection of free icons.
Other good sources are:
- [WikimediaCommons](https://commons.wikimedia.org/wiki/Main_Page)
- [RemixIcon](https://remixicon.com/).
- [Google Material Icons](https://fonts.google.com/icons).

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
cd /path/to/jarvis-streamdeck
python -m jarvis
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

### Tagged Comment System

One of the things I'm most proud of in this project is the documentation system. I created a tagged comment system that lets me organize documentation in the same codebase while keeping production code clean:

```python
# EDU: Educational content - design patterns, CS concepts
# Explains the "why" and "how" for learners

# NOTE: Implementation notes and important details
# Critical information for developers

# TODO: Future improvements
# Planned enhancements

# FIXME: Known issues that need fixing
# Bugs to address

# And more: TOCLEAN, HACK, DEBUG, IMPORTANT, REVIEW, OPTIMIZE
```

**Why I built this:**
I was frustrated with documentation always drifting out of sync with code. Separate documentation files get stale, but too many code comments make the code hard to read. I wanted a system where:
1. Documentation lives with the code (never out of sync)
2. I can be as detailed as I want without cluttering production code
3. Documentation automatically updates when code changes
4. I can generate beautiful docs from these comments

**How it works:**
The documentation pipeline has three main components:

1. **`extract_comments.py`** - Parses Python files and extracts tagged comments into structured data
2. **`generate_docs.py`** - Converts extracted comments into beautiful markdown documentation
3. **Git hooks** - Automatically run extraction before every commit

```bash
# Pre-commit hook workflow:
1. You commit code with tagged comments
2. Hook detects changed Python files
3. Extracts comments → generates markdown
4. Stages markdown files
5. Commit completes with docs included
```

Documentation is stored in `jarvis/docs/content/` and deployed to GitHub Pages via Quartz (a static site generator). The workflow is fully automated - I write code with comments, commit, and the docs update automatically.

For complete details on the documentation workflow, see **[jarvis/git_docs/](jarvis/git_docs/)** which contains comprehensive guides:
- Tag usage and best practices
- Git hooks setup and automation
- Quartz preview configuration
- GitHub Pages deployment
- Troubleshooting guides

### Automated Documentation Generation

My git hooks automatically generate documentation before every commit. This is a game-changer for keeping documentation in sync with code.

```bash
# .git/hooks/pre-commit (simplified view)
#!/usr/bin/env bash
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/
git add jarvis/docs/content/
```

**What this means:**
- Documentation is always up-to-date with code
- No manual documentation generation steps
- Changes to code automatically update docs
- No more "forgot to update the docs" commits
- Deployed automatically to GitHub Pages via GitHub Actions

### Git Hooks Setup

The repository includes pre-commit and post-commit hooks that automate the entire documentation workflow:

**Pre-Commit Hook** (`jarvis/utils/pre-commit-hook.sh`):
- Runs on `dev` branch when you commit changes
- Detects modified Python files in `jarvis/`
- Automatically generates markdown documentation
- Stages documentation files for inclusion in commit
- On `main` branch: blocks commits with tagged comments (keeps production clean)

**Post-Commit Hook** (`jarvis/utils/post-commit-hook.sh`):
- Runs after successful commit on `dev` branch
- Updates local Quartz preview automatically
- Copies generated docs to `quartz-preview/content/`
- Ready for local preview with `npx quartz build --serve`

**Installation:**
```bash
# Quick install (from repository root)
cp jarvis/utils/pre-commit-hook.sh .git/hooks/pre-commit
cp jarvis/utils/post-commit-hook.sh .git/hooks/post-commit
chmod +x .git/hooks/pre-commit .git/hooks/post-commit
```

For detailed setup instructions, see **[INSTALL_HOOKS.md](INSTALL_HOOKS.md)**.

### Quartz Documentation Preview

The repository includes a local Quartz setup for previewing documentation before deployment:

**Location**: `quartz-preview/` directory

**Features**:
- Dark mode only (no light theme toggle)
- Custom color scheme:
  - Bold text: Blue (`#6fa8dc`)
  - Italic text: Green (`#93c47d`)
  - Links: Pink (`#ff69b4`)
  - Highlights: Pinkish (`#ff69b488`)
- Automatically updated by post-commit hook

**Usage**:
```bash
cd quartz-preview
npx quartz build --serve
# Opens preview at http://localhost:8080
```

For setup and configuration details, see **[jarvis/git_docs/09_QUARTZ_PREVIEW.md](jarvis/git_docs/09_QUARTZ_PREVIEW.md)**.

### GitHub Pages Deployment

Documentation is automatically deployed to GitHub Pages when you push to `main`:

**Workflow**: `.github/workflows/deploy-docs.yml`

**What happens automatically**:
1. GitHub Actions detects push to `main` with changes in `jarvis/docs/`
2. Clones fresh Quartz installation
3. Copies documentation from `jarvis/docs/content/`
4. Copies custom theme and layout from `quartz-preview/`
5. Builds static site
6. Deploys to GitHub Pages

**Deployment URL**: `https://<username>.github.io/jarvis-streamdeck/`

**Configuration**:
- Page title: "Jarvis StreamDeck Documentation"
- Same custom theme as local preview
- Fully automated - no manual deployment steps

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

## Complete Workflow Summary

Here's the entire development and documentation workflow in action:

### Daily Development Workflow

```bash
# 1. Work on dev branch (with all tagged comments)
git checkout dev

# 2. Make changes to code with tagged comments
# Edit jarvis/actions/actions.py, add #EDU, #NOTE comments, etc.

# 3. Commit changes
git add .
git commit -m "Add new feature with documentation"

# ↓ Pre-commit hook runs automatically:
#   - Extracts tagged comments
#   - Generates markdown files in jarvis/docs/content/
#   - Stages documentation files

# ↓ Post-commit hook runs automatically:
#   - Updates quartz-preview/content/
#   - Ready for local preview

# 4. Preview documentation locally (optional)
cd quartz-preview && npx quartz build --serve

# 5. When ready for production, merge to main
git checkout main
git merge --squash dev
git commit -m "Release: Add new feature"

# 6. Push to GitHub
git push origin main

# ↓ GitHub Actions runs automatically:
#   - Builds Quartz site from jarvis/docs/content/
#   - Applies custom theme from quartz-preview/
#   - Deploys to GitHub Pages

# 7. Documentation is live!
# Visit: https://<username>.github.io/jarvis-streamdeck/
```

### Branch Strategy

- **`dev`** (local only):
  - Full code with ALL tagged comments (#EDU, #NOTE, etc.)
  - Messy commit history - all your experiments
  - Never pushed to GitHub

- **`main`** (pushed to GitHub):
  - Clean production code (tagged comments stripped)
  - Generated documentation files included
  - Clean commit history (squash merged from dev)
  - Auto-deployed to GitHub Pages

### Key Files and Locations

```
jarvis-streamdeck/
├── jarvis/
│   ├── utils/
│   │   ├── extract_comments.py      # Comment extraction
│   │   ├── generate_docs.py         # Markdown generation
│   │   ├── strip_comments.py        # Clean code for production
│   │   ├── pre-commit-hook.sh       # Pre-commit automation
│   │   └── post-commit-hook.sh      # Post-commit automation
│   ├── docs/
│   │   └── content/                 # Generated markdown docs
│   └── git_docs/                    # Workflow documentation
├── quartz-preview/                  # Local Quartz installation
│   ├── quartz.config.ts             # Quartz configuration
│   ├── quartz.layout.ts             # Layout (no dark mode toggle)
│   └── quartz/styles/custom.scss    # Custom theme colors
├── .git/hooks/
│   ├── pre-commit                   # Installed hook
│   └── post-commit                  # Installed hook
└── .github/workflows/
    └── deploy-docs.yml              # GitHub Pages deployment
```

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

Special thanks to my instant coffee for keeping me awake during those late-night sessions, and of course to the **original repo by abcminiuser for the foundational work on the StreamDeck library**.

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

nhoakingtech@gmail.com

---

**Last updated:** 2025-09-30