#!/usr/bin/python3 
"""
-- GENERAL INFORMATION --
AUTHOR: NhoaKing
PROJECT: jarvis (personal assistant using ElGato StreamDeck XL)
NAME: setup_config.py
-- DESCRIPTION --
Setup script to create personalized configuration for Jarvis StreamDeck.

This script provides interactive configuration through prompts in terminal that helps users
set up their jarvis environment by creating a personalized config.env file. It handles path detection,
user inputs, and configuration file generation.

Purpose:
- Simplify initial jarvis setup for new users
- Generate properly formatted configuration files with sensible defaults according to user environment.
- Prevent common configuration errors

Usage:
Open a default terminal (CTRL+ALT+T) and run:
- python3 setup_config.py

Output:
- Creates config.env file in jarvis/config/ directory with user-specific configuration
- Configuration is automatically loaded by jarvis at startup (no manual sourcing needed)

This first line of the script (#!/usr/bin/python3) is the 'shebang' line.
It tells the system which interpreter to use to run the script.
In this case, it specifies to use the system default python 3 interpreter.
This is important for scripts that are intended to be run directly from the command line.

This ensures the script uses python 3 default installation.
New users probably do not have any virtual environment set up yet, so this way
we avoid using specific environment names. The purpose of this script is simply to create a config.env file.
"""

from pathlib import Path  # Modern path handling, more robust than os.path
from utils.terminal_prints import print_information_type, TerminalStyles

def create_config() -> None:
    """Create a personalized config.env file through interactive prompts.

    This function provides an interactive configuration menu that guides
    users through setting up their jarvis environment. It provides a simple way
    to collect user inputs for paths and generates a properly formatted configuration file
    that jarvis will load automatically at startup.

    Process:
    1. Checks for existing configuration and asks about overwriting
    2. Prompts user for values (ydotool path, projects directory, obsidian vaults, etc.)
    3. Generates properly formatted config.env file
    4. Informs user that config will be auto-loaded (no manual sourcing needed)
    5. Refers user to README.md for run instructions

    Output:
    Creates config.env in jarvis/config/ directory with all required configuration.
    The file is automatically loaded by jarvis at startup via core/application.py.
    """
    # Determine path for configuration file (in config subdirectory)
    config_path = Path(__file__).parent / "config" / "config.env"

    # Check if configuration already exists and asks user permission to overwrite
    if config_path.exists():
        print_information_type("warning", "File config.env already exists.")
        reply = input("Overwrite? (yes/no): ")
        if reply.lower() != 'yes': #lower() to accept also YES, Yes, yEs, ...
            print_information_type("info", "Earlier configuration not overwritten.")
            return  # Exit without making changes

    print_information_type("title", "Creating Jarvis StreamDeck configuration...")

    home = Path.home()  # More reliable than os.path.expanduser('~'). It provides a path object. In this case it will be /home/username

    # ydotool path configuration
    print_information_type("info", "YDOTOOL NOTE: If you want to execute hotkeys/shortcuts from your streamdeck:", color=TerminalStyles.YELLOW)
    print_information_type("detail", "Install ydotool from source and set up a service so it's always running")
    print_information_type("detail", "The ydotool system service is described in config_example.env")
    print_information_type("detail", "Path should look like: YDOTOOL_PATH=/home/yourusername/ydotool/build/ydotool")
    print_information_type("detail", "Detailed instructions are in config_example.env")
    print("")
    ydotool_input = input("Provide the executable to your ydotool path build from source: ")
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
    print("")
    print_information_type("error", "SECURITY RISK - PLAIN TEXT PASSWORD STORAGE")
    print("")
    print_information_type("warning", "It is STRONGLY RECOMMENDED to leave this field empty.")
    print("")
    print("Storing passwords in plain text files creates serious security risks:")
    print_information_type("detail", "File system access by other users or processes")
    print_information_type("detail", "Inclusion in system backups (local or cloud)")
    print_information_type("detail", "Accidental sharing or version control commits")
    print_information_type("detail", "Exposure if config.env is tracked by git or shared")
    print("")
    print_information_type("info", "RECOMMENDED: Leave empty and use SSH keys or password managers instead.")
    print_information_type("info", "Only set this if you absolutely understand the security implications.")
    print("")
    keyring_input = input("Optional keyring password (LEAVE EMPTY recommended): ")
    keyring_pw = keyring_input.strip() or ""

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
        print_information_type("error", f"Error writing configuration file: {e}")
        print_information_type("info", "Please check file permissions and try again.")
        return

    # Next steps and usage instructions
    print("")
    print_information_type("success", f"Configuration saved to {config_path}")
    print("")
    print_information_type("info", "Configuration complete!")
    print("")
    print_information_type("detail", "The config.env file will be loaded automatically by jarvis.")
    print_information_type("detail", "No need to source it manually!")
    print("")
    print_information_type("detail", "For instructions on running jarvis (direct execution or systemd service),")
    print_information_type("detail", "please refer to the README.md file in the project root.")

    # NEXT STEPS GUIDANCE:
    print("")
    print_information_type("title", "Next steps:", border_char="-", width=50)
    print_information_type("step", "Test the configuration: python3 -m jarvis", step_number=1)
    print_information_type("step", "Customize layouts in ui/render.py, actions in actions/actions.py", step_number=2)
    print_information_type("step", "Add custom icons to assets/jarvisicons/", step_number=3)
    print_information_type("step", "Create code snippets in assets/snippets/", step_number=4)
    print_information_type("detail", "Note: Jarvis already grants execution permissions for your user only")
    print("")

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
    - config.env is automatically loaded by jarvis at startup (no manual sourcing needed)
    - User can run jarvis with: python -m jarvis (from project root with jarvis-env) or set up system service
    - System service can be configured using the generated .env file
    
    """
    create_config()
    # no return value as this is a script meant to be run directly and creates a file as output