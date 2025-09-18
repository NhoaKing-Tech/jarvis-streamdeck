# Jarvis StreamDeck

A custom StreamDeck XL control system that transforms your Elgato StreamDeck into a powerful productivity automation tool for Linux environments.

## Overview

Jarvis is a personal automation system built on top of the [python-elgato-streamdeck](https://github.com/abcminiuser/python-elgato-streamdeck) library. It provides a customizable interface for controlling system operations, launching applications, executing shortcuts, and managing development workflows through StreamDeck hardware.

## Project Structure

```
jarvis/
├── actions/
│   ├── __init__.py
│   └── actions.py          # Core action functions triggered by key presses
├── assets/
│   ├── bash_scripts/       # Shell scripts for system operations
│   ├── font/              # Custom fonts for button text rendering
│   ├── jarvisicons/       # Custom icon set for StreamDeck buttons
│   └── snippets/          # Code snippets and templates
├── ui/
│   ├── __init__.py
│   ├── lifecycle.py       # Resource management and cleanup
│   ├── logic.py          # Event handling and layout switching
│   └── render.py         # Visual rendering and layout management
├── tests/
│   └── grid_test.py      # Testing utilities
├── config.env            # Environment configuration (user-specific)
├── config_example.env    # Configuration template
├── reset_jarvis.py       # System reset utility
├── run_jarvis.py         # Main application entry point
├── run_jarvis.sh         # Shell launcher script
└── setup_config.py      # Interactive configuration setup
```

## Key Features

- **Custom Action System**: Programmable button actions for system control, application launching, and workflow automation
- **Multi-Layout Support**: Dynamic layout switching for different contexts (development, media, system tools)
- **Linux Integration**: Deep integration with Linux desktop environments through ydotool, wmctrl, and system tools
- **Visual Customization**: Custom icon rendering with text overlays and dynamic button states
- **Service Integration**: Designed to run as a systemd service for persistent operation
- **Configuration Management**: Environment-based configuration system for easy customization

## Dependencies

### Base Library
Built on top of the original [python-elgato-streamdeck](https://github.com/abcminiuser/python-elgato-streamdeck) repository, extending its core functionality with:

- Custom UI rendering system
- Action framework for system integration
- Layout management for multiple button configurations
- Asset management for icons and visual elements

### Python Dependencies
- **streamdeck (0.9.8)**: Core StreamDeck hardware library (from forked repository - installed with `pip install -e .` in editable mode)
- **Pillow >= 9.0.0**: Image processing and manipulation for StreamDeck button rendering (`PIL.Image`, `PIL.ImageDraw`, `PIL.ImageFont`)
- **hidapi**: USB device communication library (required by StreamDeck library)
- **pathlib**: Modern path handling (part of Python standard library)

**Note**: Other packages like `pyautogui`, `pyperclip`, etc. may be installed in your environment but are not currently used by the jarvis codebase.

### System Dependencies
- **libhidapi-libusb0**: Low-level USB HID device access library (required for StreamDeck communication)
- **libhidapi-hidraw0**: Alternative HID raw device access library (required for StreamDeck communication)
- **ydotool**: Wayland/X11 compatible input simulation tool for hotkey execution
- **wmctrl**: X11 window management utility for application control
- **xdg-utils**: Desktop integration utilities for opening files and URLs
- **cmake**: Required for building ydotool from source
- **build-essential**: Compilation tools for building ydotool

### Hardware Requirements
- **Elgato StreamDeck XL**: 32-key version specifically (other variants not tested)
- **USB connection**: Direct USB connection to Linux system
- **Proper udev rules**: For device access permissions

## System Requirements

- Linux environment (developed and tested on Ubuntu/Debian)
- **X11 display server** (Wayland is not supported - had to switch to X11 due to compatibility issues)
- Python 3.11.4 (recommended, tested with conda environment)
- Elgato StreamDeck XL hardware
- ydotool (for hotkey simulation)
- wmctrl (for window management)
- Additional system tools as configured

## Project Status

⚠️ **This project is in active development and not considered finished.** The functionality will be extended and evolved as new requirements emerge. Current implementation provides core StreamDeck automation but additional features are planned for future releases.

## Usage

### Environment Setup

1. **Create conda environment with Python 3.11.4:**
   ```bash
   conda create -n jarvis python=3.11.4
   conda activate jarvis
   ```

2. **Install Python dependencies:**
   ```bash
   pip install Pillow>=9.0.0 hidapi

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

3. **Install system dependencies:**
   ```bash
   # For Ubuntu/Debian systems:
   sudo apt install libhidapi-libusb0 libhidapi-hidraw0 wmctrl xdg-utils

   # Build and install ydotool from source:
   git clone https://github.com/ReimuNotMoe/ydotool.git
   cd ydotool
   mkdir build && cd build
   cmake ..
   make
   # Note the path to the built ydotool binary for configuration
   ```

### StreamDeck Hardware Setup

1. **Set up udev rules for StreamDeck access:**
   ```bash
   # Create udev rule file (requires sudo):
   sudo nano /etc/udev/rules.d/99-streamdeck.rules

   # Add the following content:
   SUBSYSTEM=="usb", ATTRS{idVendor}=="0fd9", TAG+="uaccess"

   # Reload udev rules:
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   ```

2. **Ensure your user has access to the device** (unplug and replug StreamDeck if needed)

### Service Configuration

1. **Set up ydotool service** (required for hotkey functionality):
   ```bash
   # Create user systemd service directory:
   mkdir -p ~/.config/systemd/user

   # Create ydotool service file:
   nano ~/.config/systemd/user/ydotool.service
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
   EnvironmentFile=/path/to/jarvis-streamdeck/jarvis/config.env
   WorkingDirectory=/path/to/jarvis-streamdeck/jarvis
   ExecStartPre=/bin/sleep 10
   ExecStart=/path/to/jarvis-streamdeck/jarvis/run_jarvis.sh
   Restart=on-failure

   [Install]
   WantedBy=default.target
   ```

3. **Enable and start services:**
   ```bash
   # Enable and start ydotool service:
   systemctl --user enable ydotool.service
   systemctl --user start ydotool.service

   # Enable and start jarvis service:
   systemctl --user enable jarvis.service
   systemctl --user start jarvis.service
   ```

### Configuration

1. **Run the configuration setup:**
   ```bash
   cd jarvis/
   python setup_config.py
   ```

   This will create your `config.env` file with the necessary paths.

2. **Manual configuration** (edit `config.env`):
   - `YDOTOOL_PATH`: Path to your built ydotool binary
   - `PROJECTS_DIR`: Your main projects directory
   - `OBSIDIAN_VAULT`: Path to your Obsidian vault (if used)

See `config_example.env` for a complete configuration template and detailed systemd service setup instructions.

### Running Jarvis

```bash
# Direct execution (for testing):
cd jarvis/
python run_jarvis.py

# Or via shell script:
./run_jarvis.sh

# Check service status:
systemctl --user status jarvis.service
```

**Important:** Execute from a regular Linux terminal, not from VSCode terminal, as system calls to tools like ydotool and wmctrl may not work properly in VSCode's integrated terminal.

## Author

NhoaKing (2025)

This project extends the excellent work of the python-elgato-streamdeck community, providing a personalized automation layer for enhanced productivity workflows.
