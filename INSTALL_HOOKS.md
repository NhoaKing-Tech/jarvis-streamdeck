# Git Hooks Installation Guide

Quick guide to install git hooks for the documentation pipeline.

---

## What Are Git Hooks?

Git hooks are scripts that run automatically at specific points in your git workflow:

- **Pre-commit**: Runs BEFORE commit completes (generates docs)
- **Post-commit**: Runs AFTER commit completes (updates local preview)

---

## Quick Installation

### One-Command Install (Recommended)

```bash
# From repository root
cd /home/nhoaking/Zenith/jarvis-streamdeck

# Install both hooks at once
cp jarvis/utils/pre-commit-hook.sh .git/hooks/pre-commit && \
cp jarvis/utils/post-commit-hook.sh .git/hooks/post-commit && \
chmod +x .git/hooks/pre-commit .git/hooks/post-commit && \
echo "✅ Git hooks installed successfully!"
```

---

## Manual Installation

### Step 1: Install Pre-Commit Hook

```bash
# Copy hook
cp jarvis/utils/pre-commit-hook.sh .git/hooks/pre-commit

# Make executable
chmod +x .git/hooks/pre-commit

# Verify
ls -la .git/hooks/pre-commit
# Should show: -rwxr-xr-x
```

### Step 2: Install Post-Commit Hook

```bash
# Copy hook
cp jarvis/utils/post-commit-hook.sh .git/hooks/post-commit

# Make executable
chmod +x .git/hooks/post-commit

# Verify
ls -la .git/hooks/post-commit
# Should show: -rwxr-xr-x
```

---

## What Each Hook Does

### Pre-Commit Hook (runs BEFORE commit)

**Triggers**: When you run `git commit`

**What it does**:
1. Detects if Python files in `jarvis/` were modified
2. Runs `generate_docs.py` to extract comments
3. Creates markdown files in `jarvis/docs/content/`
4. Stages the markdown files
5. Allows commit to proceed (with docs included)

**You'll see**:
```
🔍 Running Jarvis pre-commit hooks on branch: dev
📝 Python files in jarvis/ modified, generating documentation...
✅ Documentation generated successfully
📁 Staged updated documentation files
✨ Pre-commit hooks completed successfully
```

---

### Post-Commit Hook (runs AFTER commit)

**Triggers**: After commit completes successfully

**What it does**:
1. Checks if you have `quartz-preview/` set up
2. Deletes old content from `quartz-preview/content/`
3. Copies new docs from `jarvis/docs/content/`
4. Updates your local preview automatically

**You'll see**:
```
📋 Post-commit: Updating local Quartz preview...
   🗑️  Removing old preview content...
   📁 Copying updated docs to Quartz...
✨ Quartz preview updated with 15 markdown file(s)
   Run: cd quartz-preview && npx quartz build --serve
```

**Note**: Only runs on `dev` branch and only if `quartz-preview/` exists.

---

## Complete Workflow After Installation

### Before Hooks (Manual Process):

```bash
# 1. Edit code
vim jarvis/actions/actions.py

# 2. Commit
git commit -m "Add feature"

# 3. Manually generate docs
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/

# 4. Manually copy to Quartz
cp -r jarvis/docs/content/* quartz-preview/content/

# 5. Preview
cd quartz-preview && npx quartz build --serve
```

### After Hooks (Automated!):

```bash
# 1. Edit code

# 2. Commit (hooks do everything automatically!)
git commit -m "Add feature"
# ↓ Pre-commit: Generates docs automatically
# ↓ Post-commit: Updates Quartz preview automatically

# 3. Preview (already updated!)
cd quartz-preview && npx quartz build --serve
```

---

## Verification

### Test Pre-Commit Hook

```bash
# Make a small change
echo "# EDU: Test comment" >> jarvis/test.py

# Commit (hook should run)
git add jarvis/test.py
git commit -m "Test pre-commit hook"

# You should see: "✅ Documentation generated successfully"

# Clean up
git reset --hard HEAD~1
rm jarvis/test.py
```

### Test Post-Commit Hook

```bash
# Make sure quartz-preview exists
ls quartz-preview/

# Make a change
echo "# EDU: Another test" >> jarvis/actions/actions.py

# Commit
git add jarvis/actions/actions.py
git commit -m "Test post-commit hook"

# You should see: "✨ Quartz preview updated with X markdown file(s)"

# Verify files were copied
ls quartz-preview/content/
```

---

## Troubleshooting

### Hooks Don't Run

**Problem**: No output when committing

**Solution**:
```bash
# Check hooks are executable
ls -la .git/hooks/pre-commit .git/hooks/post-commit
# Should show -rwxr-xr-x

# If not:
chmod +x .git/hooks/pre-commit .git/hooks/post-commit
```

### Post-Commit Says "No quartz-preview/"

**Problem**: Post-commit skips because no Quartz

**Solution**: This is normal if you haven't set up local Quartz preview yet.

**To set up Quartz**: Follow [jarvis/git_docs/09_QUARTZ_PREVIEW.md](jarvis/git_docs/09_QUARTZ_PREVIEW.md)

### Pre-Commit Fails

**Problem**: "Documentation generation failed"

**Solution**:
```bash
# Test manually
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/

# Check for errors
# Fix any Python syntax errors in your code
```

---

## Disabling Hooks Temporarily

### Skip Hooks for One Commit

```bash
# Skip ALL hooks (not recommended)
git commit --no-verify -m "Message"
```

### Disable Permanently

```bash
# Rename to disable
mv .git/hooks/pre-commit .git/hooks/pre-commit.disabled
mv .git/hooks/post-commit .git/hooks/post-commit.disabled

# Re-enable later
mv .git/hooks/pre-commit.disabled .git/hooks/pre-commit
mv .git/hooks/post-commit.disabled .git/hooks/post-commit
```

---

## Uninstall

```bash
# Remove hooks
rm .git/hooks/pre-commit
rm .git/hooks/post-commit

# Hooks are now disabled
```

---

## Summary

**After installation, your workflow becomes**:

```bash
# Edit code with #EDU comments
vim jarvis/actions/actions.py

# Commit
git commit -m "Add feature"

# ✨ AUTOMATIC:
# - Docs generated (pre-commit)
# - Quartz preview updated (post-commit)

# Just preview!
cd quartz-preview && npx quartz build --serve
```

**Everything is automated!** 🎉

---

## Related Documentation

- [03_SETUP_INSTRUCTIONS.md](jarvis/git_docs/03_SETUP_INSTRUCTIONS.md) - Complete setup
- [09_QUARTZ_PREVIEW.md](jarvis/git_docs/09_QUARTZ_PREVIEW.md) - Quartz setup
- [07_TROUBLESHOOTING.md](jarvis/git_docs/07_TROUBLESHOOTING.md) - Issues & solutions
