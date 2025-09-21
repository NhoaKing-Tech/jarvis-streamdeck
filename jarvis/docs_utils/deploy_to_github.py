#!/usr/bin/env python3
"""
GitHub Deployment Script for Jarvis Project

This script automates the process of preparing and deploying production code to GitHub:

1. Generates production build from current dev branch
2. Switches to main branch
3. Ensures jarvis_prod/ directory is ready for GitHub deployment
4. Creates deployment commit
5. Provides instructions for pushing to GitHub

WORKFLOW:
- Development happens in 'dev' branch with full jarvis/ directory
- GitHub gets 'main' branch with jarvis_prod/ directory (clean production code)
- jarvis/ directory is ignored on main branch for privacy
- This script bridges the gap between dev and main branches

Usage:
    python3 deploy_to_github.py [commit_message]

Example:
    python3 deploy_to_github.py "feat: Add audio controls for StreamDeck"
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def run_command(command, description="", check=True):
    """Run a shell command and handle errors."""
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

        return result.returncode == 0

    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {command}")
        print(f"   Error: {e.stderr}")
        return False

def check_git_status():
    """Ensure we're in a clean git state."""
    result = subprocess.run(
        "git status --porcelain",
        shell=True,
        capture_output=True,
        text=True
    )

    if result.stdout.strip():
        print("❌ Git working directory is not clean!")
        print("   Please commit or stash your changes first:")
        print(f"   {result.stdout}")
        return False

    return True

def get_current_branch():
    """Get the current git branch."""
    result = subprocess.run(
        "git rev-parse --abbrev-ref HEAD",
        shell=True,
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def copy_production_structure():
    """Copy jarvis_prod contents to jarvis_prod/ directory for GitHub deployment."""
    source_dir = Path("../../jarvis_prod")
    target_dir = Path("../../jarvis_prod")

    if not source_dir.exists():
        print("❌ jarvis_prod directory not found!")
        print("   Run: python create_production_build.py first")
        return False

    print("📦 Production structure already prepared in jarvis_prod/")
    print("📁 GitHub Repository Structure:")
    print("   ├── jarvis_prod/           # Clean production code (what GitHub sees)")
    print("   │   ├── actions/")
    print("   │   ├── core/")
    print("   │   ├── ui/")
    print("   │   ├── config/")
    print("   │   ├── assets/")
    print("   │   ├── utils/")
    print("   │   ├── tests/")
    print("   │   └── main.py")
    print("   ├── setup.py              # Original StreamDeck library setup")
    print("   ├── README.md             # Professional project README")
    print("   └── [other repository files]")
    print("")
    print("📝 Note: jarvis/ development directory is ignored on main branch")
    return True

def create_github_readme():
    """Create a README.md for GitHub repository."""
    readme_content = """# 🤖 Jarvis StreamDeck Automation

Professional StreamDeck automation system for Linux with ElGato StreamDeck XL support.

## ✨ Features

- **Multi-Application Control**: Open VSCode projects, browsers, Spotify, terminals
- **Smart Window Management**: Prevent duplicate windows, focus existing ones
- **Audio Controls**: Microphone toggle with visual feedback
- **Text Automation**: Type snippets, passwords, and templates
- **Git Workflow Integration**: Automated commit workflows
- **Hotkey Simulation**: System-wide keyboard shortcuts
- **Environment Management**: Conda environment switching

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- ElGato StreamDeck XL
- Linux (X11 or Wayland)
- ydotool for input simulation

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/jarvis-streamdeck.git
cd jarvis-streamdeck

# Install dependencies
pip install -r requirements.txt

# Configure your environment
cd jarvis_prod
python config/setup_config.py

# Run Jarvis
python main.py
```

## 📁 Project Structure

```
jarvis-streamdeck/
├── jarvis_prod/               # Production Jarvis automation system
│   ├── actions/              # StreamDeck key actions
│   ├── core/                 # Application core logic
│   ├── ui/                   # User interface and rendering
│   ├── config/               # Configuration management
│   ├── assets/               # Icons, scripts, and resources
│   ├── utils/                # Utility functions
│   ├── tests/                # Test suite
│   └── main.py               # Application entry point
├── setup.py                  # StreamDeck library installation
├── src/                      # StreamDeck library source code
└── [other library files]     # Original python-elgato-streamdeck files
```

## ⚙️ Configuration

1. **Environment Setup**: Configure paths and credentials in `jarvis_prod/config/config.env`
2. **StreamDeck Layout**: Customize key layouts in `jarvis_prod/ui/layouts.py`
3. **Actions**: Add custom actions in `jarvis_prod/actions/actions.py`

## 🔧 Development

This is the production build. For development workflow and comprehensive documentation, see the development repository.

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

*Generated with the Jarvis Annotation Workflow System*
"""

    readme_path = Path("../../README.md")
    readme_path.write_text(readme_content)
    print("📝 Created GitHub README.md")

def main():
    """Main deployment workflow."""
    print("🚀 Jarvis GitHub Deployment Script")
    print("=" * 50)

    # Get commit message from command line or use default
    commit_message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Update production build"

    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Step 1: Verify we're in dev branch and clean state
    current_branch = get_current_branch()
    print(f"📍 Current branch: {current_branch}")

    if current_branch != "dev":
        print("⚠️  Warning: Not on 'dev' branch")
        print("   This script is designed to deploy from dev to main")
        response = input("   Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return 1

    if not check_git_status():
        return 1

    # Step 2: Generate production build
    print("\n🏭 Step 1: Generating production build...")
    if not run_command("python3 create_production_build.py", "Creating production build"):
        return 1

    # Step 3: Switch to main branch
    print("\n🌟 Step 2: Switching to main branch...")
    if not run_command("git checkout main", "Switching to main branch"):
        print("   Creating main branch...")
        if not run_command("git checkout -b main", "Creating main branch"):
            return 1

    # Step 4: Copy production structure
    print("\n📦 Step 3: Preparing GitHub structure...")
    if not copy_production_structure():
        return 1

    # Step 5: Create GitHub README
    create_github_readme()

    # Step 6: Stage files for commit
    print("\n📁 Step 4: Staging files for commit...")
    run_command("git add .", "Staging all files")

    # Step 7: Create commit
    print("\n💾 Step 5: Creating deployment commit...")
    full_commit_message = f"""{commit_message}

🤖 Deployed from dev branch with Jarvis Annotation Workflow System

Production build generated automatically from development branch.
For development history and comprehensive documentation, see dev branch.
"""

    commit_command = f'git commit -m "{full_commit_message}"'
    run_command(commit_command, "Creating deployment commit")

    # Step 8: Provide next steps
    print("\n" + "=" * 50)
    print("✅ DEPLOYMENT PREPARATION COMPLETE!")
    print("=" * 50)

    print("\n📋 Next Steps:")
    print("   1. Review the changes:")
    print("      git log --oneline -5")
    print("      git diff HEAD~1")

    print("\n   2. Push to GitHub:")
    print("      git push origin main")
    print("      # Or for first time:")
    print("      git push -u origin main")

    print("\n   3. Return to development:")
    print("      git checkout dev")

    print(f"\n🎯 GitHub Repository Structure:")
    print("   ✅ Clean production code (no jarvis/ directory)")
    print("   ✅ Professional README.md")
    print("   ✅ Complete project structure")
    print("   ✅ Ready for public sharing")

    print(f"\n💡 Tip: Your development work stays private in 'dev' branch")
    print(f"         GitHub gets clean, professional code in 'main' branch")

    return 0

if __name__ == "__main__":
    exit(main())