#!/usr/bin/env python3
"""
Branch Manager for Dev/Main Workflow

This script helps manage the different .gitignore files and workflows
for the dev (private development) and main (public GitHub) branches.

Commands:
    setup-dev     - Only configures the current branch for development (copies .gitignore-dev to .gitignore) without switching branches
    setup-main    - Only configures the current branch for GitHub deployment (copies .gitignore-main to .gitignore) without switching branches
    status        - Show current branch configuration
    switch-to-dev - First switches to the dev branch (git checkout dev), then calls setup_dev_branch() to apply the development configuration
    switch-to-main- First switches to the main branch (git checkout main) after checking for uncommitted changes, then calls setup_main_branch() to apply the production configuration

The setup-* commands are for configuring your current branch, while switch-to-* commands both change branches AND apply the appropriate configuration. The switch commands are more comprehensive - they handle branch switching plus the configuration that the setup commands provide.

This means that when we want to switch branches, we should use the switch-to-* commands to ensure both the branch and its configuration are correctly set. However, this might fail if there are uncommitted changes, so we should commit or stash changes before switching, to save the progress of the current branch. After that, we can change branches with the switch-to-* commands. When switching branches, any uncommitted changes will be lost if they conflict with the target branch. Therefore, it's crucial to ensure that all changes are committed or stashed before executing the switch-to-* commands.

We must consider that when switching branches, the files in the working directory will change to match the target branch. When you switch branches with git checkout main, your working directory files will change to match the last commit on the main branch. The same applies when switching to the dev branch.

In VS Code, you'll see:
- Files that exist in main but not dev will appear
- Files that exist in dev but not main will disappear from the file explorer
- Files that exist in both branches but with different content will show the main branch version
- Any open editor tabs for files that don't exist in main will show as "deleted" or close

This is standard git behavior - your working directory reflects whatever branch you're currently on. The branch_manager.py script adds the .gitignore switching on top of this, so you'll also get different ignore rules. 

That's why the script checks for uncommitted changes before switching to main - if you had unsaved work, it could be lost when the files revert to the main branch state.

If you want to see what differences exist between branches before switching, you can run:

`git diff dev..main`

---
What is 'stash changes'?

Stashing changes in Git allows you to save your uncommitted changes temporarily without committing them. This is useful when you need to switch branches but aren't ready to commit your current work. You can stash your changes, switch branches, and then apply the stashed changes later.

What git stash does:
- Saves your modified files and staged changes
- Reverts your working directory to the last commit (clean state)
- Stores the changes in a "stash" that you can retrieve later

Common stash commands:
`git stash`              # Save current changes to stash
`git stash pop`          # Restore the most recent stash and remove it from stash list
`git stash apply`        # Restore stash but keep it in the stash list
`git stash list`         # See all your stashes
`git stash drop`         # Delete a stash without applying it

Typical workflow:
1. You're working on dev branch with uncommitted changes
2. You need to quickly switch to main
3. Run git stash - saves your work, cleans working directory
4. Switch to main branch (now allowed since directory is clean)
5. Do your work on main
6. Switch back to dev
7. Run git stash pop - your uncommitted changes are restored

It's basically a temporary save feature that lets you switch contexts without losing work or making premature commits.

---
print() prints a new line after the mesage by default as always. If we want to avoid that, we can use end="" in the print function. We can specify the separator between multiple items with sep="" in the print function (default is space).

    To avoid newline:
    print(f"🔧 {description or command}", end="")  # No newline
    print("Hello", end=" ")  # Ends with space instead

    To print multiple items with custom separator:
    print("apple", "banana", "cherry", sep=", ")  # Output: apple, banana, cherry
    print("2025", "01", "15", sep="-")           # Output: 2025-01-15
    print("Loading", ".", ".", ".", sep="")      # Output: Loading...

    Common parameters:
    - sep="" - What to put between multiple arguments (default is space)
    - end="" - What to put at the end (default is newline)
    - file=sys.stderr - Where to print (default is stdout)

    Examples:
    print("Status:", "Running", sep=" -> ")     # Status -> Running
    print("Progress: ", end="")                 # No newline, next print continues same line
    print("[", "■" * 5, "]", sep="")           # [■■■■■]
    print("Error", "Warning", sep=" | ", end="!\n")  # Error | Warning!

    So if you wanted the original line to not add a newline:
    print(f"{description or command}", end="")  # Print without newline

---
f-strings (formatted string literals) are a way to embed expressions inside string literals, using curly braces {}. They were introduced in Python 3.6 and provide a concise and readable way to format strings. There are so many cool things we can do with f-strings:

Basic syntax:
name = "Alice"
age = 30
print(f"Hello, {name}! You are {age} years old.")
# Output: Hello, Alice! You are 30 years old.

What it does:
- f prefix tells Python this is a formatted string
- {} inside the string are placeholders for expressions
- Python evaluates the expressions and inserts the results

Examples:
x = 10
y = 20
print(f"The sum of {x} and {y} is {x + y}")  # The sum of 10 and 20 is 30

# Can call functions inside
name = "john"
print(f"Hello, {name.title()}!")  # Hello, John!

# Can format numbers. How many decimal places.
price = 19.99
print(f"Price: ${price:.2f}")  # Price: $19.99

In your code:
print(f"🔧 {description or command}")
This means: "Print 🔧 followed by either description (if it exists) or command (if description is empty/None)"

---
Usage:
    python3 branch_manager.py <command>
"""

