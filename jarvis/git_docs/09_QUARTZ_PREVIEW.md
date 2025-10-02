# Quartz Local Preview Setup Guide

**Difficulty**: Beginner-Friendly
**Time Required**: 15-20 minutes
**Prerequisites**: Node.js installed, basic terminal knowledge

---

## Table of Contents

1. [What is Quartz?](#what-is-quartz)
2. [How Quartz Works in This System](#how-quartz-works-in-this-system)
3. [Two Quartz Instances Explained](#two-quartz-instances-explained)
4. [Setting Up Local Preview](#setting-up-local-preview)
5. [Using Quartz for Preview](#using-quartz-for-preview)
6. [Understanding What Gets Tracked by Git](#understanding-what-gets-tracked-by-git)
7. [Troubleshooting](#troubleshooting)
8. [Advanced: Customizing Quartz](#advanced-customizing-quartz)

---

## What is Quartz?

**Think of Quartz like a website builder for documentation.**

### The Simple Explanation

You have markdown files (`.md`):
```markdown
# My Documentation
This is some documentation text.
```

Quartz transforms them into a beautiful website with:
- Navigation menus
- Search functionality
- Pretty styling
- Cross-references
- Mobile-friendly design

### Analogy

**Quartz is like WordPress for documentation:**
- **WordPress**: Takes blog posts → Creates beautiful blog website
- **Quartz**: Takes markdown files → Creates beautiful documentation website

### What Makes Quartz Special

Unlike simple markdown viewers, Quartz adds:
- 🔍 **Full-text search** across all docs
- 🔗 **Graph view** showing document relationships
- 📱 **Responsive design** (looks good on phones)
- 🎨 **Beautiful themes** (light/dark mode)
- ⚡ **Fast static site** (no database needed)
- 🌐 **GitHub Pages compatible**

---

## How Quartz Works in This System

Let me explain the **complete journey** of your documentation, from code comments to live website.

### The Complete Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: YOUR COMPUTER (Local Development)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  You write Python code:                                        │
│  ┌─────────────────────────────────────────┐                  │
│  │ # EDU: Design Pattern Explanation       │                  │
│  │ # EDU: This uses the Observer pattern   │                  │
│  │ def my_function():                       │                  │
│  │     pass                                 │                  │
│  └─────────────────────────────────────────┘                  │
│                     ↓                                           │
│  Pre-commit hook runs extract_comments.py:                     │
│  ┌─────────────────────────────────────────┐                  │
│  │ # Educational Content: My Function      │                  │
│  │                                          │                  │
│  │ ## Design Pattern Explanation           │                  │
│  │ This uses the Observer pattern...       │                  │
│  └─────────────────────────────────────────┘                  │
│           (Saved as .md file)                                  │
│                     ↓                                           │
│  [OPTIONAL] Local Quartz Preview:                              │
│  ┌─────────────────────────────────────────┐                  │
│  │  Beautiful website with navigation,     │                  │
│  │  search, and styling at:                │                  │
│  │  http://localhost:8080                  │                  │
│  └─────────────────────────────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                          ↓
                    git push origin main
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: GITHUB'S COMPUTERS (GitHub Actions)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  GitHub Actions workflow starts:                               │
│  ┌─────────────────────────────────────────┐                  │
│  │ 1. git clone YOUR_REPO                  │                  │
│  │    → Gets your markdown files           │                  │
│  └─────────────────────────────────────────┘                  │
│                     ↓                                           │
│  ┌─────────────────────────────────────────┐                  │
│  │ 2. git clone jackyzha0/quartz           │                  │
│  │    → Downloads Quartz (fresh copy)      │                  │
│  └─────────────────────────────────────────┘                  │
│                     ↓                                           │
│  ┌─────────────────────────────────────────┐                  │
│  │ 3. npm install                           │                  │
│  │    → Installs Quartz dependencies       │                  │
│  └─────────────────────────────────────────┘                  │
│                     ↓                                           │
│  ┌─────────────────────────────────────────┐                  │
│  │ 4. cp your_docs/* quartz/content/       │                  │
│  │    → Copies YOUR markdown to Quartz     │                  │
│  └─────────────────────────────────────────┘                  │
│                     ↓                                           │
│  ┌─────────────────────────────────────────┐                  │
│  │ 5. npx quartz build                     │                  │
│  │    → Builds static HTML website         │                  │
│  └─────────────────────────────────────────┘                  │
│                     ↓                                           │
│  ┌─────────────────────────────────────────┐                  │
│  │ 6. Upload to GitHub Pages               │                  │
│  │    → Deploys to your public URL         │                  │
│  └─────────────────────────────────────────┘                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: PUBLIC WEBSITE (GitHub Pages)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Your documentation is now live at:                            │
│  https://YOUR_USERNAME.github.io/jarvis-streamdeck/            │
│                                                                 │
│  Anyone can visit and see:                                     │
│  ✓ Beautiful formatted documentation                           │
│  ✓ Search functionality                                        │
│  ✓ Navigation between pages                                    │
│  ✓ Professional styling                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Insight: Quartz is Used Twice (But Differently)

1. **Local Quartz** (Optional): You run on your computer to preview
2. **GitHub Quartz** (Automatic): GitHub Actions runs to deploy

**Important**: These are completely separate! You don't commit your local Quartz to git.

---

## Two Quartz Instances Explained

This is often confusing for beginners, so let's break it down carefully.

### Instance 1: Local Quartz (Your Computer)

**Location**: `jarvis-streamdeck/quartz-preview/` (in `.gitignore`)

**Purpose**: Preview what your docs will look like BEFORE pushing to GitHub

**How it works**:
```bash
# You run this command:
npx quartz build --serve

# Quartz starts a local web server on your computer:
# → Opens http://localhost:8080
# → You see your docs as a website
# → Changes appear instantly when you refresh
```

**Think of it like**: A "Print Preview" before printing a document

**Tracked by git?** ❌ NO - It's in `.gitignore`

**Why not track it?**
- It's a build tool (like installing Microsoft Word - you use it, but don't commit it)
- Takes up lots of space (node_modules/ can be 100+ MB)
- GitHub Actions will install its own copy anyway

---

### Instance 2: GitHub Actions Quartz (GitHub's Computers)

**Location**: GitHub's temporary server (created fresh each time)

**Purpose**: Build and deploy your PRODUCTION documentation website

**How it works**:
```yaml
# In .github/workflows/deploy-docs.yml:

1. GitHub's computer starts (fresh, empty machine)
2. git clone YOUR_REPO → Gets your markdown
3. git clone jackyzha0/quartz → Gets Quartz (brand new copy)
4. npm install → Installs Quartz
5. Copy your markdown to quartz/content/
6. npx quartz build → Builds website
7. Deploy to GitHub Pages → Makes it public
8. Delete everything → Temporary server is destroyed
```

**Think of it like**: A factory that assembles your product (then throws away the assembly line)

**Tracked by git?** ❌ NO - GitHub downloads it fresh each time

**Why download fresh each time?**
- Always gets the latest version of Quartz
- No conflicts with your code
- Clean build every time

---

### Visual Comparison

```
┌──────────────────────────────────────────────────────────────┐
│                     LOCAL QUARTZ                             │
├──────────────────────────────────────────────────────────────┤
│  Location:     quartz-preview/ (your computer)               │
│  Purpose:      Preview before pushing                        │
│  Tracked:      NO (in .gitignore)                            │
│  Updates:      You update manually                           │
│  Audience:     Just you                                      │
│  Speed:        Instant (already installed)                   │
│  Command:      npx quartz build --serve                      │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                   GITHUB ACTIONS QUARTZ                      │
├──────────────────────────────────────────────────────────────┤
│  Location:     GitHub's server (temporary)                   │
│  Purpose:      Deploy production website                     │
│  Tracked:      NO (downloaded fresh)                         │
│  Updates:      Always latest version                         │
│  Audience:     Public (anyone on internet)                   │
│  Speed:        3-5 minutes (downloads everything)            │
│  Command:      Automatic (triggered by push)                 │
└──────────────────────────────────────────────────────────────┘
```

---

## Setting Up Local Preview

Let's set up Quartz on your computer for local previewing.

### Prerequisites Check

```bash
# Check if Node.js is installed
node --version
# Should show: v18.x.x or higher

npm --version
# Should show: 9.x.x or higher

# If not installed:
# Ubuntu/Debian: sudo apt install nodejs npm
# macOS: brew install node
# Or download from: https://nodejs.org/
```

---

### Method 1: Automated Setup with Script (Recommended - Easiest!)

We've created a script that automates the entire setup process!

#### Quick Setup

```bash
# Navigate to your jarvis-streamdeck repo
cd /home/nhoaking/Zenith/jarvis-streamdeck

# Copy your existing Quartz from another repo
cp -r /path/to/your/other/repo/quartz ./quartz-preview

# Run the setup script (does everything automatically!)
./setup-quartz-preview.sh
```

**What the script does automatically**:
1. ✅ Checks that `quartz-preview/` exists
2. ✅ Removes unnecessary files (`.git`, `.github`, `README.md`, etc.)
3. ✅ Adds `quartz-preview/` to `.gitignore`
4. ✅ Removes from git tracking (if already tracked)
5. ✅ Verifies required Quartz files are present
6. ✅ Shows next steps

**You'll see output like**:
```
========================================
  Quartz Preview Setup Script
========================================

✓ Found quartz-preview/ directory

🗑️  Removing unnecessary files...
   ✓ Removed: .git
   ✓ Removed: .github
   ✓ Removed: .gitignore
   ✓ Removed: .gitattributes
   ✓ Removed: CODE_OF_CONDUCT.md
   ✓ Removed: CONTRIBUTING.md
   ✓ Removed: LICENSE.txt
   ✓ Removed: README.md

✓ Removed 8 item(s)

📝 Updating .gitignore...
   ✓ Added quartz-preview/ to .gitignore

🔍 Verifying setup...
   ✓ Found: quartz-preview/quartz
   ✓ Found: quartz-preview/quartz.config.ts
   ✓ Found: quartz-preview/package.json

✓ Git is correctly ignoring quartz-preview/

========================================
✨ Quartz Preview Setup Complete!
========================================
```

**Benefits of using the script**:
- ⚡ Fast - One command does everything
- 🔒 Safe - Checks before removing files
- 📋 Consistent - Same setup every time
- ♻️ Reusable - Works for any repo with Quartz

---

### Method 2: Manual Setup (Alternative)

If you prefer to do it manually or want to understand each step:

#### Step 1: Copy Quartz (Without Git History)

```bash
# Navigate to your jarvis-streamdeck repo
cd /home/nhoaking/Zenith/jarvis-streamdeck

# Copy your existing Quartz
# Replace /path/to/your/other/repo with actual path
cp -r /path/to/your/other/repo/quartz ./quartz-preview

# CRITICAL: Remove Quartz's git history
rm -rf quartz-preview/.git
```

**Why remove `.git`?**
- Quartz has its own git history (thousands of commits)
- You don't want that mixed with YOUR project's history
- Removing `.git` makes it just a regular folder

#### Step 2: Clean Up Unnecessary Files

Quartz comes with files for their own project that you don't need:

```bash
cd quartz-preview

# Remove Quartz's GitHub workflows (you have your own!)
rm -rf .github

# Remove Quartz's git configuration
rm .gitignore .gitattributes

# Remove Quartz's community files
rm CODE_OF_CONDUCT.md CONTRIBUTING.md LICENSE.txt

# Remove Quartz's README (optional - you won't need it)
rm README.md

# Remove their content (you'll add yours)
rm -rf content/*
```

**What you're keeping**:
```
quartz-preview/
├── quartz/              ✓ Core Quartz code (needed)
├── quartz.config.ts     ✓ Configuration file (needed)
├── quartz.layout.ts     ✓ Layout settings (needed)
├── package.json         ✓ Dependencies list (needed)
├── package-lock.json    ✓ Dependency versions (needed)
├── tsconfig.json        ✓ TypeScript config (needed)
├── node_modules/        ✓ Installed packages (needed if already there)
└── content/             ✓ Empty - will hold YOUR docs
```

#### Step 3: Install Dependencies (If Needed)

```bash
# Still in quartz-preview/
cd /home/nhoaking/Zenith/jarvis-streamdeck/quartz-preview

# If node_modules/ doesn't exist or is incomplete:
npm install

# This downloads all dependencies Quartz needs
# Takes 1-2 minutes, downloads ~100MB
```

You'll see output like:
```
added 482 packages, and audited 483 packages in 1m
```

#### Step 4: Add to .gitignore

**VERY IMPORTANT**: Tell git to ignore your local Quartz.

```bash
# Go back to repo root
cd /home/nhoaking/Zenith/jarvis-streamdeck

# Add Quartz to .gitignore
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
package-lock.json

EOF
```

#### Step 5: Verify Git Doesn't See It

```bash
# Check git status
git status

# You should NOT see quartz-preview/ listed
# If you do, check your .gitignore is correct
```

**If git still sees it**:
```bash
# Make sure .gitignore is in the right place
ls -la .gitignore
# Should be in /home/nhoaking/Zenith/jarvis-streamdeck/.gitignore

# Check it contains the right lines
cat .gitignore | grep quartz-preview

# If needed, force git to ignore it
git rm -r --cached quartz-preview/
```

---

### Method 2: Fresh Installation (Alternative)

If you don't have Quartz elsewhere or want a fresh copy:

```bash
# In your repo root
cd /home/nhoaking/Zenith/jarvis-streamdeck

# Clone Quartz
git clone https://github.com/jackyzha0/quartz.git quartz-preview

# Remove git history
cd quartz-preview
rm -rf .git

# Install dependencies
npm install

# Clean up unnecessary files (same as Method 1 Step 2)
rm -rf .github .gitignore .gitattributes
rm CODE_OF_CONDUCT.md CONTRIBUTING.md LICENSE.txt README.md
rm -rf content/*

# Add to .gitignore (same as Method 1 Step 4)
cd ..
echo "quartz-preview/" >> .gitignore
```

---

## Using Quartz for Preview

Now that Quartz is set up, let's use it to preview your documentation.

### The Complete Preview Workflow

#### Step 1: Generate Your Documentation

First, create the markdown files from your code comments:

```bash
# From repo root
cd /home/nhoaking/Zenith/jarvis-streamdeck

# Generate docs from your code
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/
```

**What this does**:
- Scans all Python files in `jarvis/`
- Finds comments with tags (#EDU, #NOTE, etc.)
- Creates markdown files in `jarvis/docs/content/`

**You should see**:
```
Extracting comments from jarvis/...
Found tagged comments in 8 file(s)
Generating documentation in jarvis/docs/content/...
✓ Generated 15 documentation file(s)

Files processed: 8
Docs generated: 15
Categories: EDU, NOTE, IMPORTANT
```

#### Step 2: Copy Docs to Quartz

```bash
# Clear Quartz's content folder
rm -rf quartz-preview/content/*

# Copy YOUR generated docs to Quartz
cp -r jarvis/docs/content/* quartz-preview/content/

# Verify files were copied
ls -R quartz-preview/content/
```

**You should see**:
```
quartz-preview/content/:
index.md  educational/  notes/  important/

quartz-preview/content/educational/:
actions.md  application.md  lifecycle.md
...
```

#### Step 3: Build and Serve

```bash
# Navigate to Quartz
cd quartz-preview

# Build and start preview server
npx quartz build --serve
```

**What happens**:
```
1. Quartz reads all .md files in content/
2. Generates HTML pages with navigation
3. Adds search functionality
4. Applies styling and theme
5. Starts a local web server
6. Opens your browser automatically
```

**You'll see output like**:
```
Started a Quartz server listening at http://localhost:8080
hint: exit with ctrl+c
```

#### Step 4: View in Browser

Your browser should open automatically to `http://localhost:8080`

If not, manually open: **http://localhost:8080**

**You should see**:
- Your documentation homepage (index.md)
- Navigation menu on the left
- Search bar at the top
- Beautiful styling with your content

#### Step 5: Make Changes and Refresh

**Option A: Automatic (with post-commit hook - Recommended)**

If you've installed the post-commit hook, changes sync automatically:

```bash
# 1. Edit your Python code
vim jarvis/actions/actions.py
# Add #EDU comments

# 2. Commit (hooks do everything!)
git add jarvis/actions/actions.py
git commit -m "Update docs"

# Pre-commit hook: Generates docs → jarvis/docs/content/
# Post-commit hook: Copies to quartz-preview/content/ automatically!

# 3. Just refresh browser - changes are already there!
```

**To install post-commit hook**:
```bash
cp jarvis/utils/post-commit-hook.sh .git/hooks/post-commit
chmod +x .git/hooks/post-commit
```

See: [INSTALL_HOOKS.md](../../INSTALL_HOOKS.md) for details.

---

**Option B: Manual (without post-commit hook)**

If you haven't installed the post-commit hook:

```bash
# In another terminal (keep Quartz running):
cd /home/nhoaking/Zenith/jarvis-streamdeck

# Regenerate docs
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/

# Copy to Quartz
rm -rf quartz-preview/content/*
cp -r jarvis/docs/content/* quartz-preview/content/

# In browser: Refresh the page
# Changes appear immediately!
```

**Or use this one-liner**:
```bash
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/ && \
rm -rf quartz-preview/content/* && \
cp -r jarvis/docs/content/* quartz-preview/content/
```

#### Step 6: Stop the Server

When done previewing:

```bash
# In the terminal running Quartz:
# Press Ctrl+C

# Server stops
```

---

### Creating a Preview Helper Script

To make this easier, create a helper script:

```bash
# From repo root
cat > preview-docs.sh << 'EOF'
#!/bin/bash
#
# Quick documentation preview script
# Usage: ./preview-docs.sh
#

set -e

echo "🔄 Generating documentation from code..."
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/

echo "📋 Copying to Quartz..."
rm -rf quartz-preview/content/*
cp -r jarvis/docs/content/* quartz-preview/content/

echo "🚀 Starting preview server..."
echo "   Opening http://localhost:8080"
echo "   Press Ctrl+C to stop"
echo ""

cd quartz-preview
npx quartz build --serve
EOF

# Make executable
chmod +x preview-docs.sh
```

**Now you can just run**:
```bash
./preview-docs.sh
```

**And it does everything automatically!**

---

## Understanding What Gets Tracked by Git

This is crucial to understand. Let's be very clear about what goes where.

### What IS Tracked by Git (Committed to Your Repo)

```
✅ TRACKED (committed to git):

jarvis-streamdeck/
├── jarvis/
│   ├── actions/
│   │   └── actions.py              ✓ Your Python code
│   ├── docs/
│   │   └── content/
│   │       ├── index.md             ✓ Generated markdown
│   │       ├── educational/*.md     ✓ Generated markdown
│   │       └── notes/*.md           ✓ Generated markdown
│   ├── utils/
│   │   ├── extract_comments.py     ✓ Your script
│   │   ├── generate_docs.py        ✓ Your script
│   │   └── strip_comments.py       ✓ Your script
│   └── git_docs/
│       └── *.md                     ✓ This documentation!
├── .github/
│   └── workflows/
│       └── deploy-docs.yml         ✓ YOUR GitHub Actions workflow
└── .gitignore                      ✓ Git ignore rules
```

**Why tracked?**
- These are YOUR files - your code, your docs, your scripts
- Other people cloning your repo need these files
- GitHub Actions needs your markdown files to deploy

---

### What is NOT Tracked by Git (In .gitignore)

```
❌ NOT TRACKED (in .gitignore):

jarvis-streamdeck/
├── quartz-preview/                 ✗ Entire Quartz installation
│   ├── quartz/                     ✗ Quartz code
│   ├── content/                    ✗ Copy of your docs
│   ├── node_modules/               ✗ Node.js packages (huge!)
│   ├── public/                     ✗ Built website (generated)
│   ├── .quartz-cache/              ✗ Quartz cache
│   └── quartz.config.ts            ✗ Quartz config
└── node_modules/                   ✗ Any Node packages
```

**Why NOT tracked?**
- **Quartz is a tool**, not part of your project (like not committing Microsoft Word)
- **Large size**: node_modules/ can be 100+ MB
- **Can be regenerated**: Anyone can download Quartz
- **GitHub Actions doesn't use it**: It downloads its own copy

---

### The .gitignore File Explained

Your `.gitignore` should contain:

```bash
# Python
__pycache__/
*.py[cod]
*.egg-info/

# Quartz Local Preview
# We use Quartz to preview docs locally, but don't commit it.
# GitHub Actions downloads it fresh for deployment.
quartz-preview/
quartz/

# Quartz build outputs
public/
.quartz-cache/

# Node.js
node_modules/
package-lock.json

# OS files
.DS_Store
Thumbs.db

# Project-specific
jarvis_prod/
config.env
*.log
```

**What this means**:
- Git will completely ignore `quartz-preview/`
- Even if it exists on your computer, git won't see it
- `git status` won't show it
- `git add .` won't add it
- It won't be pushed to GitHub

---

### Visual: What GitHub Sees vs. What's on Your Computer

```
┌──────────────────────────────────────────────────────────────┐
│              YOUR COMPUTER (Local Files)                     │
├──────────────────────────────────────────────────────────────┤
│  jarvis-streamdeck/                                          │
│  ├── jarvis/                    ← Tracked by git             │
│  ├── .github/                   ← Tracked by git             │
│  ├── quartz-preview/            ← NOT tracked (ignored)      │
│  ├── node_modules/              ← NOT tracked (ignored)      │
│  └── .gitignore                 ← Tracked by git             │
└──────────────────────────────────────────────────────────────┘
                          ↓ git push
┌──────────────────────────────────────────────────────────────┐
│              GITHUB (Remote Repository)                      │
├──────────────────────────────────────────────────────────────┤
│  jarvis-streamdeck/                                          │
│  ├── jarvis/                    ← Visible on GitHub          │
│  ├── .github/                   ← Visible on GitHub          │
│  └── .gitignore                 ← Visible on GitHub          │
│                                                              │
│  (quartz-preview/ doesn't exist here - it was ignored)       │
└──────────────────────────────────────────────────────────────┘
```

---

## How GitHub Actions Uses Quartz

Let's walk through **exactly** what happens on GitHub's computers when you push.

### Timeline of GitHub Actions Deployment

#### T+0 seconds: You Push to GitHub

```bash
# On your computer:
git push origin main
```

**What gets uploaded to GitHub**:
- Your Python code
- Your generated markdown files (`jarvis/docs/content/*.md`)
- Your workflow file (`.github/workflows/deploy-docs.yml`)
- NOT quartz-preview/ (it's ignored!)

---

#### T+5 seconds: GitHub Detects Push

GitHub sees:
1. New commits pushed to `main` branch
2. Files changed include `jarvis/docs/**`
3. Workflow file exists: `.github/workflows/deploy-docs.yml`
4. Workflow triggers say: "Run on push to main"

**GitHub Actions starts running!**

---

#### T+10 seconds: GitHub Creates Temporary Computer

GitHub spins up a **brand new, empty Ubuntu Linux virtual machine**.

Think of it like:
- A completely fresh computer
- Nothing installed except basic Linux
- Temporary (will be destroyed after deployment)
- Has internet connection

---

#### T+15 seconds: Step 1 - Checkout Your Repository

```yaml
- name: Checkout repository
  uses: actions/checkout@v4
```

**What happens**:
```bash
# GitHub runs (on its temporary computer):
git clone https://github.com/YOUR_USERNAME/jarvis-streamdeck.git
cd jarvis-streamdeck
```

**Now the computer has**:
```
/home/runner/work/jarvis-streamdeck/jarvis-streamdeck/
├── jarvis/
│   ├── actions/
│   ├── docs/
│   │   └── content/
│   │       └── *.md        ← Your markdown files!
│   └── utils/
└── .github/
```

**Note**: No `quartz-preview/` here! It was in .gitignore.

---

#### T+20 seconds: Step 2 - Install Node.js

```yaml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '18'
```

**What happens**:
- Downloads and installs Node.js version 18
- Installs npm (Node Package Manager)

**Now the computer can run**: `npm` and `node` commands

---

#### T+30 seconds: Step 3 - Install Quartz (Fresh Copy)

```yaml
- name: Install Quartz
  run: |
    git clone https://github.com/jackyzha0/quartz.git
    cd quartz
    npm install
```

**What happens**:
```bash
# Downloads Quartz from official repo
git clone https://github.com/jackyzha0/quartz.git

# Enters Quartz directory
cd quartz

# Installs all Quartz dependencies
npm install
# (Downloads 400+ packages, takes ~1 minute)
```

**Now the computer has**:
```
/home/runner/work/jarvis-streamdeck/jarvis-streamdeck/
├── jarvis/
│   └── docs/content/*.md
└── quartz/                    ← Fresh Quartz installation!
    ├── quartz/
    ├── node_modules/         ← All dependencies
    └── quartz.config.ts
```

**Key insight**: This is a **brand new** Quartz, not your local `quartz-preview/`!

---

#### T+90 seconds: Step 4 - Copy Your Docs to Quartz

```yaml
- name: Copy documentation to Quartz
  run: |
    mkdir -p quartz/content
    cp -r jarvis/docs/content/* quartz/content/
```

**What happens**:
```bash
# Copy YOUR markdown files into Quartz
cp jarvis/docs/content/index.md → quartz/content/index.md
cp jarvis/docs/content/educational/* → quartz/content/educational/
cp jarvis/docs/content/notes/* → quartz/content/notes/
# etc.
```

**Now Quartz has your content**:
```
quartz/
├── content/
│   ├── index.md              ← YOUR docs
│   ├── educational/          ← YOUR docs
│   └── notes/                ← YOUR docs
└── quartz/                   ← Quartz code
```

---

#### T+100 seconds: Step 5 - Configure Quartz

```yaml
- name: Configure Quartz
  run: |
    cd quartz
    cat > quartz.config.ts << 'EOF'
    import { QuartzConfig } from "./quartz/cfg"
    ...
    baseUrl: "YOUR_USERNAME.github.io/jarvis-streamdeck"
    ...
    EOF
```

**What happens**:
- Creates configuration file
- Sets your GitHub Pages URL as base
- Configures theme, colors, plugins

---

#### T+110 seconds: Step 6 - Build Static Website

```yaml
- name: Build Quartz site
  run: |
    cd quartz
    npx quartz build
```

**What happens**:
```bash
# Quartz processes all markdown files
# Generates complete static website
# Output goes to quartz/public/

Processing: index.md → public/index.html
Processing: educational/actions.md → public/educational/actions.html
Processing: notes/implementation.md → public/notes/implementation.html
# etc.

✓ Generating HTML files
✓ Adding navigation menus
✓ Creating search index
✓ Applying styling and theme
✓ Building graph visualization
✓ Generating sitemap
```

**Result**: `quartz/public/` now contains a complete website!

```
quartz/public/
├── index.html
├── educational/
│   └── actions.html
├── notes/
│   └── implementation.html
├── static/
│   ├── styles.css
│   └── scripts.js
└── search-index.json
```

---

#### T+150 seconds: Step 7 - Deploy to GitHub Pages

```yaml
- name: Deploy to GitHub Pages
  uses: actions/deploy-pages@v4
```

**What happens**:
- Takes everything in `quartz/public/`
- Uploads to GitHub Pages servers
- Makes it available at `https://YOUR_USERNAME.github.io/jarvis-streamdeck/`

---

#### T+180 seconds: Step 8 - Cleanup

**GitHub destroys the temporary computer**:
- Deletes Quartz installation
- Deletes all temporary files
- Frees up resources

**Everything is gone EXCEPT**:
- Your website on GitHub Pages (stays live!)

---

### What This Means for You

**You don't need to**:
- Commit Quartz to your repo
- Worry about Quartz versioning
- Install Node.js on your computer (for deployment)

**GitHub handles everything**:
- Downloads fresh Quartz each time
- Always uses latest version
- Builds in isolated environment
- No conflicts with your code

**Your local `quartz-preview/`**:
- Only for YOUR previewing
- Completely separate from GitHub
- Never uploaded or used by GitHub

---

## Troubleshooting

### Preview Server Won't Start

**Problem**: `npx quartz build --serve` fails

**Solution 1**: Check Node.js version
```bash
node --version
# Should be v18 or higher

# If too old:
# Ubuntu: sudo apt update && sudo apt install nodejs npm
# macOS: brew upgrade node
```

**Solution 2**: Reinstall dependencies
```bash
cd quartz-preview
rm -rf node_modules
npm install
```

**Solution 3**: Check port 8080 is free
```bash
# See what's using port 8080
lsof -i :8080

# If something is using it, kill it:
kill -9 <PID>

# Or use a different port:
npx quartz build --serve --port 3000
```

---

### No Content Shows Up

**Problem**: Preview loads but shows empty page

**Solution**: Verify content was copied
```bash
# Check if content exists
ls quartz-preview/content/

# Should show: index.md, educational/, notes/, etc.

# If empty, copy again:
cp -r jarvis/docs/content/* quartz-preview/content/
```

---

### Git Sees quartz-preview/

**Problem**: `git status` shows quartz-preview/

**Solution**: Add to .gitignore properly
```bash
# Check .gitignore exists at repo root
ls -la .gitignore

# Add Quartz to ignore
echo "quartz-preview/" >> .gitignore

# Remove from git cache
git rm -r --cached quartz-preview/

# Verify
git status
# Should NOT show quartz-preview/
```

---

### "Module not found" Errors

**Problem**: Quartz errors about missing modules

**Solution**: Install dependencies
```bash
cd quartz-preview

# Clean install
rm -rf node_modules package-lock.json
npm install

# Should see: "added 482 packages"
```

---

### Browser Doesn't Open Automatically

**Problem**: `npx quartz build --serve` runs but no browser opens

**Solution**: Open manually
```
1. Look for this in terminal output:
   "Started a Quartz server listening at http://localhost:8080"

2. Copy the URL: http://localhost:8080

3. Open in your browser manually
```

---

### Changes Don't Appear in Preview

**Problem**: You updated docs but preview still shows old content

**Solution**: Full refresh
```bash
# Stop the server (Ctrl+C)

# Regenerate docs
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/

# Clear Quartz content
rm -rf quartz-preview/content/*

# Copy fresh
cp -r jarvis/docs/content/* quartz-preview/content/

# Restart server
cd quartz-preview
npx quartz build --serve

# Hard refresh in browser: Ctrl+Shift+R (or Cmd+Shift+R on Mac)
```

---

## Advanced: Customizing Quartz

Want to customize how your docs look? Here's how.

### Customizing Theme Colors

Edit `quartz-preview/quartz.config.ts`:

```typescript
theme: {
  colors: {
    lightMode: {
      light: "#faf8f8",      // Background
      lightgray: "#e5e5e5",  // Borders
      gray: "#b8b8b8",       // Muted text
      darkgray: "#4e4e4e",   // Body text
      dark: "#2b2b2b",       // Headers
      secondary: "#284b63",  // Links (change this!)
      tertiary: "#84a59d",   // Hover states
      highlight: "rgba(143, 159, 169, 0.15)",
    },
  }
}
```

**To use your own colors**:
1. Edit the hex codes above
2. Save the file
3. Restart preview server
4. Refresh browser

---

### Adding Custom Pages

You can add custom pages that aren't auto-generated:

```bash
# Create custom page
cat > quartz-preview/content/about.md << 'EOF'
---
title: "About This Project"
---

# About This Project

This documentation is generated from code comments
using a custom pipeline.

## Features
- Automatic extraction from code
- Beautiful formatting with Quartz
- Deployed via GitHub Actions
EOF

# Restart server to see it
```

---

### Changing Site Title

Edit `quartz-preview/quartz.config.ts`:

```typescript
configuration: {
  pageTitle: "Jarvis StreamDeck Documentation",  // Change this
  // ...
}
```

---

### Enabling Additional Features

Quartz has many optional features. Enable them in `quartz.config.ts`:

```typescript
plugins: {
  transformers: [
    Plugin.FrontMatter(),
    Plugin.TableOfContents(),           // Table of contents
    Plugin.SyntaxHighlighting(),        // Code highlighting
    Plugin.ObsidianFlavoredMarkdown(),  // Obsidian compatibility
    Plugin.GitHubFlavoredMarkdown(),    // GitHub markdown
    Plugin.Latex({ renderEngine: "katex" }), // Math equations
  ],
}
```

---

## Reusable Setup Script

### Using the Script in Other Repos

The `setup-quartz-preview.sh` script is designed to be reusable across multiple repositories!

**To use it in another project**:

1. **Copy the script** to your new repo:
```bash
# From jarvis-streamdeck repo
cp setup-quartz-preview.sh /path/to/your/other/repo/

# Navigate to new repo
cd /path/to/your/other/repo/

# Make executable
chmod +x setup-quartz-preview.sh
```

2. **Copy Quartz** to the new repo:
```bash
cp -r /path/to/quartz ./quartz-preview
```

3. **Run the script**:
```bash
./setup-quartz-preview.sh
```

**The script will automatically**:
- Clean up Quartz files
- Update `.gitignore`
- Verify setup
- Show next steps

**Perfect for**:
- Multiple documentation projects
- Team members setting up locally
- Consistent setup across repos
- Quick Quartz preview setup

---

### Script Customization

You can modify the script to fit your needs:

```bash
# Edit the script
vim setup-quartz-preview.sh

# Customize:
# - Files to remove (FILES_TO_REMOVE array)
# - .gitignore patterns
# - Required files to check
# - Output messages
```

**Example customization** - Add more files to remove:
```bash
# In setup-quartz-preview.sh, modify:
FILES_TO_REMOVE=(
    ".git"
    ".github"
    ".gitignore"
    ".gitattributes"
    "CODE_OF_CONDUCT.md"
    "CONTRIBUTING.md"
    "LICENSE.txt"
    "README.md"
    "CHANGELOG.md"        # Add this
    "docs/"              # Add this
)
```

---

## Summary

Let's recap everything you've learned.

### The Big Picture

```
1. You write code with #EDU comments
2. Scripts extract comments → markdown
3. [OPTIONAL] Quartz preview locally
4. You push to GitHub
5. GitHub Actions downloads fresh Quartz
6. Builds your docs → deploys to Pages
7. Public website is live!
```

### Key Concepts

| Concept | Explanation |
|---------|-------------|
| **Quartz** | Static site generator for documentation |
| **Local Quartz** | Your preview copy (not in git) |
| **GitHub Quartz** | Fresh copy GitHub downloads for deployment |
| **Two separate instances** | Local and GitHub versions are independent |
| **.gitignore** | Keeps local Quartz out of version control |
| **npx quartz build** | Command to build static site |
| **--serve** | Runs local preview server |

### File Locations

```
Your Computer:
  jarvis-streamdeck/
  ├── jarvis/docs/content/*.md        (tracked by git)
  └── quartz-preview/                 (NOT tracked - .gitignore)

GitHub Repository:
  jarvis-streamdeck/
  ├── jarvis/docs/content/*.md        (visible on GitHub)
  └── .github/workflows/deploy-docs.yml (deployment config)

GitHub Actions (temporary):
  /runner/work/
  ├── jarvis-streamdeck/              (your repo)
  └── quartz/                         (downloaded fresh)

GitHub Pages (public):
  https://USERNAME.github.io/jarvis-streamdeck/
```

---

## Related Documentation

For more information, see:

- **[00_OVERVIEW.md](./00_OVERVIEW.md)** - System architecture overview
- **[02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md](./02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md)** - How documentation is generated
- **[03_SETUP_INSTRUCTIONS.md](./03_SETUP_INSTRUCTIONS.md)** - Complete setup guide (includes GitHub Pages setup)
- **[05_GITHUB_ACTIONS_SETUP.md](./05_GITHUB_ACTIONS_SETUP.md)** - GitHub Actions details
- **[07_TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md)** - Common issues
- **[08_TECHNICAL_REFERENCE.md](./08_TECHNICAL_REFERENCE.md)** - Script APIs

---

## Quick Reference

### Daily Commands

```bash
# Generate docs and preview
./preview-docs.sh

# Or manually:
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/
cp -r jarvis/docs/content/* quartz-preview/content/
cd quartz-preview && npx quartz build --serve
```

### Setup Commands (One-Time)

**Automated (Recommended)**:
```bash
# Copy Quartz and run setup script
cp -r /path/to/existing/quartz ./quartz-preview
./setup-quartz-preview.sh
cd quartz-preview && npm install
```

**Manual**:
```bash
# Copy Quartz
cp -r /path/to/existing/quartz ./quartz-preview
rm -rf quartz-preview/.git
cd quartz-preview
rm -rf .github .gitignore .gitattributes *.md
npm install

# Add to .gitignore
echo "quartz-preview/" >> .gitignore
```

### Troubleshooting Commands

```bash
# Reinstall dependencies
cd quartz-preview
rm -rf node_modules
npm install

# Check Node version
node --version  # Should be v18+

# Remove from git if needed
git rm -r --cached quartz-preview/
```

---

**You now understand exactly how Quartz works in this system!** 🎉

**Next steps**:
1. Set up local preview (if you haven't)
2. Generate your docs and preview them
3. When happy, push to GitHub
4. Watch GitHub Actions deploy automatically!
