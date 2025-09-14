#!/usr/bin/env python3
"""
Setup script to create personalized configuration for Jarvis StreamDeck
"""
from pathlib import Path

def create_config():
    """Create a personalized config.env file"""
    config_path = Path(__file__).parent / "config.env"

    if config_path.exists():
        response = input("File config.env already exists. Overwrite? (y/N): ")
        if response.lower() != 'y':
            print("Past configuration not overwritten.")
            return

    print("Creating Jarvis StreamDeck configuration...")
    print("Press Enter to use default path values")

    # Get user home directory
    home = Path.home()

    # Get configuration values
    ydotool_path = input(f"ydotool path [{which_ydotool()}]: ")
    projects_dir = input(f"projects directory [{home / 'projects'}]: ")
    obsidian_vault = input(f"Obsidian vault [{projects_dir}/my_vault]: ")

    # Write configuration
    config_content = f"""# Jarvis StreamDeck System Configuration
    # Output environment configuration file created by executing setup_config.py
    # in the jarvis directory.

    YDOTOOL_PATH={ydotool_path}
    PROJECTS_DIR={projects_dir}
    OBSIDIAN_VAULT={obsidian_vault}
    """

    with open(config_path, 'w') as f:
        f.write(config_content)

    print(f"Configuration saved to {config_path}")
    print("To use this configuration, run:")
    print("`source config.env && python run_jarvis.py`")
    print(" or update your system service as described in config_example.env")

def which_ydotool():
    """Find ydotool in system PATH"""
    import shutil
    path = shutil.which('ydotool')
    return path if path else '/usr/local/bin/ydotool'

if __name__ == "__main__":
    create_config()