import os # module for interacting with the operating system
import sys # module for accessing system-specific parameters and functions
import shutil # module for high-level file operations
import subprocess # module for running shell commands
from pathlib import Path # module for object-oriented filesystem paths. Better than using os.path

def run_command(command, description="", check=True, return_output=False):
    """Run a shell command and return success status. I can use this to run git commands automatically and handle errors gracefully.

    Parameters:
        command (str): The shell command to run.
        description (str): Optional human-readable description to print before running the command. Defaults to empty string.
        check (bool): If True, raise an error on command failure. Defaults to True.
    """
    print(f"Running: {description or command}") #print the description OR command being that will run next. Using an f-string followed by, either description (if it exists), or command (if description is empty/None), as it uses the "or" operator for fallback logic.
    # If description is provided (not empty), it will print that. Otherwise, it will print the command itself.
    
    # error handling block with try-except
    try:
        result = subprocess.run( # to run shell commands from Python
            command, # the shell command to execute
            shell=True, # run the command through the shell, allows using shell features like pipes, redirection, etc.
            check=check, # if true, raise CalledProcessError on non-zero exit codes
            capture_output=True, # capture stdout and stderr
            text=True # treat output as text (string) instead of bytes
        )

        if result.stdout.strip(): #result.stdout contains the standard output of the command. strip() removes leading/trailing whitespace
            # only prints if there is actual output, not just whitespace
            print(f"   {result.stdout.strip()}") # indents output for readability and visual hierarchy

        if return_output: # if we want to return the command output
            return result.stdout.strip() # return the stripped output

        return True # returns True if command succeeded

    except subprocess.CalledProcessError as e: # catches the specific exception raised when check=True and the command fails. "as e" assigns the exception to variable e for access
        print(f"❌ Command failed: {command}") # prints error message with the failed command
        if e.stderr: # if there is any error output captured
            print(f"   Error: {e.stderr}") # prints the error output, indented for readability and visual hierarchy
        return False # returns False if command failed

        # Key Concepts Used:
        # 1. Error handling: try/except for graceful failure management
        # 2. Subprocess: secure way to run shell commands from Python
        # 3. String methods: .strip() removes whitespace
        # 4. Boolean logic: description or command for fallback values
        # 5. F-strings: f"text {variable}" for string formatting with an or operator
        # 6. Conditional execution: if condition: blocks

def get_current_branch(): # function with no parameters
    """Get the currently active git branch."""
    # Uses run_command with return_output=True to get the actual branch name instead of just success/failure
    # git rev-parse: Git command that parses git objects and references
    # --abbrev-ref: Returns abbreviated reference name (branch name instead of full commit hash)
    # HEAD: Points to the current branch/commit you are on
    return run_command("git rev-parse --abbrev-ref HEAD", "Getting current git branch", return_output=True)

'''
Parameters vs Arguments of a function
Parameters: The variables defined in the function signature or definition. They are placeholders for the values that will be passed to the function when it is called.
Arguments: The actual values or data that are passed to the function when it is called or invoked. These values correspond to the parameters defined in the function signature.
So argument is the name for the actual value we pass to a function, while parameter is the name for the variable in the function definition that receives that value.
We use parameters to refer to the definition of the function, and arguments to refer to the actual values we provide when calling the function.
However, many people use them interchangeably in casual conversation, so the distinction is not always strictly observed.
There are three types of parameters:
1. Positional Parameters: These are the most common type of parameters. When you define a function, you can specify parameters in the function signature. When you call the function, you provide arguments in the same order as the parameters are defined. For example in run_command(command, description="", check=True), command is a positional parameter, because it has no default value and must be provided in the correct order when calling the function.
2. Keyword Parameters (optional when calling the function): These parameters are defined with default values in the function signature. When calling the function, you can specify arguments by naming the parameters explicitly, regardless of their order. For example, in run_command(command, description="", check=True), description and check are keyword parameters with default values.
3. *args and **kwargs: These are special types of parameters that allow you to pass a variable number of arguments to a function. *args collects extra positional arguments as a tuple, while **kwargs collects extra keyword arguments as a dictionary. We do not need to provide default values for these parameters. These are called variable-length argument collectors. *args is variable positional parameters, while **kwargs is variable keyword parameters.
'''

