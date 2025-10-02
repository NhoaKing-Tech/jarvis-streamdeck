#!/bin/bash
#
# Pre-commit Hook for Jarvis Documentation Pipeline
# ==================================================
#
# This hook implements the documentation automation workflow:
# - DEV BRANCH: Generates documentation from tagged comments
# - MAIN BRANCH: Verifies only clean code is committed
#
# Installation:
#   cp jarvis/utils/pre-commit-hook.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get current branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

echo -e "${BLUE}🔍 Running Jarvis pre-commit hooks on branch: ${CURRENT_BRANCH}${NC}"

# Change to project root
cd "$(git rev-parse --show-toplevel)"

# Initialize conda for bash (if available)
if command -v conda &> /dev/null; then
    eval "$(conda shell.bash hook)" 2>/dev/null || true
fi

# Try to activate jarvis-busybee conda environment
if conda info --envs 2>/dev/null | grep -q "jarvis-busybee"; then
    echo -e "${BLUE}🐍 Activating jarvis-busybee conda environment...${NC}"
    conda activate jarvis-busybee 2>/dev/null || {
        echo -e "${YELLOW}⚠️  Failed to activate jarvis-busybee environment, using system python${NC}"
    }
else
    echo -e "${BLUE}📍 No jarvis-busybee conda environment found, using system python${NC}"
fi

# Check if we have Python available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}❌ Python not found, skipping hooks${NC}"
    exit 0
fi

# Use python if available (from conda env), otherwise python3
PYTHON_CMD="python"
if ! command -v python &> /dev/null; then
    PYTHON_CMD="python3"
fi

# ============================================================================
# BRANCH-SPECIFIC WORKFLOWS
# ============================================================================

if [[ "$CURRENT_BRANCH" == "dev" ]]; then
    echo -e "${GREEN}🚀 DEV BRANCH WORKFLOW: Documentation generation${NC}"

    # Check if jarvis/utils exists
    if [ ! -d "jarvis/utils" ]; then
        echo -e "${YELLOW}⚠️  jarvis/utils directory not found, skipping hooks${NC}"
        exit 0
    fi

    # Check if any Python files in jarvis/ have been modified (excluding docs_utils)
    MODIFIED_PY_FILES=$(git diff --cached --name-only | grep -E '^jarvis/.*\.py$' | grep -v '^jarvis/docs_utils/' || true)

    if [ -n "$MODIFIED_PY_FILES" ]; then
        echo -e "${BLUE}📝 Python files in jarvis/ modified, generating documentation...${NC}"

        # Create docs output directory if it doesn't exist
        mkdir -p jarvis/docs/content

        # Generate documentation from tagged comments
        if $PYTHON_CMD jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/; then
            echo -e "${GREEN}✅ Documentation generated successfully${NC}"

            # Stage generated documentation files
            git add jarvis/docs/content/*.md 2>/dev/null || true
            git add jarvis/docs/content/**/*.md 2>/dev/null || true
            echo -e "${GREEN}📁 Staged updated documentation files${NC}"
        else
            echo -e "${RED}❌ Documentation generation failed${NC}"
            echo -e "${YELLOW}💡 Check that jarvis/utils/generate_docs.py and extract_comments.py exist${NC}"
            echo -e "${YELLOW}💡 You can skip this check with: git commit --no-verify${NC}"
            exit 1
        fi
    else
        echo -e "${BLUE}ℹ️  No Python files modified in jarvis/, skipping doc generation${NC}"
    fi

    # Check if documentation utils were modified
    if git diff --cached --name-only | grep -E '^jarvis/(utils|git_docs)/.*\.(py|md)$' > /dev/null; then
        echo -e "${BLUE}📚 Documentation scripts or guides modified${NC}"
    fi

