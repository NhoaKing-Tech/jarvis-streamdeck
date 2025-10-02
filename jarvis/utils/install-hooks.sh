#!/bin/bash
#
# Git Hooks Installation Script
# ==============================
#
# Installs pre-commit and post-commit hooks for the Jarvis documentation pipeline
#
# Usage:
#   ./jarvis/utils/install-hooks.sh
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   Jarvis Git Hooks Installation${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# Change to repository root
cd "$(git rev-parse --show-toplevel)" 2>/dev/null || {
    echo -e "${RED}❌ Error: Not in a git repository${NC}"
    exit 1
}

REPO_ROOT=$(pwd)
HOOKS_DIR="$REPO_ROOT/.git/hooks"
SOURCE_DIR="$REPO_ROOT/jarvis/utils"

# Check if source hooks exist
if [ ! -f "$SOURCE_DIR/pre-commit-hook.sh" ]; then
    echo -e "${RED}❌ Error: Source hooks not found in jarvis/utils/${NC}"
    exit 1
fi

echo -e "${BLUE}📍 Repository: $REPO_ROOT${NC}"
echo -e "${BLUE}📂 Installing hooks to: $HOOKS_DIR${NC}"
echo ""

# Backup existing hooks if they exist
for hook in pre-commit post-commit; do
    if [ -f "$HOOKS_DIR/$hook" ] && [ ! -L "$HOOKS_DIR/$hook" ]; then
        BACKUP_FILE="$HOOKS_DIR/${hook}.backup.$(date +%Y%m%d_%H%M%S)"
        echo -e "${YELLOW}📦 Backing up existing $hook to: $(basename $BACKUP_FILE)${NC}"
        cp "$HOOKS_DIR/$hook" "$BACKUP_FILE"
    fi
done

# Install pre-commit hook
echo -e "${BLUE}🔧 Installing pre-commit hook...${NC}"
cp "$SOURCE_DIR/pre-commit-hook.sh" "$HOOKS_DIR/pre-commit"
chmod +x "$HOOKS_DIR/pre-commit"
echo -e "${GREEN}   ✓ pre-commit hook installed${NC}"

# Install post-commit hook
if [ -f "$SOURCE_DIR/post-commit-hook.sh" ]; then
    echo -e "${BLUE}🔧 Installing post-commit hook...${NC}"
    cp "$SOURCE_DIR/post-commit-hook.sh" "$HOOKS_DIR/post-commit"
    chmod +x "$HOOKS_DIR/post-commit"
    echo -e "${GREEN}   ✓ post-commit hook installed${NC}"
fi

echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Git hooks installed successfully!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📋 Installed hooks:${NC}"
echo -e "${BLUE}   • pre-commit  - Documentation generation (dev) & auto-stripping (main)${NC}"
echo -e "${BLUE}   • post-commit - Quartz preview updates (dev)${NC}"
echo ""
echo -e "${BLUE}🎯 Workflow:${NC}"
echo -e "${BLUE}   DEV branch:  Commits generate docs from tagged comments${NC}"
echo -e "${BLUE}   MAIN branch: Commits auto-strip EDU/REVIEW tags (keeps other tags)${NC}"
echo ""
echo -e "${YELLOW}💡 To bypass hooks on a specific commit:${NC}"
echo -e "${YELLOW}   git commit --no-verify${NC}"
echo ""
