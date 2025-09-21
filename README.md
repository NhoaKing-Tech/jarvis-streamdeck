# Jarvis StreamDeck Automation System

*Extended from [python-elgato-streamdeck](https://github.com/abcminiuser/python-elgato-streamdeck)*

A personal automation system that transforms your Elgato StreamDeck XL into a powerful Linux productivity control center. This fork extends the base StreamDeck library with custom workflow automation capabilities.

## Jarvis Personal Assistant

A custom StreamDeck XL control system that transforms your Elgato StreamDeck into a powerful productivity automation tool for Linux environments.

### Overview

Jarvis is a personal automation system built on top of the [python-elgato-streamdeck](https://github.com/abcminiuser/python-elgato-streamdeck) library. It provides a customizable interface for controlling system operations, launching applications, executing shortcuts, and managing development workflows through StreamDeck hardware.

### Project Structure v0.6 (Final)

```
jarvis/
├── actions/
│   ├── __init__.py
│   └── actions.py # Core action functions triggered by key presses
├── assets/
│   ├── bash_scripts/ # Shell scripts for system operations
│   ├── font/ # Custom fonts for button text rendering
│   ├── jarvisicons/ # Custom icon set for StreamDeck buttons
│   └── snippets/ # Code snippets and templates
├── config/
│   ├── __init__.py
│   ├── config.env # Environment configuration (user-specific)
│   ├── initialization.py # Centralized module initialization
│   └── setup_config.py # Interactive configuration setup through terminal
├── core/
│   ├── __init__.py
│   ├── application.py # Core application logic (formerly run_jarvis.py)
│   ├── lifecycle.py # Resource management and cleanup
│   └── logic.py # Event handling and layout switching
├── ui/
│   ├── __init__.py
│   ├── layouts.py # Layout definitions and configurations
│   └── render.py # Visual rendering and layout management
├── utils/
│   ├── __init__.py
│   ├── reset_jarvis.py # System reset utility script
│   └── terminal_prints.py # Testing utilities
├── tests/
│   └── grid_test.py # Testing utilities
├── config_example.env # Configuration example with extra information for clarity
├── main.py # Python entry point
└── main.sh # Shell entry point (formerly run_jarvis.sh)
```

### Recent Structure Changes (v0.6)

**What Changed:**
- Moved `lifecycle.py` and `logic.py` from `ui/` to new `core/` directory for better organization
- Renamed `run_jarvis.py` → `application.py` and moved to `core/` (clearer naming for core logic)
- Renamed `run_jarvis.sh` → `main.sh` and moved to root (consistent with `main.py` entry point)
- Created `main.py` as the clean Python entry point that delegates to `core.application`
- Moved `config.env` and `setup_config.py` to `config/` directory for logical grouping
- Moved `reset_jarvis.py` to `utils/` directory as it's a utility script
- Added `config/` directory for centralized module initialization and configuration files
- Updated all import statements and documentation to reflect new structure

**Why These Changes:**
- **Better Separation of Concerns**: Core business logic in `core/`, UI code in `ui/`, config in `config/`, utilities in `utils/`
- **Consistent Entry Points**: Both `main.py` and `main.sh` are entry points at the same directory level
- **Clearer Naming**: `application.py` better describes core app logic than `run_jarvis.py`
- **Logical Grouping**: Configuration files and setup scripts now grouped together in `config/`
- **Standard Python Structure**: Follows Python package conventions with clear module boundaries
- **Future-Proof**: Easier to extend and maintain with well-organized, focused directories

**Migration Impact:**
- Service configuration needs to be updated to use the new entry point
- Import paths have been updated throughout the codebase
- All functionality remains the same - only internal organization changed

### Migrating from v0.5 to v0.6

If you have an existing Jarvis installation, follow these steps to migrate to the new structure:

#### 1. Stop Current Services
```bash
# Stop jarvis service before making changes
systemctl --user stop jarvis.service
```

#### 2. Update Service Configuration
Edit your systemd service file:
```bash
nano ~/.config/systemd/user/jarvis.service
```

Update the paths in the service file:
```ini
# Change EnvironmentFile from:
EnvironmentFile=/path/to/jarvis-streamdeck/jarvis/config.env
# To:
EnvironmentFile=/path/to/jarvis-streamdeck/jarvis/config/config.env

# Change ExecStart from:
ExecStart=/path/to/jarvis-streamdeck/jarvis/run_jarvis.sh
# To:
ExecStart=/path/to/jarvis-streamdeck/jarvis/main.sh
```

#### 3. Update File Permissions
```bash
# Make sure the new script location is executable
chmod u+x /path/to/jarvis-streamdeck/jarvis/main.sh
```

#### 4. Reload and Restart Services
```bash
# Reload systemd configuration
systemctl --user daemon-reload

# Restart jarvis service
systemctl --user restart jarvis.service

# Check service status
systemctl --user status jarvis.service
```

#### 5. Verify Migration
```bash
# Test manual execution with new entry point
cd /path/to/jarvis-streamdeck/jarvis
python main.py

# Check logs for any issues
journalctl --user -u jarvis.service -f
```

**Note**: If you've customized any scripts or have automated tools that reference the old paths, update them to use:
- `main.py` instead of `run_jarvis.py` as the Python entry point
- `main.sh` instead of `run_jarvis.sh` for the shell script
- `config/config.env` instead of `config.env` for the configuration file

### Key Features

- **Custom Action System**: Programmable button actions for system control, application launching, and workflow automation
- **Multi-Layout Support**: Dynamic layout switching for different contexts
- **Linux Integration**: Deep integration with Linux desktop environments through ydotool, wmctrl, and system tools
- **Visual Customization**: Custom icon rendering with text overlays and dynamic button states
- **Service Integration**: Designed to run as a systemd service so that jarvis runs from startup at all times
- **Configuration Management**: Environment-based configuration system for easy customization

### Dependencies

#### Base Library
Built on top of the original [python-elgato-streamdeck](https://github.com/abcminiuser/python-elgato-streamdeck) repository, extending its core functionality with:

- Custom UI rendering system
- Action framework for system integration
- Layout management for multiple button configurations
- Asset management for icons and visual elements

#### Python Dependencies
- **streamdeck (0.9.8)**: Core StreamDeck hardware library (from forked repository - installed with `pip install -e .` in editable mode)
- **Pillow >= 9.0.0**: Image processing and manipulation for StreamDeck button rendering (`PIL.Image`, `PIL.ImageDraw`, `PIL.ImageFont`)
- **hidapi**: USB device communication library (required by StreamDeck library)
- **pathlib**: Modern path handling (part of Python standard library)

**Note**: Other packages like `pyautogui`, `pyperclip`, etc. may be installed in your environment but are not currently used by the jarvis codebase.

#### System Dependencies
- **libhidapi-libusb0**: Low-level USB HID device access library (required for StreamDeck communication)
- **libhidapi-hidraw0**: Alternative HID raw device access library (required for StreamDeck communication)
- **ydotool**: Wayland/X11 compatible input simulation tool for hotkey execution

  **Note on ydotool vs xdotool**: While jarvis currently runs on X11 and could use xdotool instead of ydotool, the decision to use ydotool was made during initial development when jarvis was designed for Wayland. When switching to X11, ydotool continued to work fine, so the change to xdotool was deemed unnecessary. This also keeps the door open for future Wayland compatibility without major code changes.
- **wmctrl**: X11 window management utility for application control and smart window handling
- **playerctl**: Media player control for Spotify integration
- **alsa-utils**: Audio mixer control for microphone toggle (provides amixer)
- **nautilus**: GNOME file manager for directory navigation
- **gnome-terminal**: Terminal emulator for bash script execution
- **xdg-utils**: Desktop integration utilities for opening files and URLs (provides xdg-open)
- **cmake**: Required for building ydotool from source
- **build-essential**: Compilation tools for building ydotool
- **libevdev-dev**: Development files for libevdev (required for ydotool build)
- **scdoc**: Simple document format for man pages (required for ydotool build)
- **procps**: Process utilities (provides pgrep, usually pre-installed)

#### Hardware Requirements
- **Elgato StreamDeck XL**: 32-key version specifically (other variants not tested)
- **USB connection**: Direct USB connection to Linux system
- **Proper udev rules**: For device access permissions

### System Requirements

- Linux environment (developed and tested on Ubuntu/Debian)
- **X11 display server** (Wayland is not supported - had to switch to X11 due to compatibility issues)
- Python 3.11.4 (recommended, tested with conda environment)
- Elgato StreamDeck XL hardware
- ydotool (for hotkey simulation)
- wmctrl (for window management)
- Additional system tools as configured

### Project Status

⚠️ **This project is in active development and not considered finished.** The functionality will be extended and evolved as new requirements emerge. Current implementation provides core StreamDeck automation but additional features are planned for future releases.

### Usage

#### Environment Setup

1. **Create conda environment with Python 3.11.4:**
   ```bash
   conda create -n jarvis python=3.11.4
   conda activate jarvis
   ```
   You can use a different way of handling the environment, but I use conda since maybe I will need this environment to also support some data science workflows.

2. **Install system dependencies:**
   ```bash
   # For Ubuntu/Debian systems - install HID device access libraries:
   sudo apt install libhidapi-libusb0 libhidapi-hidraw0

   # Install additional system dependencies required by jarvis actions:
   sudo apt install wmctrl playerctl alsa-utils nautilus gnome-terminal xdg-utils

   # Install ydotool build dependencies:
   sudo apt update
   sudo apt upgrade
   sudo apt install git cmake build-essential libevdev-dev scdoc
   ```

3. **Build and install ydotool from source:**
   ```bash
   # Clone and build ydotool:
   git clone https://github.com/ReimuNotMoe/ydotool.git
   cd ydotool
   mkdir build && cd build
   cmake ..
   make -j $(nproc)
   # Note the path to the built ydotool binary (/path/to/ydotool/build/ydotool) for configuration
   ```

4. **Install optional applications that jarvis can control:**
   ```bash
   # Visual Studio Code (choose one method):
   # Method 1: Download from https://code.visualstudio.com/
   # Method 2: Using snap
   sudo snap install code --classic
   # Method 3: Using apt (after adding Microsoft repository)

   # Spotify (choose one method):
   sudo snap install spotify
   # Or download from https://www.spotify.com/

   # Obsidian (if using vault functions):
   # Download from https://obsidian.md/
   ```

5. **Set up user permissions:**
   ```bash
   # Add your user to the uinput group (required for ydotool):
   sudo usermod -a -G uinput $USER
   # Log out and log back in for group changes to take effect
   ```

6. **Install Python dependencies:**
   ```bash
   # Install Python dependencies separately for version control:
   pip install "pillow>=9.0.0"
   pip install hidapi

   # Install the streamdeck library in editable mode from the parent directory:
   cd ..  # Navigate to the parent directory (jarvis-streamdeck root)
   pip install -e .
   cd jarvis  # Return to jarvis directory
   ```

   **Why editable install (`-e`)**: This installs the streamdeck library from your local forked repository in "development mode". Any changes you make to the StreamDeck library code will immediately be available to jarvis without reinstalling. This is essential because jarvis imports from the forked repository's `src/` directory.

   **Why `pip install -e .` instead of `python setup.py install`**:
   - **Modern Standard**: `python setup.py install` is deprecated and discouraged by the Python packaging community
   - **Dependency Management**: `pip` properly handles all dependencies listed in `setup.py`, while `setup.py install` often misses them
   - **Uninstallation**: Easy removal with `pip uninstall streamdeck` (no clean uninstall method exists for `setup.py install`)
   - **Virtual Environment Safety**: `pip` is virtual environment aware and won't accidentally install system-wide
   - **Package Tracking**: `pip list` shows pip-installed packages, but not those installed via `setup.py install`
   - **Professional Standard**: This is how modern Python developers install packages from source

#### StreamDeck Hardware Setup

1. **Set up udev rules for StreamDeck access:**
   ```bash
   # Create StreamDeck permissions rule (requires sudo):
   sudo nano /etc/udev/rules.d/60-jarvis.rules

   # Add the following content (adjust idProduct for your StreamDeck model):
   SUBSYSTEM=="usb", ATTR{idVendor}=="0fd9", ATTR{idProduct}=="008f", MODE="0666"

   # For other StreamDeck models, check with: lsusb | grep -i elgato
   # Common StreamDeck device IDs:
   # - StreamDeck XL: idProduct=="008f"
   # - StreamDeck Original: idProduct=="0060"
   # - StreamDeck Mini: idProduct=="0063"
   ```

2. **Set up ydotool udev rule:**
   ```bash
   # Create ydotool udev rule:
   sudo nano /etc/udev/rules.d/99-uinput.rules

   # Add the following content:
   KERNEL=="uinput", MODE="0660", GROUP="uinput", OPTIONS+="static_node=uinput"
   ```

3. **Set up jarvis auto-start udev rule (optional):**
   ```bash
   # Create jarvis auto-start rule:
   sudo nano /etc/udev/rules.d/99-jarvis-autostart.rules

   # Add the following content (adjust idProduct for your StreamDeck model):
   ACTION=="add", SUBSYSTEM=="usb", ATTR{idVendor}=="0fd9", ATTR{idProduct}=="008f", TAG+="systemd", ENV{SYSTEMD_USER_WANTS}+="jarvis.service"
   ACTION=="remove", SUBSYSTEM=="usb", ATTR{idVendor}=="0fd9", ATTR{idProduct}=="008f", TAG+="systemd", ENV{SYSTEMD_USER_STOP}+="jarvis.service"
   ```

4. **Reload udev rules:**
   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

   **Note on udev rule numbering**: The numbers in udev rule filenames (60-, 99-) are intentional. udev rules are processed in numerical order, with higher numbers running later. This ensures the correct execution order for ydotool and USB device setup.

5. **Ensure your user has access to the device** (unplug and replug StreamDeck if needed)

#### Service Configuration

1. **Set up ydotool service** (required for hotkey functionality):
   ```bash
   # Create user systemd service directory:
   mkdir -p ~/.config/systemd/user

   # Create ydotool service file:
   nano ~/.config/systemd/user/ydotoold.service
   ```

   Service content:
   ```ini
   [Unit]
   Description=ydotoold daemon (Wayland key injection)

   [Service]
   ExecStart=/path/to/your/ydotool/build/ydotoold
   Restart=always

   [Install]
   WantedBy=default.target
   ```

2. **Set up Jarvis service** (for automatic startup):
   ```bash
   # Create jarvis service file:
   nano ~/.config/systemd/user/jarvis.service
   ```

   Service content:
   ```ini
   [Unit]
   Description=Jarvis StreamDeck Service
   After=graphical.target

   [Service]
   Type=simple
   EnvironmentFile=/path/to/jarvis-streamdeck/jarvis/config/config.env
   WorkingDirectory=/path/to/jarvis-streamdeck/jarvis
   ExecStartPre=/bin/sleep 10
   ExecStart=/path/to/jarvis-streamdeck/jarvis/main.sh
   Restart=on-failure

   [Install]
   WantedBy=default.target
   ```

3. **Configure the launch script:**
   ```bash
   # Edit main.sh to customize for your system:
   nano /path/to/jarvis-streamdeck/jarvis/main.sh

   # Update these lines to match your setup:
   # 1. Change the conda environment name:
   # conda activate jarvis-busybee  # Change to your environment name
   # conda activate jarvis          # Example: if you created 'jarvis' environment

   # 2. If using a different conda installation path, update:
   # source ~/miniconda3/etc/profile.d/conda.sh  # Change if conda is elsewhere
   ```

   **Note**: The script now automatically uses the `PROJECTS_DIR` environment variable from your `config.env` file to locate the jarvis installation and uses `main.py` as the entry point. This makes the script portable across different systems.

4. **Set up file permissions:**
   ```bash
   # Make the run_jarvis.sh script executable (user only for security):
   chmod u+x /path/to/jarvis-streamdeck/jarvis/core/run_jarvis.sh
   ```

4. **Enable and start services:**
   ```bash
   # Reload systemd daemon to recognize new service files:
   systemctl --user daemon-reload

   # Enable and start ydotool service:
   systemctl --user enable ydotoold.service
   systemctl --user start ydotoold.service

   # Enable and start jarvis service:
   systemctl --user enable jarvis.service
   systemctl --user start jarvis.service

   # Check service status:
   systemctl --user status ydotoold.service
   systemctl --user status jarvis.service
   ```

5. **Service management commands:**
   ```bash
   # View service logs:
   journalctl --user -u jarvis.service -f

   # Restart jarvis after making changes:
   systemctl --user restart jarvis.service

   # Stop/start jarvis temporarily (toggle on/off, doesn't affect startup behavior):
   systemctl --user stop jarvis.service
   systemctl --user start jarvis.service
   ```

**Setup Summary**: After completing all the above steps, you will have:
- The **permissions rule** (`60-jarvis.rules`) to avoid needing `sudo` for StreamDeck access
- The **auto-start rule** (`99-jarvis-autostart.rules`) to automatically link the device to `jarvis.service`
- The **systemd service** (`jarvis.service`) to manage Jarvis with auto-restart and proper environment setup

#### Configuration

1. **Run the configuration setup:**
   ```bash
   cd jarvis/
   python config/setup_config.py
   ```

   This will create your `config/config.env` file with the necessary paths.

2. **Manual configuration** (edit `config/config.env`):
   - `YDOTOOL_PATH`: Path to your built ydotool binary (e.g., `/home/username/ydotool/build/ydotool`)
   - `PROJECTS_DIR`: Your main projects directory (e.g., `/home/username/projects`)
   - `OBSIDIAN_VAULT_journal`: Path to your journal Obsidian vault (optional)
   - `OBSIDIAN_VAULT_quartz`: Path to your documentation Obsidian vault (optional)
   - `KEYRING_PW`: Password for keyring/password manager access (optional)

   **Security Note**: Be careful when storing passwords in plain text files. Consider using password managers or SSH keys for better security.

See `config_example.env` for a complete configuration template and detailed setup instructions.

#### Running Jarvis

```bash
# Direct execution (for testing):
cd jarvis/
python main.py

# Or via shell script:
./main.sh

# Check service status:
systemctl --user status jarvis.service
```

**Important:** Execute from a regular Linux terminal, not from VSCode terminal, as system calls to tools like ydotool and wmctrl may not work properly in VSCode's integrated terminal.

### Verification Steps

Test each component before proceeding to the next:

```bash
# 1. Test ydotool installation:
~/ydotool/build/ydotool type "hello world"

# 2. Test StreamDeck detection:
lsusb | grep -i elgato

# 3. Test Python environment:
source jarvis-env/bin/activate && python -c "import hidapi; print('HID access OK')"

# 4. Test jarvis script manually:
source jarvis-env/bin/activate && python main.py

# 5. Test service status:
systemctl --user status jarvis.service
```

### Troubleshooting

#### Common Issues and Solutions

##### "Permission denied" errors:
- Make sure all scripts have executable permissions: `ls -la run_jarvis.sh`
- Ensure user is in uinput group: `groups $USER | grep uinput`
- Check udev rules are loaded: `sudo udevadm control --reload-rules && sudo udevadm trigger`
- Verify file permissions are set correctly

##### Service fails to start:
- Check logs: `journalctl --user -u jarvis.service -n 50`
- Verify paths in service file match your system
- Test script manually first (use native terminal, not VSCode - environment differs!)
- Ensure all dependencies are installed

##### StreamDeck not detected:
- Check USB connection: `lsusb`
- Verify correct idVendor/idProduct in udev rules
- Try different USB port
- Unplug and replug the StreamDeck device
- Check device permissions: `ls -l /dev/input/`

##### ydotool not working:
- Check if ydotoold service is running: `systemctl --user status ydotoold`
- Test manually: `~/ydotool/build/ydotool type "test"`
- Verify udev rule for uinput device exists and is correct
- Ensure user is in uinput group and logged out/in after adding

##### Python import errors:
- Verify virtual environment is activated
- Check that all dependencies are installed: `pip list`
- Ensure editable install was successful: `pip show streamdeck`
- Test imports individually: `python -c "import PIL; import hidapi; print('OK')"`

### Author

NhoaKing (2025)

This project extends the excellent work of the python-elgato-streamdeck community, providing a personalized automation layer for enhanced productivity workflows.

---

# Python Elgato Stream Deck Library

![Example Deck](ExampleDeck.jpg)

This is an open source Python 3 library to control an
[Elgato Stream Deck](https://www.elgato.com/en/gaming/stream-deck) directly,
without the official software. This can allow you to create your own custom
front-ends, such as a custom control front-end for home automation software.

_________________

[PyPi Project Entry](https://pypi.org/project/streamdeck/) - [Online Documentation](https://python-elgato-streamdeck.readthedocs.io) - [Source Code](https://github.com/abcminiuser/python-elgato-streamdeck)


## Project Status:

Working - you can enumerate devices, set the brightness of the panel(s), set
the images shown on each button, and read the current button states.

Currently the following StreamDeck products are supported in multiple hardware
variants:

* StreamDeck 6 Key, 15 Key and 32 Key Modules
* StreamDeck Mini
* StreamDeck Neo
* StreamDeck Original
* StreamDeck Pedal
* StreamDeck Plus
* StreamDeck XL

## Package Installation:

Install the library via pip:

```
pip install streamdeck
```

Alternatively, manually clone the project repository:

```
git clone https://github.com/abcminiuser/python-elgato-streamdeck.git
```

For detailed installation instructions, refer to the prebuilt
[online documentation](https://python-elgato-streamdeck.readthedocs.io), or
build the documentation yourself locally by running `make html` from the `docs`
directory.


## Credits:

I've used the reverse engineering notes from
[this GitHub](https://github.com/alvancamp/node-elgato-stream-deck/blob/master/NOTES.md)
repository to implement this library. Thanks Alex Van Camp!

Thank you to the following contributors, large and small, for helping with the
development and maintenance of this library:

- [admiral0](https://github.com/admiral0)
- [Aetherdyne](https://github.com/Aetherdyne)
- [Benargee](https://github.com/Benargee)
- [benedikt-bartscher](https://github.com/benedikt-bartscher)
- [brimston3](https://github.com/brimston3)
- [BS-Tek](https://github.com/BS-Tek)
- [Core447](https://github.com/Core447)
- [dirkk0](https://github.com/dirkk0)
- [dodgyrabbit](https://github.com/dodgyrabbit)
- [dubstech](https://github.com/dubstech)
- [Giraut](https://github.com/Giraut)
- [impala454](https://github.com/impala454)
- [iPhoneAddict](https://github.com/iPhoneAddict)
- [itsusony](https://github.com/itsusony)
- [jakobbuis](https://github.com/jakobbuis)
- [jmudge14](https://github.com/jmudge14)
- [jonbloom](https://github.com/jonbloom)
- [Kalle-Wirsch](https://github.com/Kalle-Wirsch)
- [karstlok](https://github.com/karstlok)
- [Lewiscowles1986](https://github.com/Lewiscowles1986)
- [m-weigand](https://github.com/m-weigand)
- [mathben](https://github.com/mathben)
- [matrixinius](https://github.com/matrixinius)
- [phillco](https://github.com/phillco)
- [pointshader](https://github.com/pointshader)
- [pylogger-html](https://github.com/pylogger-html)
- [shanna](https://github.com/shanna)
- [spidererrol](https://github.com/Spidererrol)
- [spyoungtech](https://github.com/spyoungtech)
- [Subsentient](https://github.com/Subsentient)
- [swedishmike](https://github.com/swedishmike)
- [TheSchmidt](https://github.com/TheSchmidt)
- [theslimshaney](https://github.com/theslimshaney)
- [tjemg](https://github.com/tjemg)
- [VladFlorinIlie](https://github.com/VladFlorinIlie)

If you've contributed in some manner, but I've accidentally missed you in the
list above, please let me know.


## License:

Released under the [MIT license](LICENSE).