def setup_dev_branch():
    """Configure branch for development work."""
    print("🚀 Setting up DEV branch configuration...")

    # Copy dev gitignore
    dev_gitignore = Path("../../.gitignore-dev")
    main_gitignore = Path("../../.gitignore")

    if dev_gitignore.exists():
        shutil.copy2(dev_gitignore, main_gitignore)
        print("✅ Applied dev .gitignore")
    else:
        print("⚠️  .gitignore-dev not found")

    print("\n📋 DEV BRANCH CONFIGURATION:")
    print("   ✅ Full jarvis/ directory available")
    print("   ✅ Documentation generation enabled")
    print("   ✅ Educational and architectural comments preserved")
    print("   ✅ jarvis_prod/ ignored (generated)")
    print("   ✅ jarvis/docs_utils/ scripts and guides tracked")
    print("   ✅ jarvis/docs/content/ ignored (generated)")
    print("   ✅ Personal configuration files ignored")

    return True

def setup_main_branch():
    """Configure branch for GitHub deployment."""
    print("🏭 Setting up MAIN branch configuration...")

    # Copy main gitignore
    main_gitignore_source = Path("../../.gitignore-main")
    main_gitignore = Path("../../.gitignore")

    if main_gitignore_source.exists():
        shutil.copy2(main_gitignore_source, main_gitignore)
        print("✅ Applied main .gitignore")
    else:
        print("⚠️  .gitignore-main not found")

    print("\n📋 MAIN BRANCH CONFIGURATION:")
    print("   ✅ jarvis_prod/ directory contains clean production code")
    print("   ✅ Clean, professional structure for GitHub")
    print("   ✅ jarvis/ directory ignored (private development)")
    print("   ✅ Ready for public GitHub repository")
    print("   ✅ Documentation focused on end users")

    return True

def show_status():
    """Show current branch and configuration status."""
    current_branch = get_current_branch()
    print(f"📍 Current Branch: {current_branch}")

    # Check which .gitignore is active
    gitignore = Path("../../.gitignore")
    if gitignore.exists():
        content = gitignore.read_text()
        if "DEV BRANCH" in content:
            config_type = "DEV (Development)"
        elif "MAIN BRANCH" in content:
            config_type = "MAIN (Production/GitHub)"
        else:
            config_type = "UNKNOWN (Manual configuration)"
    else:
        config_type = "NO .gitignore found"

    print(f"⚙️  Configuration: {config_type}")

    # Show relevant directories
    jarvis_dir = Path("../../jarvis")
    production_dir = Path("../../jarvis_prod")

    print(f"\n📁 Directory Status:")
    print(f"   jarvis/       {'✅ EXISTS' if jarvis_dir.exists() else '❌ Missing'}")
    print(f"   jarvis_prod/  {'✅ EXISTS' if production_dir.exists() else '❌ Missing'}")

    # Check git status
    result = subprocess.run(
        "git status --porcelain",
        shell=True,
        capture_output=True,
        text=True,
        cwd="../../"
    )

    if result.stdout.strip():
        print(f"\n⚠️  Uncommitted changes:")
        print(f"   {result.stdout.strip()}")
    else:
        print(f"\n✅ Working directory clean")

def switch_to_dev():
    """Switch to dev branch and apply dev configuration."""
    print("🔄 Switching to dev branch...")

    if not run_command("git checkout dev", "Switching to dev branch"):
        print("   Creating dev branch...")
        if not run_command("git checkout -b dev", "Creating dev branch"):
            return False

    return setup_dev_branch()

def switch_to_main():
    """Switch to main branch and apply main configuration."""
    print("🔄 Switching to main branch...")

    # Check if we have uncommitted changes
    result = subprocess.run(
        "git status --porcelain",
        shell=True,
        capture_output=True,
        text=True
    )

    if result.stdout.strip():
        print("⚠️  You have uncommitted changes!")
        print("   Please commit or stash them before switching branches")
        return False

    if not run_command("git checkout main", "Switching to main branch"):
        print("   Main branch doesn't exist yet")
        print("   Use: python3 deploy_to_github.py to create it")
        return False

    return setup_main_branch()

def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python3 branch_manager.py <command>")
        print("\nCommands:")
        print("  setup-dev      - Configure current branch for development")
        print("  setup-main     - Configure current branch for GitHub deployment")
        print("  status         - Show current branch and configuration")
        print("  switch-to-dev  - Switch to dev branch with dev configuration")
        print("  switch-to-main - Switch to main branch with main configuration")
        return 1

    command = sys.argv[1]

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    print("🎯 Jarvis Branch Manager")
    print("=" * 40)

    if command == "setup-dev":
        return 0 if setup_dev_branch() else 1

    elif command == "setup-main":
        return 0 if setup_main_branch() else 1

    elif command == "status":
        show_status()
        return 0

    elif command == "switch-to-dev":
        return 0 if switch_to_dev() else 1

    elif command == "switch-to-main":
        return 0 if switch_to_main() else 1

    else:
        print(f"❌ Unknown command: {command}")
        return 1

if __name__ == "__main__":
    exit(main())