#!/usr/bin/env python3
"""
Branch Manager for Jarvis Dev/Main Workflow

This script helps manage the different .gitignore files and workflows
for the dev (private development) and main (public GitHub) branches.

Commands:
    setup-dev     - Configure branch for development work
    setup-main    - Configure branch for GitHub deployment
    status        - Show current branch configuration
    switch-to-dev - Switch to dev branch and apply dev configuration
    switch-to-main- Switch to main branch and apply main configuration

Usage:
    python3 branch_manager.py <command>
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(command, description="", check=True):
    """Run a shell command and return success status."""
    print(f"🔧 {description or command}")

    try:
        result = subprocess.run(
            command,
            shell=True,
            check=check,
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            print(f"   {result.stdout.strip()}")

        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False

def get_current_branch():
    """Get the current git branch."""
    result = subprocess.run(
        "git rev-parse --abbrev-ref HEAD",
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

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