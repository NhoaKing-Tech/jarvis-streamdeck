# Git Hooks: Pre-Commit and Post-Commit

**Difficulty**: Beginner-Friendly
**Time Required**: 10 minutes setup
**Prerequisites**: Git installed, basic terminal knowledge

---

## Table of Contents

1. [What Are Git Hooks?](#what-are-git-hooks)
2. [The Two Hooks in This System](#the-two-hooks-in-this-system)
3. [Pre-Commit Hook Explained](#pre-commit-hook-explained)
4. [Post-Commit Hook Explained](#post-commit-hook-explained)
5. [Installation](#installation)
6. [Complete Automated Workflow](#complete-automated-workflow)
7. [What You'll See](#what-youll-see)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Usage](#advanced-usage)

---

## What Are Git Hooks?

### Simple Explanation

**Git hooks are automatic scripts that run at specific points in your git workflow.**

Think of them like "triggers" or "event handlers":
- You do something (like commit)
- Git automatically runs a script
- The script does useful work for you

### Analogy

**Git hooks are like automatic car features:**
- **Backup camera**: Automatically turns on when you shift to reverse
- **Headlights**: Automatically turn on when it's dark
- **Git hooks**: Automatically run scripts when you commit

---

### Types of Git Hooks

Git supports many hooks. We use two:

| Hook | When It Runs | Use Case |
|------|--------------|----------|
| **pre-commit** | BEFORE commit completes | Validate code, generate docs, run tests |
| **post-commit** | AFTER commit completes | Update files, sync preview, notifications |
| pre-push | Before pushing to remote | Run CI checks |
| post-merge | After merging branches | Update dependencies |
| prepare-commit-msg | Before commit message editor | Auto-fill commit message |

**We use**: pre-commit and post-commit

---

## The Two Hooks in This System

### Overview

```
You edit code
      ↓
git add .
      ↓
git commit -m "message"
      ↓
┌─────────────────────────────────────────┐
│  PRE-COMMIT HOOK (runs first)           │
│  • Extract comments from Python files   │
│  • Generate markdown documentation      │
│  • Stage markdown files                 │
│  • Let commit proceed                   │
└─────────────────────────────────────────┘
      ↓
Commit completes
      ↓
┌─────────────────────────────────────────┐
│  POST-COMMIT HOOK (runs after)          │
│  • Delete old quartz-preview/content/   │
│  • Copy new docs to Quartz              │
│  • Keep preview in sync                 │
└─────────────────────────────────────────┘
      ↓
Ready to preview!
```

---

## Pre-Commit Hook Explained

### Purpose

**Automatically generate documentation from code comments BEFORE the commit completes.**

This ensures your commits always include up-to-date documentation.

---

### What It Does (Step-by-Step)

#### Step 1: Detect Changes

```bash
# Hook checks: Did any Python files in jarvis/ change?
git diff --cached --name-only | grep -E '^jarvis/.*\.py$'
```

**If YES** → Continue to Step 2
**If NO** → Skip, nothing to do

---

#### Step 2: Extract Comments

```bash
# Runs your extraction script
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/
```

**What this does**:
- Scans all Python files in `jarvis/`
- Finds comments with tags (#EDU, #NOTE, etc.)
- Generates markdown files
- Saves to `jarvis/docs/content/`

---

#### Step 3: Stage Documentation

```bash
# Adds generated markdown to this commit
git add jarvis/docs/content/*.md
git add jarvis/docs/content/**/*.md
```

**Result**: Your commit now includes both:
- Your code changes
- Updated documentation

---

#### Step 4: Allow Commit

The hook exits with code `0` (success), allowing the commit to proceed.

---

### Branch-Specific Behavior

**On dev branch**:
- ✅ Generates documentation automatically
- ✅ Stages markdown files
- ✅ Includes docs in commit

**On main branch**:
- ✅ Checks for tagged comments (warns if found)
- ✅ Verifies code is clean for production
- ❌ Blocks commit if development tags detected

**On other branches**:
- ℹ️ Basic validation only
- ℹ️ Notes what's being committed

---

### Security Features

The pre-commit hook also checks for accidentally committed secrets:

```bash
# Patterns it detects:
- password = "..."
- api_key = "..."
- secret = "..."
- BEGIN PRIVATE KEY
```

**If found**: Warns you and gives 3 seconds to cancel (Ctrl+C)

---

## Post-Commit Hook Explained

### Purpose

**Automatically update your local Quartz preview AFTER the commit completes.**

This keeps `quartz-preview/content/` in sync with `jarvis/docs/content/` automatically.

---

### What It Does (Step-by-Step)

#### Step 1: Check Branch

```bash
# Only run on dev branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

if [[ "$CURRENT_BRANCH" != "dev" ]]; then
    exit 0  # Skip on other branches
fi
```

**Why?** Documentation generation happens on dev, so only update preview there.

---

#### Step 2: Check if Quartz Exists

```bash
# Check if you have local Quartz preview set up
if [ ! -d "quartz-preview" ]; then
    echo "No quartz-preview/ directory found. Skipping."
    exit 0
fi
```

**Graceful skip**: If you haven't set up Quartz, hook does nothing (no errors).

---

#### Step 3: Check if Docs Exist

```bash
# Make sure docs were generated
if [ ! -d "jarvis/docs/content" ]; then
    exit 0  # No docs, nothing to copy
fi
```

---

#### Step 4: Delete Old Preview Content

```bash
# Remove outdated files from Quartz
rm -rf quartz-preview/content/*
```

**Why delete first?**
- Ensures no stale files remain
- Prevents orphaned documentation
- Clean slate for new docs

---

#### Step 5: Copy New Documentation

```bash
# Copy fresh docs to Quartz
cp -r jarvis/docs/content/* quartz-preview/content/
```

**Result**: `quartz-preview/content/` now matches `jarvis/docs/content/`

---

#### Step 6: Report Success

```bash
FILE_COUNT=$(find quartz-preview/content -name "*.md" | wc -l)
echo "✨ Quartz preview updated with ${FILE_COUNT} markdown file(s)"
echo "   Run: cd quartz-preview && npx quartz build --serve"
```

Tells you:
- How many files were copied
- How to start the preview server

---

### What Gets Updated

**Source** (tracked by git):
```
jarvis/docs/content/
├── index.md
├── educational/
│   ├── actions.md
│   └── application.md
└── notes/
    └── implementation.md
```

**Destination** (NOT tracked, for preview only):
```
quartz-preview/content/
├── index.md                    ← Copied from jarvis/docs/content/
├── educational/
│   ├── actions.md              ← Copied
│   └── application.md          ← Copied
└── notes/
    └── implementation.md       ← Copied
```

---

## Installation

### Quick Install (Both Hooks)

```bash
# From repository root
cd /home/nhoaking/Zenith/jarvis-streamdeck

# Copy both hooks
cp jarvis/utils/pre-commit-hook.sh .git/hooks/pre-commit
cp jarvis/utils/post-commit-hook.sh .git/hooks/post-commit

# Make executable
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/post-commit

# Verify
ls -la .git/hooks/pre-commit .git/hooks/post-commit
# Should show: -rwxr-xr-x (note the x's)
```

---

### One-Line Install

```bash
cp jarvis/utils/pre-commit-hook.sh .git/hooks/pre-commit && \
cp jarvis/utils/post-commit-hook.sh .git/hooks/post-commit && \
chmod +x .git/hooks/pre-commit .git/hooks/post-commit && \
echo "✅ Git hooks installed successfully!"
```

---

### Verify Installation

```bash
# Check hooks exist and are executable
ls -la .git/hooks/

# You should see:
# -rwxr-xr-x pre-commit
# -rwxr-xr-x post-commit
```

The `-rwxr-xr-x` shows the execute permission (`x`).

---

## Complete Automated Workflow

### Before Installing Hooks (Manual Process)

```bash
# Step 1: Edit code
vim jarvis/actions/actions.py
# Add #EDU: Educational comment

# Step 2: Generate docs manually
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/

# Step 3: Stage everything manually
git add jarvis/actions/actions.py
git add jarvis/docs/content/

# Step 4: Commit
git commit -m "Add feature with docs"

# Step 5: Manually copy to Quartz
rm -rf quartz-preview/content/*
cp -r jarvis/docs/content/* quartz-preview/content/

# Step 6: Preview
cd quartz-preview && npx quartz build --serve
```

**Total manual steps**: 6

---

### After Installing Hooks (Automated!)

```bash
# Step 1: Edit code
vim jarvis/actions/actions.py
# Add #EDU: Educational comment

# Step 2: Commit (hooks do EVERYTHING else!)
git add jarvis/actions/actions.py
git commit -m "Add feature"

# Pre-commit hook automatically:
#   ✓ Generates docs → jarvis/docs/content/
#   ✓ Stages markdown files
#   ✓ Includes in commit

# Post-commit hook automatically:
#   ✓ Deletes old quartz-preview/content/*
#   ✓ Copies new jarvis/docs/content/*
#   ✓ Syncs local preview

# Step 3: Preview (already updated!)
cd quartz-preview && npx quartz build --serve
```

**Total manual steps**: 2 (edit + commit)

**Automation saves**: 4 manual steps every time!

---

## What You'll See

### Terminal Output Example

When you commit with both hooks installed:

```bash
$ git commit -m "Add observer pattern documentation"

🔍 Running Jarvis pre-commit hooks on branch: dev
🐍 Activating jarvis-busybee conda environment...
📝 Python files in jarvis/ modified, generating documentation...

Extracting comments from jarvis/...
Found tagged comments in 3 file(s)
Generating documentation in jarvis/docs/content/...
✓ Generated 8 documentation file(s)

✅ Documentation generated successfully
📁 Staged updated documentation files
✨ Pre-commit hooks completed successfully

[dev abc1234] Add observer pattern documentation
 4 files changed, 150 insertions(+), 12 deletions(-)
 create mode 100644 jarvis/docs/content/educational/observer-pattern.md

📋 Post-commit: Updating local Quartz preview...
   🗑️  Removing old preview content...
   📁 Copying updated docs to Quartz...
✨ Quartz preview updated with 15 markdown file(s)
   Run: cd quartz-preview && npx quartz build --serve
   Or:  ./preview-docs.sh (if script exists)
```

---

### What Each Section Means

**Pre-commit output**:
```
🔍 Running Jarvis pre-commit hooks on branch: dev
```
Hook started, detected dev branch

```
📝 Python files in jarvis/ modified, generating documentation...
```
Found changes to Python files, extracting docs

```
✅ Documentation generated successfully
📁 Staged updated documentation files
```
Docs created and added to commit

```
✨ Pre-commit hooks completed successfully
```
Hook finished, commit proceeding

---

**Commit output**:
```
[dev abc1234] Add observer pattern documentation
 4 files changed, 150 insertions(+), 12 deletions(-)
 create mode 100644 jarvis/docs/content/educational/observer-pattern.md
```
Normal git commit message, shows docs were included

---

**Post-commit output**:
```
📋 Post-commit: Updating local Quartz preview...
   🗑️  Removing old preview content...
   📁 Copying updated docs to Quartz...
✨ Quartz preview updated with 15 markdown file(s)
```
Preview automatically synced with new docs

---

## Troubleshooting

### Hooks Don't Run

**Symptom**: No output when committing, hooks seem inactive

**Cause**: Hooks not executable

**Solution**:
```bash
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/post-commit

# Verify
ls -la .git/hooks/pre-commit
# Should show: -rwxr-xr-x
```

---

### Pre-Commit Hook Fails

**Symptom**: "❌ Documentation generation failed"

**Cause**: Python error in generate_docs.py

**Solution**:
```bash
# Test manually to see error
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/

# Fix any errors shown
# Common issues:
# - Python syntax errors in your code
# - Missing dependencies
# - File permission issues
```

---

### Post-Commit Says "No quartz-preview/"

**Symptom**: Post-commit skips with message about missing directory

**Cause**: You haven't set up local Quartz preview

**Solution**: This is normal! The hook gracefully skips.

**If you want local preview**:
1. Follow [09_QUARTZ_PREVIEW.md](./09_QUARTZ_PREVIEW.md) to set up Quartz
2. Post-commit will automatically start working

---

### "Python not found" Error

**Symptom**: Hook errors about Python not being found

**Cause**: Python not in PATH, or conda environment issues

**Solution**:
```bash
# Check Python installation
which python python3

# If using conda, edit hook to use specific Python:
# Edit .git/hooks/pre-commit
# Change: PYTHON_CMD="python"
# To: PYTHON_CMD="/full/path/to/python"
```

---

### Changes Not in Quartz Preview

**Symptom**: Committed but preview shows old content

**Cause**: Quartz server needs restart

**Solution**:
```bash
# Stop Quartz (Ctrl+C in terminal running it)

# Restart
cd quartz-preview
npx quartz build --serve

# Hard refresh browser: Ctrl+Shift+R
```

---

## Advanced Usage

### Skipping Hooks Temporarily

Sometimes you need to commit without running hooks:

```bash
# Skip ALL hooks for this commit
git commit --no-verify -m "Emergency fix"

# Shorthand
git commit -n -m "Emergency fix"
```

**Use cases**:
- Emergency hotfixes
- WIP commits (you'll regenerate docs later)
- Testing hook modifications

**Warning**: Docs won't be generated/synced!

---

### Disabling Hooks

**Temporary disable** (easy to re-enable):
```bash
# Rename to disable
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled
mv .git/hooks/post-commit .git/hooks/post-commit.disabled

# Re-enable later
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
mv .git/hooks/post-commit.disabled .git/hooks/post-commit
```

**Permanent removal**:
```bash
rm .git/hooks/pre-commit
rm .git/hooks/post-commit
```

---

### Customizing Hooks

Hooks are just bash scripts! You can modify them:

```bash
# Edit pre-commit hook
vim .git/hooks/pre-commit

# Add custom logic:
# - Run linters (pylint, black)
# - Run tests
# - Check file sizes
# - Anything you want!
```

**Example additions**:

```bash
# Add to pre-commit hook:

# Run Python linter
if command -v pylint &> /dev/null; then
    pylint jarvis/*.py
fi

# Check for large files
find . -type f -size +10M | while read file; do
    echo "Warning: Large file detected: $file"
done
```

---

### Creating a Preview Script

The post-commit hook suggests running Quartz manually. Create a helper:

```bash
cat > preview-docs.sh << 'EOF'
#!/bin/bash
# Quick documentation preview
cd quartz-preview && npx quartz build --serve
EOF

chmod +x preview-docs.sh

# Now just run:
./preview-docs.sh
```

---

### Logging Hook Output

Useful for debugging:

```bash
# Add to top of .git/hooks/pre-commit or post-commit:
exec > >(tee -a /tmp/git-hooks.log) 2>&1

# Now all output is saved to /tmp/git-hooks.log
# View it anytime:
cat /tmp/git-hooks.log
```

---

## Testing Hooks

### Test Pre-Commit Hook

```bash
# Create test file with tagged comment
echo '# EDU: Test educational comment' >> jarvis/test_hook.py

# Stage it
git add jarvis/test_hook.py

# Commit (hook should run)
git commit -m "Test pre-commit hook"

# You should see:
# - "📝 Python files in jarvis/ modified, generating documentation..."
# - "✅ Documentation generated successfully"

# Check docs were generated
ls jarvis/docs/content/

# Clean up
git reset --hard HEAD~1
rm jarvis/test_hook.py
```

---

### Test Post-Commit Hook

```bash
# Prerequisites: Must have quartz-preview/ set up

# Edit existing file
echo '# NOTE: Test implementation note' >> jarvis/actions/actions.py

# Commit
git add jarvis/actions/actions.py
git commit -m "Test post-commit hook"

# You should see:
# - Pre-commit output (generates docs)
# - Normal commit message
# - "📋 Post-commit: Updating local Quartz preview..."
# - "✨ Quartz preview updated with X markdown file(s)"

# Verify files copied
ls quartz-preview/content/

# Clean up
git reset --hard HEAD~1
```

---

## Hook Workflow Diagram

### Complete Flow with Both Hooks

```
┌─────────────────────────────────────────────────────────────┐
│  1. YOU EDIT CODE                                           │
│  jarvis/actions/actions.py                                  │
│  # EDU: Observer pattern implementation                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  2. YOU STAGE AND COMMIT                                    │
│  git add jarvis/actions/actions.py                          │
│  git commit -m "Add observer pattern"                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  3. PRE-COMMIT HOOK RUNS                                    │
│  • Detects Python file changed                             │
│  • Runs extract_comments.py                                 │
│  • Generates markdown → jarvis/docs/content/               │
│  • Stages markdown files                                    │
│  • Returns success (allows commit)                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  4. COMMIT COMPLETES                                        │
│  [dev abc1234] Add observer pattern                         │
│  2 files changed:                                           │
│  • jarvis/actions/actions.py (your code)                    │
│  • jarvis/docs/content/educational/observer.md (generated)  │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  5. POST-COMMIT HOOK RUNS                                   │
│  • Checks branch (dev ✓)                                    │
│  • Checks quartz-preview exists ✓                           │
│  • Deletes quartz-preview/content/*                         │
│  • Copies jarvis/docs/content/* → quartz-preview/content/  │
│  • Reports success                                          │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  6. READY TO PREVIEW                                        │
│  cd quartz-preview && npx quartz build --serve              │
│  → http://localhost:8080 (shows your updated docs!)         │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary

### What Hooks Do

| Hook | Runs | Purpose | Output |
|------|------|---------|--------|
| **pre-commit** | Before commit | Generate docs from code | `jarvis/docs/content/` (tracked) |
| **post-commit** | After commit | Sync local preview | `quartz-preview/content/` (not tracked) |

---

### Files Involved

**Scripts** (you install these):
```
jarvis/utils/
├── pre-commit-hook.sh       → Copy to .git/hooks/pre-commit
└── post-commit-hook.sh      → Copy to .git/hooks/post-commit
```

**Hooks** (installed location):
```
.git/hooks/
├── pre-commit               ← Active hook
└── post-commit              ← Active hook
```

**Generated docs** (tracked by git):
```
jarvis/docs/content/         ← Pre-commit generates here
├── index.md
├── educational/
└── notes/
```

**Preview copy** (NOT tracked):
```
quartz-preview/content/      ← Post-commit copies here
├── index.md
├── educational/
└── notes/
```

---

### Key Benefits

✅ **Automation**: No manual doc generation
✅ **Consistency**: Docs always match code
✅ **Synchronization**: Preview always current
✅ **Version control**: Docs committed with code
✅ **Error prevention**: Hooks catch issues early

---

## Related Documentation

- **[02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md](./02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md)** - Overall documentation workflow
- **[03_SETUP_INSTRUCTIONS.md](./03_SETUP_INSTRUCTIONS.md)** - Complete system setup (includes hooks)
- **[09_QUARTZ_PREVIEW.md](./09_QUARTZ_PREVIEW.md)** - Setting up local Quartz preview
- **[07_TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md)** - Common issues and solutions
- **[INSTALL_HOOKS.md](../../INSTALL_HOOKS.md)** - Quick installation guide

---

## Quick Reference

### Installation
```bash
cp jarvis/utils/pre-commit-hook.sh .git/hooks/pre-commit && \
cp jarvis/utils/post-commit-hook.sh .git/hooks/post-commit && \
chmod +x .git/hooks/pre-commit .git/hooks/post-commit
```

### Test
```bash
echo '# EDU: Test' >> jarvis/test.py
git add jarvis/test.py
git commit -m "Test hooks"
# Clean up: git reset --hard HEAD~1 && rm jarvis/test.py
```

### Skip (when needed)
```bash
git commit --no-verify -m "Skip hooks"
```

### Disable
```bash
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled
mv .git/hooks/post-commit .git/hooks/post-commit.disabled
```

---

**With both hooks installed, your documentation stays perfectly synchronized with zero manual effort!** 🎉
