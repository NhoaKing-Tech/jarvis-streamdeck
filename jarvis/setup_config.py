#!/usr/bin/python3 
# This above is the 'shebang' line. It is a label that tells the system which interpreter to use to run the script.
# In this case, it specifies to use the system default python 3 interpreter. This is important for scripts that are intended 
# to be run directly from the command line.
#
# In this way, it ensures that the script will use python 3 default installation.
# New users probably do not have any virtual environment set up yet, so in this way we avoid using specific environment names.
# The purpose of this script is simply to create a config.env file, so no dependencies are needed as only standard modules are used.

"""
Setup script to create personalized configuration for Jarvis StreamDeck.

This script provides interactive configuration through prompts in terminal that helps users
set up their jarvis environment by creating a personalized config.env file. It handles path detection,
user inputs, and configuration file generation.

Purpose:
- Simplify initial jarvis setup for new users
- Generate properly formatted configuration files with sensible defaults according to user environment.
- Detect system-specific paths and tools
- Prevent common configuration errors

Usage:
Open a default terminal (CTRL+ALT+T) and run:
- python3 setup_config.py

Output:
- Creates config.env file in the jarvis directory with user-specific configuration
"""

from pathlib import Path  # Modern path handling, more robust than os.path

def create_config() -> None:
    """Create a personalized config.env file through interactive prompts.

    This function provides an interactive configuration menu that guides
    users through setting up their jarvis environment. It provides a simple way
    to collect user inputs for paths and generates a properly formatted configuration file
    as the jarvis modules expect.

    Process:
    1. Checks for existing configuration and asks about overwriting
    2. Prompts user for values
    4. Generates properly formatted config.env file
    5. Provides simple usage instructions and some warnings about security

    Output:
    Creates config.env with paths for ydotool, projects directory,
    and obsidian vaults.
    """
    # Determine path for configuration file (same directory as this script)
    config_path = Path(__file__).parent / "config.env"

    # Check if configuration already exists and asks user permission to overwrite
    if config_path.exists():
        response = input("File config.env already exists. Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("Earlier configuration not overwritten.")
            return  # Exit without making changes
        
    print("Creating Jarvis StreamDeck configuration...")
    print("")

    home = Path.home()  # More reliable than os.path.expanduser('~'). It provides a path object. In this case it will be /home/username

    # ydotool path configuration
    print("\033[93mYODOTOOL NOTE: If you want to be able to execute hotkeys/shortcuts\n"
        "from your streamdeck, you need to install ydotool from source and set up a service so that it\n"
        "is always running. The ydotool system service is described in config_example.env\n"
        "inside the jarvis directory. When building from source, the path\n"
        "should like something like 'YDOTOOL_PATH=/home/yourusername/ydotool/build/ydotool'\n"
        "Detail instructions are given in config_example.env\033[0m")

    ydotool_input = input(f"Provide the executable to your ydotool path build from source: ")
    ydotool_path = ydotool_input.strip()

    # Projects directory configuration. The default is /home/username/projects
    default_projects = home / 'projects'
    projects_input = input(f"Path to projects directory [{default_projects}]: ")
    projects_dir = projects_input.strip() or str(default_projects)

    # Obsidian vault configurations - multiple vaults with codenames
    # In my case I use two vaults, one for journaling and one for projects documentation and task management, 
    # as I am using quartz to create my static website from my notes and host that through github pages later on.
    # You can customize these vaults for your use case. Use only one vault if you want, or more than two. 
    # However, if you use more than two, please introduce the paths to the vaults directly manually inside 
    # the config.env, and then refer to them with the codename after "OBISIDIAN_VAULT_" in the config.env file.
    # In the actions module you can then refer to them with the same codename to access the vault you want.
    # You can also customize the codenames to your liking, just make sure to use only letters, numbers and underscores.
    
    # Journal vault configuration
    default_journal_vault_path = f"{projects_dir}/journal_vault"
    journal_vault_path = input(f"Obsidian vault journal path [{default_journal_vault_path}]: ")
    obsidian_journal_vault_path = journal_vault_path.strip() or default_journal_vault_path

    # Quartz vault configuration
    default_quartz_vault_path = f"{projects_dir}/quartz_vault"
    quartz_input = input(f"Obsidian vault quartz path [{default_quartz_vault_path}]: ")
    obsidian_quartz_vault_path = quartz_input.strip() or default_quartz_vault_path

    # Keyring password configuration
    print("\033[93mSECURITY NOTE: This note is about storing passwords in plain text file storage.\n"
          "Jarvis handles passwords securely in memory and will not log or expose them unless you share them.\n"
          "Storing passwords in plain text files creates security risks:\n"
          "- File system access by other users or processes\n"
          "- Inclusion in system backups (local or cloud)\n"
          "- Accidental sharing or version control commits\n"
          "Treat this file with the same care as any sensitive credential.\n"
          "Consider using password managers or SSH keys for better security.\033[0m")
    keyring_input = input("Optional keyring password): ")
    keyring_pw = keyring_input.strip() or "your_password_here"

    # Create properly formatted config.env file with collected paths and values
    config_content = f"""# Jarvis System Configuration
    # Output environment configuration file created by executing 
    # setup_config.py in the jarvis directory with `python3 setup_config.py`

    YDOTOOL_PATH={ydotool_path}
    PROJECTS_DIR={projects_dir}
    OBSIDIAN_VAULT_journal={obsidian_journal_vault_path}
    OBSIDIAN_VAULT_quartz={obsidian_quartz_vault_path}
    KEYRING_PW={keyring_pw}
"""

    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
    except IOError as e:
        print(f"Error writing configuration file: {e}")
        print("Please check file permissions and try again.")
        return

    # Next steps and usage instructions
    print(f"\nConfiguration saved to {config_path}")
    print("\nTo use this configuration you have two options. I recommend option 2.")
    print("\n1. Direct execution:")
    print("   source config.env && python run_jarvis.py")
    print("\n   or")
    print("\n2. System service setup:")
    print("   See config_example.env for systemd service configuration, udev rules, ydotool configuration, and usage instructions.")

    # NEXT STEPS GUIDANCE:
    print("\nNext steps:")
    print("1. Test the configuration: python3 run_jarvis.py")
    print("2. Customize layouts in ui/render.py, actions in actions/actions.py")
    print("3. Add custom icons to assets/jarvisicons/")
    print("4. Create code snippets in assets/snippets/. Jarvis layer already grants execution permissions for only your user so you do not need to worry about doing that manually.")

if __name__ == "__main__":
    """Script entry point for interactive configuration setup.

    This ensures the configuration wizard only runs when script is executed
    directly, not when imported as a module by other Python scripts.

    Execution:
    1. Script is run from command line: python3 setup_config.py
    2. Interactive configuration through terminal prompts starts
    3. User provides configuration values
    4. config.env file is generated
    5. Usage instructions are displayed

    Output:
    After this script completes:
    - config.env file exists with user configuration
    - User can run jarvis with: source config.env && python run_jarvis.py (from jarvis-env) or set up system service
    - System service can be configured using the generated .env file
    
    """
    create_config()
    # no return value as this is a script meant to be run directly and creates a file as output