elif [[ "$CURRENT_BRANCH" == "main" ]]; then
    echo -e "${GREEN}🏭 MAIN BRANCH WORKFLOW: Auto-strip production tags${NC}"

    # Get list of Python files in jarvis/ being committed
    PYTHON_FILES=$(git diff --cached --name-only | grep -E '^jarvis/.*\.py$' || true)

    if [ -n "$PYTHON_FILES" ]; then
        echo -e "${BLUE}🧹 Auto-stripping EDU and REVIEW tags from Python files...${NC}"

        # Check if strip_comments.py exists
        if [ ! -f "jarvis/utils/strip_comments.py" ]; then
            echo -e "${RED}❌ Error: jarvis/utils/strip_comments.py not found${NC}"
            echo -e "${YELLOW}💡 Commit with --no-verify to skip, or add the script${NC}"
            exit 1
        fi

        # Create a temporary directory for processing
        TEMP_DIR=$(mktemp -d)
        trap "rm -rf $TEMP_DIR" EXIT

        STRIPPED_COUNT=0
        TOTAL_LINES_REMOVED=0

        for file in $PYTHON_FILES; do
            if [ -f "$file" ]; then
                # Check if file contains tags that should be stripped (EDU or REVIEW only)
                if grep -E '^\s*#\s*(EDU|REVIEW)[\s:]' "$file" > /dev/null; then
                    echo -e "${BLUE}   📝 Stripping tags from: $file${NC}"

                    # Copy file to temp location
                    TEMP_FILE="$TEMP_DIR/$(basename $file)"
                    cp "$file" "$TEMP_FILE"

                    # Strip comments (only EDU and REVIEW tags by default)
                    if $PYTHON_CMD jarvis/utils/strip_comments.py "$file" --output "$TEMP_FILE" 2>/dev/null; then
                        # Count lines removed
                        ORIGINAL_LINES=$(wc -l < "$file")
                        NEW_LINES=$(wc -l < "$TEMP_FILE")
                        LINES_REMOVED=$((ORIGINAL_LINES - NEW_LINES))

                        if [ $LINES_REMOVED -gt 0 ]; then
                            # Replace the file with stripped version
                            cp "$TEMP_FILE" "$file"

                            # Re-stage the modified file
                            git add "$file"

                            STRIPPED_COUNT=$((STRIPPED_COUNT + 1))
                            TOTAL_LINES_REMOVED=$((TOTAL_LINES_REMOVED + LINES_REMOVED))

                            echo -e "${GREEN}      ✓ Removed $LINES_REMOVED lines${NC}"
                        fi
                    else
                        echo -e "${RED}      ✗ Failed to strip comments from $file${NC}"
                        exit 1
                    fi
                fi
            fi
        done

        if [ $STRIPPED_COUNT -gt 0 ]; then
            echo -e "${GREEN}✅ Stripped tags from $STRIPPED_COUNT file(s), removed $TOTAL_LINES_REMOVED lines${NC}"
            echo -e "${BLUE}   Kept tags: NOTE, IMPORTANT, OPTIMIZE, TODO, DEBUG, FIXME, HACK${NC}"
        else
            echo -e "${GREEN}✅ No EDU/REVIEW tags found - code is already clean${NC}"
        fi
    fi

    # Verify documentation exists
    if [ -d "jarvis/docs/content" ]; then
        DOC_COUNT=$(find jarvis/docs/content -name "*.md" | wc -l)
        echo -e "${GREEN}✅ Found ${DOC_COUNT} documentation file(s)${NC}"
    else
        echo -e "${YELLOW}⚠️  No documentation directory found${NC}"
    fi

else
    echo -e "${BLUE}🔧 FEATURE BRANCH: Basic validation only${NC}"

    # For feature branches, just note what's being committed
    if git diff --cached --name-only | grep -E '\.py$' > /dev/null; then
        PY_COUNT=$(git diff --cached --name-only | grep -E '\.py$' | wc -l)
        echo -e "${BLUE}📝 Committing ${PY_COUNT} Python file(s)${NC}"
    fi
fi

# ============================================================================
# FINAL CHECKS (all branches)
# ============================================================================

# Check for common issues
echo -e "${BLUE}🔍 Running final checks...${NC}"

# Check for accidentally committed secrets/credentials
SENSITIVE_PATTERNS=(
    "password\s*=\s*['\"]"
    "api[_-]?key\s*=\s*['\"]"
    "secret\s*=\s*['\"]"
    "token\s*=\s*['\"]"
    "BEGIN PRIVATE KEY"
    "BEGIN RSA PRIVATE KEY"
)

FOUND_SENSITIVE=0
for pattern in "${SENSITIVE_PATTERNS[@]}"; do
    if git diff --cached | grep -iE "$pattern" > /dev/null; then
        echo -e "${RED}⚠️  WARNING: Possible sensitive data detected matching: $pattern${NC}"
        FOUND_SENSITIVE=1
    fi
done

if [ $FOUND_SENSITIVE -eq 1 ]; then
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}Review your changes carefully!${NC}"
    echo -e "${YELLOW}Press Ctrl+C to cancel, or wait 3 seconds to continue...${NC}"
    echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    sleep 3
fi

echo -e "${GREEN}✨ Pre-commit hooks completed successfully${NC}"
exit 0
