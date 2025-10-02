# Setup Instructions: Complete Implementation Guide

**Difficulty**: Beginner to Intermediate
**Time Required**: 45-60 minutes
**Prerequisites**: Git installed, Python 3.7+, GitHub account

---

## Table of Contents

1. [Pre-Setup Checklist](#pre-setup-checklist)
2. [Phase 1: Install Git Hook](#phase-1-install-git-hook)
3. [Phase 2: Test Documentation Generation](#phase-2-test-documentation-generation)
4. [Phase 3: Configure GitHub Repository](#phase-3-configure-github-repository)
5. [Phase 4: Set Up GitHub Actions](#phase-4-set-up-github-actions)
6. [Phase 5: Perform First Squash Merge](#phase-5-perform-first-squash-merge)
7. [Phase 6: Deploy to GitHub Pages](#phase-6-deploy-to-github-pages)
8. [Verification](#verification)
9. [Next Steps](#next-steps)

---

## Pre-Setup Checklist

Before starting, verify you have:

- [ ] Git installed and configured
- [ ] Python 3.7 or higher installed
- [ ] GitHub account created
- [ ] Repository pushed to GitHub (or ready to create)
- [ ] Terminal/command line access
- [ ] Text editor (VS Code, vim, nano, etc.)

### Check Your Environment

```bash
# Check git
git --version
# Should show: git version 2.x.x or higher

# Check Python
python --version
# or
python3 --version
# Should show: Python 3.7.x or higher

# Verify you're in the correct directory
pwd
# Should show: /path/to/jarvis-streamdeck

# Check current branch
git branch
# Should show dev branch exists
```

---

## Phase 1: Install Git Hook

The pre-commit hook automates documentation generation.

### Step 1.1: Copy Hook Script

```bash
# From repository root
cp jarvis/utils/pre-commit-hook.sh .git/hooks/pre-commit
```

### Step 1.2: Make Hook Executable

```bash
chmod +x .git/hooks/pre-commit
```

### Step 1.3: Verify Hook Installation

```bash
# Check that hook exists and is executable
ls -la .git/hooks/pre-commit
```

**Expected output**:
```
-rwxr-xr-x 1 user user 8234 Oct 02 12:34 .git/hooks/pre-commit
```

The first `x` after `-rwx` indicates it's executable.

### Step 1.4: Test Hook

```bash
# Switch to dev branch
git checkout dev

# Make a small change to test the hook
echo "# Test comment" >> jarvis/test_hook.py

# Try to commit
git add jarvis/test_hook.py
git commit -m "Test pre-commit hook"
```

**Expected output**:
```
🔍 Running Jarvis pre-commit hooks on branch: dev
🚀 DEV BRANCH WORKFLOW: Documentation generation
📝 Python files in jarvis/ modified, generating documentation...
✅ Documentation generated successfully
📁 Staged updated documentation files
✨ Pre-commit hooks completed successfully
```

### Step 1.5: Clean Up Test

```bash
# Remove test file
git reset HEAD~1  # Undo the commit
rm jarvis/test_hook.py
```

**✅ Phase 1 Complete!** Git hook is installed and working.

---

## Phase 2: Test Documentation Generation

Before integrating with git, test the documentation scripts manually.

### Step 2.1: Test Comment Extraction

```bash
# Test extraction on a single file
python jarvis/utils/extract_comments.py jarvis/actions/actions.py
```

**Expected output**:
```
======================================================================
File: jarvis/actions/actions.py
======================================================================
Total tagged comment blocks: 45

Comments by tag:
  EDU: 12 block(s)
    Block 1 (line 109):
      Context: function: init_module
      Preview: COMPUTER SCIENCE EDUCATION: DESIGN PATTERNS COMPARISON...
```

### Step 2.2: Test on Entire Directory

```bash
# Extract from all files
python jarvis/utils/extract_comments.py jarvis/ --recursive
```

**What to look for**:
- Number of files processed
- Total comments found
- Any errors (there shouldn't be any)

### Step 2.3: Test Documentation Generation

```bash
# Generate markdown documentation
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/
```

**Expected output**:
```
Extracting comments from jarvis/...
Found tagged comments in 8 file(s)
Generating documentation in jarvis/docs/content/...
Generating category indices...
Generating main index...
✓ Generated 15 documentation file(s)

======================================================================
Documentation Generation Complete
======================================================================
Files processed: 8
Docs generated: 15
Categories: EDU, NOTE, IMPORTANT
Output directory: jarvis/docs/content/
```

### Step 2.4: Inspect Generated Documentation

```bash
# List generated files
ls -R jarvis/docs/content/

# View the main index
cat jarvis/docs/content/index.md

# View an educational doc
cat jarvis/docs/content/educational/actions.md
```

### Step 2.5: Test Comment Stripping (Optional)

```bash
# Test stripping on a single file (dry run)
python jarvis/utils/strip_comments.py jarvis/actions/actions.py --dry-run
```

**Expected output** (shows what would be removed):
```
======================================================================
File Stripping Summary
======================================================================
Input: jarvis/actions/actions.py
Output: jarvis/actions/actions.py
Original lines: 450
Output lines: 320
Lines removed: 130
Blocks removed: 15
Reduction: 28.9%

[DRY RUN] No files were modified.
```

**✅ Phase 2 Complete!** All scripts are working correctly.

---

## Phase 3: Configure GitHub Repository

Set up your GitHub repository for the workflow.

### Step 3.1: Create GitHub Repository (if not exists)

If you haven't already pushed to GitHub:

```bash
# On GitHub website:
# 1. Go to github.com
# 2. Click "New repository"
# 3. Name: jarvis-streamdeck
# 4. Description: Personal assistant using ElGato StreamDeck
# 5. Public or Private (your choice)
# 6. Do NOT initialize with README
# 7. Click "Create repository"
```

### Step 3.2: Configure Remote

```bash
# If repository doesn't have a remote yet
git remote add origin https://github.com/YOUR_USERNAME/jarvis-streamdeck.git

# If remote exists, verify it
git remote -v
```

**Expected output**:
```
origin  https://github.com/YOUR_USERNAME/jarvis-streamdeck.git (fetch)
origin  https://github.com/YOUR_USERNAME/jarvis-streamdeck.git (push)
```

### Step 3.3: Create .gitignore (if not exists)

```bash
# Create or edit .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project-specific
jarvis_prod/
*.log
config.env

# Temporary files
*.tmp
*.bak
EOF
```

### Step 3.4: Configure Branch Protection (Optional but Recommended)

On GitHub website:
1. Go to repository → Settings → Branches
2. Add branch protection rule for `main`
3. Enable: "Require pull request reviews before merging"
4. This prevents accidental direct commits to main

**✅ Phase 3 Complete!** GitHub repository is configured.

---

## Phase 4: Set Up GitHub Actions

Enable automated deployment to GitHub Pages.

### Step 4.1: Verify GitHub Actions Workflow Exists

```bash
# Check that workflow file exists
ls -la .github/workflows/deploy-docs.yml
```

If it doesn't exist, it was created by the setup in this repository.

### Step 4.2: Enable GitHub Pages

On GitHub website:
1. Go to repository → Settings → Pages
2. Source: Select "GitHub Actions" (not "Deploy from branch")
3. Click Save

### Step 4.3: Verify Actions Are Enabled

On GitHub website:
1. Go to repository → Settings → Actions → General
2. Ensure "Allow all actions and reusable workflows" is selected
3. Click Save

### Step 4.4: Grant Workflow Permissions

On GitHub website:
1. Go to repository → Settings → Actions → General
2. Scroll to "Workflow permissions"
3. Select "Read and write permissions"
4. Check "Allow GitHub Actions to create and approve pull requests"
5. Click Save

**✅ Phase 4 Complete!** GitHub Actions is ready.

---

## Phase 5: Perform First Squash Merge

Now that everything is set up, perform your first squash merge from dev to main.

### Step 5.1: Ensure Dev is Clean

```bash
# Make sure you're on dev
git checkout dev

# Commit any pending changes
git status

# If there are uncommitted changes:
git add .
git commit -m "Prepare for first squash merge to main"
```

### Step 5.2: Review What Will Be Merged

```bash
# See all commits that will be squashed
git log --oneline main..dev

# See the actual changes
git diff main...dev --stat
```

### Step 5.3: Switch to Main and Squash Merge

```bash
# Switch to main branch
git checkout main

# Perform squash merge
git merge --squash dev
```

### Step 5.4: Review Staged Changes

```bash
# See what will be committed
git status

# See detailed changes
git diff --staged --stat
```

### Step 5.5: Create the Squash Commit

```bash
git commit -m "Initial release of Jarvis StreamDeck system

Complete implementation of personal assistant using ElGato StreamDeck XL.

Features:
- Custom action system for system automation
- Dynamic layout management with visual feedback
- Extensive configuration system
- Integration with Linux system tools (ydotool, wmctrl, xdotool)
- Modular architecture with separation of concerns
- Auto-generated documentation from code comments

Built on python-elgato-streamdeck library with custom enhancements
for personal productivity workflows.

🤖 Generated with Claude Code
https://claude.com/claude-code"
```

### Step 5.6: Verify the Merge

```bash
# Check commit history
git log --oneline -5

# Verify files match dev
git diff dev --stat
# Should show no differences!
```

**✅ Phase 5 Complete!** First squash merge is done!

---

## Phase 6: Deploy to GitHub Pages

Push to GitHub and trigger automatic deployment.

### Step 6.1: Push Main Branch

```bash
# Push main to GitHub
git push origin main
```

### Step 6.2: Monitor GitHub Actions

1. Go to GitHub repository
2. Click "Actions" tab
3. You should see workflow "Deploy Documentation to GitHub Pages" running
4. Click on the workflow to see progress

**Expected steps**:
- ✓ Checkout repository
- ✓ Setup Node.js
- ✓ Install Quartz
- ✓ Copy documentation
- ✓ Build Quartz site
- ✓ Deploy to GitHub Pages

### Step 6.3: Wait for Deployment

Deployment takes 3-5 minutes. You'll see:
```
Deploy to GitHub Pages ✓
```

### Step 6.4: Visit Your Documentation Site

Go to:
```
https://YOUR_USERNAME.github.io/jarvis-streamdeck/
```

**You should see**:
- Main index page with categories
- Navigation to Educational Content, Notes, etc.
- Properly formatted markdown
- Working links

### Step 6.5: Push Dev Branch (Optional)

If you want to back up your dev branch to GitHub:

```bash
# Push dev to a private remote (if repo is private)
git checkout dev
git push origin dev
```

**Note**: For public repos, consider NOT pushing dev to keep your messy history private.

**✅ Phase 6 Complete!** Documentation is live!

---

## Verification

Let's verify everything works end-to-end.

### Checklist

- [ ] Git hook is installed and executable
- [ ] Documentation scripts work (tested manually)
- [ ] GitHub repository is configured
- [ ] GitHub Actions workflow exists
- [ ] GitHub Pages is enabled
- [ ] First squash merge completed successfully
- [ ] Documentation is live on GitHub Pages
- [ ] All commits are in proper branches

### Test the Complete Workflow

```bash
# 1. Make a change in dev
git checkout dev
echo "# EDU: This is a test educational comment" >> jarvis/test.py

# 2. Commit (hook runs automatically)
git add jarvis/test.py
git commit -m "Test: Add educational comment"
# Hook should generate docs automatically

# 3. Check that docs were generated
ls jarvis/docs/content/

# 4. When ready, merge to main
git checkout main
git merge --squash dev
git commit -m "Add test feature"

# 5. Push to GitHub (triggers deployment)
git push origin main

# 6. Wait a few minutes, then check your site
# https://YOUR_USERNAME.github.io/jarvis-streamdeck/
```

---

## Next Steps

### Daily Workflow

From now on, your workflow is:

```bash
# 1. Work in dev branch
git checkout dev

# 2. Make changes, commit normally
# (docs auto-generated by pre-commit hook)
git add .
git commit -m "Add new feature"

# 3. When ready for release, squash merge to main
git checkout main
git merge --squash dev
git commit -m "Release v1.1"

# 4. Push (docs auto-deploy)
git push origin main
```

### Recommended Reading

- [04_INTEGRATION_GUIDE.md](./04_INTEGRATION_GUIDE.md) - How workflows work together
- [07_TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md) - Common issues
- [08_TECHNICAL_REFERENCE.md](./08_TECHNICAL_REFERENCE.md) - Script details

### Optional Enhancements

1. **Add More Tags**: Edit `extract_comments.py` to support custom tags
2. **Customize Quartz Theme**: Modify `.github/workflows/deploy-docs.yml`
3. **Add CI/CD Tests**: Create test workflow for your code
4. **Set Up Branch Protection**: Prevent accidental commits to main

---

## Troubleshooting

### Hook Doesn't Run

**Problem**: Pre-commit hook doesn't execute
**Solution**:
```bash
chmod +x .git/hooks/pre-commit
```

### Python Not Found

**Problem**: Hook says "Python not found"
**Solution**:
```bash
# Check Python installation
which python python3

# If not installed, install Python 3.7+
```

### Documentation Not Generated

**Problem**: Hook runs but no docs generated
**Solution**:
```bash
# Run manually to see errors
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/
```

### GitHub Pages Not Working

**Problem**: Site doesn't deploy
**Solution**:
1. Check Settings → Pages → Source is "GitHub Actions"
2. Check Actions tab for error messages
3. Verify workflow file exists: `.github/workflows/deploy-docs.yml`

---

## Success!

🎉 **Congratulations!** You've successfully set up:

- ✅ Automated documentation extraction from code comments
- ✅ Git hooks for pre-commit automation
- ✅ Squash merge workflow for clean git history
- ✅ GitHub Actions for CI/CD
- ✅ GitHub Pages deployment with Quartz

Your repository now demonstrates professional Docs-as-Code practices, perfect for your technical writing portfolio!

---

**Questions?** See [07_TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md) or open an issue on GitHub.
