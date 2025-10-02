# Workflow 2: Automated Documentation Pipeline

**Difficulty**: Intermediate
**Time Required**: 30-45 minutes (initial setup)
**Prerequisites**: Understanding of Workflow 1, basic Python knowledge

---

## Table of Contents

1. [The Problem We're Solving](#the-problem-were-solving)
2. [The Solution: Documentation Pipeline](#the-solution-documentation-pipeline)
3. [Architecture Overview](#architecture-overview)
4. [Key Concepts](#key-concepts)
5. [Component Details](#component-details)
6. [How It Works End-to-End](#how-it-works-end-to-end)
7. [Tag System Explained](#tag-system-explained)
8. [Benefits for Portfolio](#benefits-for-portfolio)

---

## The Problem We're Solving

### Your Situation

Your codebase has **extensive educational comments** like this:

```python
# EDU: COMPUTER SCIENCE EDUCATION: DESIGN PATTERNS COMPARISON
# EDU: =====================================================
# EDU: Our pattern stores configuration in module-level global variables
# EDU: This approach provides:
# EDU: 1. TESTABILITY: Easy to mock configuration
# EDU: 2. FLEXIBILITY: Can be configured for different environments
# EDU: 3. PERFORMANCE: Configuration accessed directly
```

These comments are **valuable** but:
- ❌ Make production code look cluttered
- ❌ Can confuse readers looking for just the implementation
- ❌ Aren't easily searchable or navigable
- ❌ Could be formatted better as documentation

### What You Want

1. **Clean production code** on GitHub (no educational comments)
2. **Beautiful documentation** generated from those comments
3. **Keep the commented version** locally for your learning
4. **Automatic updates** when code changes

---

## The Solution: Documentation Pipeline

### High-Level Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    LOCAL DEV BRANCH                          │
│  Python files with extensive comments (#EDU, #NOTE, etc.)   │
└────────────┬─────────────────────────────────────────────────┘
             │
             │ git commit (triggers pre-commit hook)
             ↓
┌──────────────────────────────────────────────────────────────┐
│               PRE-COMMIT HOOK ACTIONS                        │
│  1. Extract tagged comments → Generate markdown files       │
│  2. Create clean version of code (strip tags)               │
│  3. Stage documentation files                               │
└────────────┬─────────────────────────────────────────────────┘
             │
             │ Commit completes
             ↓
┌──────────────────────────────────────────────────────────────┐
│                 RESULT IN DEV BRANCH                         │
│  • Original code with comments preserved                     │
│  • Generated markdown docs in docs/ directory               │
└────────────┬─────────────────────────────────────────────────┘
             │
             │ Squash merge to main (Workflow 1)
             ↓
┌──────────────────────────────────────────────────────────────┐
│                    MAIN BRANCH                               │
│  • Clean code (comments stripped during merge)              │
│  • Generated documentation included                          │
└────────────┬─────────────────────────────────────────────────┘
             │
             │ git push origin main
             ↓
┌──────────────────────────────────────────────────────────────┐
│                  GITHUB ACTIONS                              │
│  Triggered on push to main                                   │
│  1. Build Quartz static site from markdown                  │
│  2. Deploy to GitHub Pages                                   │
└────────────┬─────────────────────────────────────────────────┘
             │
             ↓
┌──────────────────────────────────────────────────────────────┐
│              GITHUB PAGES (PUBLIC DOCS)                      │
│  Beautiful searchable documentation at:                      │
│  https://yourusername.github.io/jarvis-streamdeck           │
└──────────────────────────────────────────────────────────────┘
```

---

## Architecture Overview

### The Three-Branch Strategy

We'll use a **modified approach** that keeps your commented code safe:

```
┌─────────────────────────────────────────────────────────────┐
│  LOCAL BRANCHES                                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  dev (local only - NEVER pushed)                           │
│  • Full code with ALL comments                             │
│  • Tagged educational content (#EDU, #NOTE, etc.)          │
│  • Messy commit history                                     │
│  • This is your "source of truth"                          │
│                                                             │
│  ↓ (pre-commit hook extracts docs)                         │
│                                                             │
│  dev-clean (intermediate - auto-generated)                 │
│  • Same code, comments stripped                            │
│  • Documentation extracted to markdown                     │
│  • Ready for squash merge                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  GITHUB BRANCHES (pushed to remote)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  main                                                       │
│  • Clean production code                                    │
│  • Generated documentation files                           │
│  • Clean commit history                                     │
│  • Public-facing                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Key Insight**: You'll have TWO local versions:
1. `dev` - Your commented version (never leaves your computer)
2. `dev-clean` - Auto-generated clean version (for merging to main)

---

## Key Concepts

### 1. Docs-as-Code (DaC)

**Definition**: Documentation lives in the code as comments, not separate documents.

**Why it's better**:
- ✅ Developers actually update it (it's right there!)
- ✅ Version controlled alongside code
- ✅ Can't get out of sync with implementation
- ✅ Easy to review in pull requests

**Example**:
```python
# EDU: What is dependency injection?
# EDU: It's a design pattern where dependencies are provided (injected)
# EDU: from external sources rather than created internally.

def action_handler(config):  # config is injected!
    pass
```

---

### 2. Single-Sourcing

**Definition**: One source of truth generates multiple outputs.

**In your case**:
- **Single Source**: Code comments with tags
- **Multiple Outputs**:
  - Markdown documentation
  - GitHub Pages website
  - (Future: PDF guides, API docs, etc.)

**Benefits**:
- Update once, publish everywhere
- No manual copy-paste
- Consistency guaranteed

---

### 3. CI/CD for Documentation

**Traditional approach**:
```
1. Write code
2. Manually write docs
3. Manually build static site
4. Manually deploy
```

**Your automated approach**:
```
1. Write code with comments
2. Commit → Docs auto-generated
3. Push → Site auto-built
4. → Deployed automatically
```

---

## Component Details

### Component 1: Comment Extraction Script

**Location**: `jarvis/utils/extract_comments.py`

**Purpose**: Parse Python files and extract tagged comments

**What it does**:
```python
# Input: Python file with tagged comments
# EDU: This is an educational comment
# NOTE: This is a note
# TOCLEAN: This needs cleanup

# Output: Structured data
{
    "file": "actions.py",
    "tags": {
        "EDU": ["This is an educational comment"],
        "NOTE": ["This is a note"],
        "TOCLEAN": ["This needs cleanup"]
    }
}
```

**Key features**:
- Detects multi-line tagged comments
- Preserves formatting and structure
- Handles code blocks within comments
- Supports multiple tag types

---

### Component 2: Markdown Generator

**Location**: `jarvis/utils/generate_docs.py`

**Purpose**: Convert extracted comments to beautiful markdown

**What it does**:
```python
# Input: Structured comment data
{
    "EDU": ["Dependency injection is...", "It provides..."]
}

# Output: Markdown file
# Educational Notes

## Dependency Injection

Dependency injection is...

It provides...
```

**Key features**:
- Groups comments by tag type
- Creates table of contents
- Adds cross-references
- Formats code blocks correctly
- Generates navigation links

---

### Component 3: Code Cleaner

**Location**: `jarvis/utils/strip_comments.py`

**Purpose**: Create clean version of code without tagged comments

**What it does**:
```python
# Input: Code with tagged comments
def foo():
    # EDU: This is educational
    # NOTE: Implementation detail
    return bar()

# Output: Clean code
def foo():
    return bar()
```

**Important**: Only removes **tagged** comments. Regular comments stay!

---

### Component 4: Pre-commit Hook

**Location**: `.git/hooks/pre-commit`

**Purpose**: Automatically run extraction before each commit

**What it does**:
```bash
1. Detect which files changed
2. If Python files in jarvis/ changed:
   a. Run extract_comments.py
   b. Run generate_docs.py
   c. Stage generated markdown files
3. Commit completes with docs included
```

---

### Component 5: GitHub Actions Workflow

**Location**: `.github/workflows/deploy-docs.yml`

**Purpose**: Deploy documentation to GitHub Pages automatically

**What it does**:
```yaml
1. Triggered on push to main
2. Check out repository
3. Install Quartz
4. Build static site from markdown
5. Deploy to GitHub Pages
```

---

## How It Works End-to-End

### Scenario: You Add Educational Comments

**Step 1**: You write code with comments in `dev` branch
```python
# jarvis/actions/actions.py (in dev branch)

# EDU: Command Pattern Implementation
# EDU: ===================================
# EDU: Each action is encapsulated as a function, following the
# EDU: Command pattern. This allows us to:
# EDU: - Store actions in dictionaries
# EDU: - Execute them dynamically
# EDU: - Add new actions without modifying existing code

def open_browser():
    """Open the default web browser."""
    # Implementation...
```

---

**Step 2**: You commit your changes
```bash
git add jarvis/actions/actions.py
git commit -m "Add browser action with educational comments"
```

---

**Step 3**: Pre-commit hook runs automatically

**You'll see output like**:
```
🔍 Running Jarvis pre-commit hooks on branch: dev
📝 Python files in jarvis/ modified, extracting documentation...
   ✓ Extracted 45 tagged comments from actions.py
   ✓ Generated docs/educational/command-pattern.md
   ✓ Generated docs/notes/implementation-details.md
📁 Staged updated documentation files
✨ Pre-commit hooks completed successfully
```

**What happened**:
1. Hook detected `actions.py` changed
2. Ran `extract_comments.py` → found 45 comments with tags
3. Ran `generate_docs.py` → created markdown files
4. Staged markdown files → they're included in your commit

---

**Step 4**: Your commit now includes docs
```bash
git log -1 --stat

commit abc1234
Author: You
Date: Today

    Add browser action with educational comments

 jarvis/actions/actions.py              | 20 ++++++++++++++++
 jarvis/docs/educational/command-pattern.md | 35 ++++++++++++++++++++++++
 jarvis/docs/notes/implementation-details.md | 15 +++++++++++
```

---

**Step 5**: When ready, merge to main (Workflow 1)

```bash
# Switch to main
git checkout main

# Squash merge dev into main
git merge --squash dev

# During merge, comments are stripped automatically
# (using custom merge strategy - see Setup Guide)

# Commit the clean version
git commit -m "Add browser action functionality"
```

**Result**:
- `main` has clean code (no #EDU comments)
- `main` has generated markdown docs
- `dev` still has all your comments

---

**Step 6**: Push to GitHub
```bash
git push origin main
```

---

**Step 7**: GitHub Actions deploys automatically

**GitHub Actions runs**:
```
✓ Checkout repository
✓ Setup Node.js
✓ Install Quartz
✓ Build static site
✓ Deploy to GitHub Pages
→ Site live at https://yourusername.github.io/jarvis-streamdeck
```

---

**Step 8**: Your docs are live!

Anyone can now visit your documentation site and read beautifully formatted guides generated from your code comments.

---

## Tag System Explained

### Recommended Tags

| Tag | Purpose | Example Use |
|-----|---------|-------------|
| `#EDU` | Educational content, CS concepts | Design patterns, algorithms, best practices |
| `#NOTE` | Implementation notes, gotchas | "NOTE: This assumes only one device connected" |
| `#TOCLEAN` | Temporary notes to clean up | "TOCLEAN: Refactor this later" |
| `#FIXME` | Known issues to fix | "FIXME: Handle edge case when X is None" |
| `#TODO` | Future improvements | "TODO: Add error handling" |
| `#HACK` | Workarounds | "HACK: Temporary fix for library bug" |
| `#DEBUG` | Debugging aids | "DEBUG: Print state for troubleshooting" |
| `#IMPORTANT` | Critical information | "IMPORTANT: Must run as root" |
| `#REVIEW` | Needs review | "REVIEW: Is this the best approach?" |
| `#OPTIMIZE` | Performance notes | "OPTIMIZE: This could be faster with caching" |

### Tag Usage Examples

**Educational Content** (will become docs):
```python
# EDU: Factory Pattern
# EDU: ===============
# EDU: We use a factory function to create different types of actions
# EDU: based on runtime configuration. This provides:
# EDU:
# EDU: 1. Flexibility - Easy to add new action types
# EDU: 2. Testability - Mock factories in unit tests
# EDU: 3. Separation of Concerns - Creation logic isolated

def create_action(action_type, config):
    if action_type == "browser":
        return BrowserAction(config)
    # ...
```

**Implementation Notes** (will be stripped):
```python
# NOTE: This function must be called before deck.open()
# NOTE: Otherwise the device won't be initialized properly
def initialize_deck(deck):
    # ...
```

**Temporary Notes** (will be stripped):
```python
# TOCLEAN: This whole section needs refactoring
# TOCLEAN: Consider using a state machine instead
def messy_function():
    # ...
```

### Multi-Line Tagged Comments

Tags work for multi-line comments:
```python
# EDU: Callback Pattern Explanation
# EDU: ==============================
# EDU: StreamDeck uses callbacks for button press events.
# EDU: When you press a button:
# EDU:   1. Hardware detects press
# EDU:   2. Library calls our callback
# EDU:   3. We dispatch to the appropriate action
# EDU:
# EDU: This is an example of the Observer pattern.
```

### Mixing Tags and Regular Comments

```python
# This is a regular comment - stays in production code

# EDU: This is educational - will be extracted to docs

def my_function():
    # Regular comment - stays
    x = 5

    # NOTE: Edge case handling - will be stripped
    if x < 0:
        return None

    return x * 2
```

**Result in production**:
```python
# This is a regular comment - stays in production code

def my_function():
    # Regular comment - stays
    x = 5

    if x < 0:
        return None

    return x * 2
```

---

## Benefits for Portfolio

This workflow demonstrates key technical writing skills:

### 1. Docs-as-Code Expertise ✅

- Documentation lives in code
- Single source of truth
- Version controlled
- Developer-friendly

**Shows**: You understand modern documentation practices

---

### 2. CI/CD Knowledge ✅

- Git hooks for automation
- GitHub Actions for deployment
- Automated build pipeline
- Continuous documentation delivery

**Shows**: You can implement automated workflows

---

### 3. Python Programming ✅

- Custom tooling development
- File parsing and processing
- Markdown generation
- Integration scripting

**Shows**: You can code solutions, not just document them

---

### 4. Static Site Generation ✅

- Quartz integration
- GitHub Pages deployment
- Modern documentation hosting
- Professional presentation

**Shows**: You understand documentation platforms

---

### 5. Git Proficiency ✅

- Branch strategies
- Merge workflows
- Hook development
- Repository management

**Shows**: You can work in professional dev environments

---

## What's Next?

Now that you understand the **what** and **why**, let's implement it!

📖 **Next Steps**:
1. [03_SETUP_INSTRUCTIONS.md](./03_SETUP_INSTRUCTIONS.md) - Complete setup guide
2. [04_INTEGRATION_GUIDE.md](./04_INTEGRATION_GUIDE.md) - How workflows work together
3. [08_TECHNICAL_REFERENCE.md](./08_TECHNICAL_REFERENCE.md) - Script API details

---

## Quick Reference

### Daily Workflow
```bash
# Work in dev (with comments)
git checkout dev

# Edit code, add educational comments
# Commit (docs auto-generated)
git commit -m "Add feature"

# When ready for release
git checkout main
git merge --squash dev
git commit -m "Release v1.0"
git push origin main

# GitHub Actions deploys docs automatically
```

### File Structure After Setup
```
jarvis-streamdeck/
├── jarvis/
│   ├── actions/
│   │   └── actions.py          # Your code (with #EDU comments in dev)
│   ├── docs/
│   │   └── content/
│   │       ├── educational/    # Generated from #EDU
│   │       ├── notes/          # Generated from #NOTE
│   │       └── index.md        # Auto-generated index
│   ├── utils/
│   │   ├── extract_comments.py # Comment extraction
│   │   ├── generate_docs.py    # Markdown generation
│   │   └── strip_comments.py   # Code cleaning
│   └── git_docs/               # This documentation!
├── .git/hooks/
│   └── pre-commit              # Auto-run extraction
└── .github/workflows/
    └── deploy-docs.yml         # GitHub Actions config
```

---

**Ready to implement?** → [03_SETUP_INSTRUCTIONS.md](./03_SETUP_INSTRUCTIONS.md)
