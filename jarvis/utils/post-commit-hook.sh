#!/bin/bash
#
# Post-commit Hook for Jarvis Documentation Pipeline
# ===================================================
#
# This hook runs AFTER a commit completes and updates the local
# Quartz preview with the latest generated documentation.
#
# Installation:
#   cp jarvis/utils/post-commit-hook.sh .git/hooks/post-commit
#   chmod +x .git/hooks/post-commit
#

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Only run on dev branch (where docs are generated)
if [[ "$CURRENT_BRANCH" != "dev" ]]; then
    exit 0
fi

# Change to project root
cd "$(git rev-parse --show-toplevel)"

# Check if quartz-preview exists
if [ ! -d "quartz-preview" ]; then
    echo -e "${YELLOW}ℹ️  No quartz-preview/ directory found. Skipping Quartz update.${NC}"
    echo -e "${YELLOW}💡 To enable local preview, set up Quartz following: jarvis/git_docs/09_QUARTZ_PREVIEW.md${NC}"
    exit 0
fi

# Check if docs were generated in this commit
if [ ! -d "jarvis/docs/content" ]; then
    # No docs directory, nothing to copy
    exit 0
fi

# Check if any markdown files exist
if ! ls jarvis/docs/content/*.md >/dev/null 2>&1 && ! ls jarvis/docs/content/**/*.md >/dev/null 2>&1; then
    # No markdown files, nothing to copy
    exit 0
fi

echo -e "${BLUE}📋 Post-commit: Updating local Quartz preview...${NC}"

# Clear old content from Quartz
echo -e "${BLUE}   🗑️  Removing old preview content...${NC}"
rm -rf quartz-preview/content/*

# Copy new documentation to Quartz
echo -e "${BLUE}   📁 Copying updated docs to Quartz...${NC}"
cp -r jarvis/docs/content/* quartz-preview/content/

# Count files copied
FILE_COUNT=$(find quartz-preview/content -name "*.md" | wc -l)

echo -e "${GREEN}✨ Quartz preview updated with ${FILE_COUNT} markdown file(s)${NC}"
echo -e "${GREEN}   Run: cd quartz-preview && npx quartz build --serve${NC}"
echo -e "${GREEN}   Or:  ./preview-docs.sh (if script exists)${NC}"
echo ""
