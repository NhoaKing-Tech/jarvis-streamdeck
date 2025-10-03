#!/bin/bash
#
# Git Hooks Installation Script
# Installs pre-commit and post-commit hooks for the Jarvis documentation pipeline
#
# Usage: 
#   From repository root: ./jarvis/utils/install-hooks.sh
#   Or make executable and run: chmod +x jarvis/utils/install-hooks.sh && ./jarvis/utils/install-hooks.sh
#

set -e

# Change to repository root
cd "$(git rev-parse --show-toplevel)" 2>/dev/null || {
    echo "Error: Not in a git repository"
    exit 1
}

REPO_ROOT=$(pwd)
HOOKS_DIR="$REPO_ROOT/.git/hooks"
SOURCE_DIR="$REPO_ROOT/jarvis/utils"

# Check if both source hooks exist
if [ ! -f "$SOURCE_DIR/pre-commit-hook.sh" ]; then
    echo "Error: pre-commit-hook.sh not found in jarvis/utils/"
    exit 1
fi

if [ ! -f "$SOURCE_DIR/post-commit-hook.sh" ]; then
    echo "Error: post-commit-hook.sh not found in jarvis/utils/"
    exit 1
fi

# Backup existing hooks if they exist
for hook in pre-commit post-commit; do
    if [ -f "$HOOKS_DIR/$hook" ] && [ ! -L "$HOOKS_DIR/$hook" ]; then
        BACKUP_FILE="$HOOKS_DIR/${hook}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$HOOKS_DIR/$hook" "$BACKUP_FILE"
    fi
done

# Install pre-commit hook
cp "$SOURCE_DIR/pre-commit-hook.sh" "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/pre-commit"

# Install post-commit hook
cp "$SOURCE_DIR/post-commit-hook.sh" "$HOOKS_DIR/post-commit"
chmod +x "$HOOKS_DIR/post-commit"

echo "Installation of git hooks successful."
echo ""
echo "Hook behavior:"
echo "• DEV branch:"
echo "  - pre-commit: Generates documentation from tagged comments"
echo "  - post-commit: Updates Quartz preview"
echo "• MAIN branch:"
echo "  - pre-commit: Auto-strips EDU/REVIEW tags (preserves other tags)"
echo "  - post-commit: No action"
