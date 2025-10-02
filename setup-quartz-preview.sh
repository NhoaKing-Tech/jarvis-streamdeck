#!/bin/bash
#
# Quartz Preview Setup Script
# ============================
#
# This script sets up a local Quartz installation for documentation preview.
# It cleans up unnecessary files and configures git to ignore the preview directory.
#
# USAGE:
#   1. Copy your Quartz installation to quartz-preview/
#   2. Run: ./setup-quartz-preview.sh
#
# AUTHOR: NhoaKing
# PROJECT: jarvis-streamdeck
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Quartz Preview Setup Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if quartz-preview directory exists
if [ ! -d "quartz-preview" ]; then
    echo -e "${RED}❌ Error: quartz-preview/ directory not found!${NC}"
    echo -e "${YELLOW}${NC}"
    echo -e "${YELLOW}Please copy your Quartz installation first:${NC}"
    echo -e "${YELLOW}  cp -r /path/to/your/quartz ./quartz-preview${NC}"
    echo -e "${YELLOW}${NC}"
    echo -e "${YELLOW}Then run this script again.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Found quartz-preview/ directory${NC}"
echo ""

# Navigate to quartz-preview
cd quartz-preview

echo -e "${BLUE}🗑️  Removing unnecessary files...${NC}"

# List of files/directories to remove
FILES_TO_REMOVE=(
    ".git"
    ".github"
    ".gitignore"
    ".gitattributes"
    "CODE_OF_CONDUCT.md"
    "CONTRIBUTING.md"
    "LICENSE.txt"
    "README.md"
)

# Remove each file/directory
REMOVED_COUNT=0
for item in "${FILES_TO_REMOVE[@]}"; do
    if [ -e "$item" ]; then
        rm -rf "$item"
        echo -e "${GREEN}   ✓ Removed: $item${NC}"
        REMOVED_COUNT=$((REMOVED_COUNT + 1))
    else
        echo -e "${YELLOW}   ℹ️  Not found (already removed?): $item${NC}"
    fi
done

echo ""
echo -e "${GREEN}✓ Removed $REMOVED_COUNT item(s)${NC}"
echo ""

# Go back to repo root
cd ..

# Add quartz-preview to .gitignore
echo -e "${BLUE}📝 Updating .gitignore...${NC}"

# Check if .gitignore exists
if [ ! -f ".gitignore" ]; then
    echo -e "${YELLOW}   ℹ️  Creating .gitignore file${NC}"
    touch .gitignore
fi

# Check if quartz-preview is already in .gitignore
if grep -q "^quartz-preview/" .gitignore 2>/dev/null || grep -q "^quartz-preview$" .gitignore 2>/dev/null; then
    echo -e "${GREEN}   ✓ quartz-preview/ already in .gitignore${NC}"
else
    # Add to .gitignore with a comment section
    cat >> .gitignore << 'EOF'

# ============================================
# Quartz Local Preview (not tracked by git)
# ============================================
# We use Quartz locally to preview docs, but don't commit it
# because GitHub Actions downloads it fresh for deployment

quartz-preview/
quartz/

# Quartz build outputs
**/public/
**/.quartz-cache/

# Node.js dependencies
node_modules/

EOF
    echo -e "${GREEN}   ✓ Added quartz-preview/ to .gitignore${NC}"
fi

echo ""

# Check if quartz-preview is tracked by git
if git ls-files --error-unmatch quartz-preview/ >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Warning: quartz-preview/ is currently tracked by git${NC}"
    echo -e "${YELLOW}   Removing from git cache...${NC}"
    git rm -r --cached quartz-preview/ >/dev/null 2>&1 || true
    echo -e "${GREEN}   ✓ Removed from git tracking${NC}"
    echo ""
fi

# Verify setup
echo -e "${BLUE}🔍 Verifying setup...${NC}"

# Check that key Quartz files exist
REQUIRED_FILES=(
    "quartz-preview/quartz"
    "quartz-preview/quartz.config.ts"
    "quartz-preview/package.json"
)

ALL_GOOD=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -e "$file" ]; then
        echo -e "${GREEN}   ✓ Found: $file${NC}"
    else
        echo -e "${RED}   ✗ Missing: $file${NC}"
        ALL_GOOD=false
    fi
done

echo ""

if [ "$ALL_GOOD" = false ]; then
    echo -e "${RED}⚠️  Warning: Some required Quartz files are missing!${NC}"
    echo -e "${YELLOW}   Make sure you copied a complete Quartz installation.${NC}"
    echo ""
fi

# Check if git ignores quartz-preview
if git check-ignore quartz-preview/ >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Git is correctly ignoring quartz-preview/${NC}"
else
    echo -e "${YELLOW}⚠️  Warning: Git might still be tracking quartz-preview/${NC}"
    echo -e "${YELLOW}   Run: git status${NC}"
    echo -e "${YELLOW}   If you see quartz-preview/, run: git rm -r --cached quartz-preview/${NC}"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✨ Quartz Preview Setup Complete!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Display next steps
echo -e "${BLUE}📋 Next Steps:${NC}"
echo ""
echo -e "1. Install dependencies:"
echo -e "   ${YELLOW}cd quartz-preview && npm install${NC}"
echo ""
echo -e "2. Generate your documentation:"
echo -e "   ${YELLOW}python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/${NC}"
echo ""
echo -e "3. Copy docs to Quartz:"
echo -e "   ${YELLOW}cp -r jarvis/docs/content/* quartz-preview/content/${NC}"
echo ""
echo -e "4. Start preview server:"
echo -e "   ${YELLOW}cd quartz-preview && npx quartz build --serve${NC}"
echo ""
echo -e "5. Open browser to: ${YELLOW}http://localhost:8080${NC}"
echo ""
echo -e "${BLUE}📚 For detailed instructions, see:${NC}"
echo -e "   ${YELLOW}jarvis/git_docs/09_QUARTZ_PREVIEW.md${NC}"
echo ""
echo -e "${GREEN}Happy documenting! 📝${NC}"
echo ""
