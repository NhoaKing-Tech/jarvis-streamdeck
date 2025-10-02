# Integration Guide: How Both Workflows Work Together

This guide explains how Workflow 1 (squash merge) and Workflow 2 (documentation pipeline) integrate seamlessly.

---

## The Complete Picture

```
LOCAL DEVELOPMENT (dev branch)
├── Write code with educational comments
├── Commit changes
│   └── Pre-commit hook extracts comments → generates markdown
├── Continue development with full history preserved
└── When ready for release...

MERGE TO PRODUCTION (main branch)
├── Squash merge dev → main
│   └── All commits condensed into one clean commit
├── Documentation included in merge
└── Clean code ready for GitHub

DEPLOY TO GITHUB
├── Push main branch
├── GitHub Actions triggered
│   └── Builds Quartz site from markdown docs
└── Deploys to GitHub Pages
```

---

## Day-to-Day Workflow

### Scenario 1: Adding a New Feature with Documentation

**Step 1: Work in Dev**
```bash
git checkout dev
```

**Step 2: Write Code with Comments**
```python
# jarvis/actions/new_feature.py

# EDU: Observer Pattern in Action
# EDU: ==========================
# EDU: This implements the Observer pattern for event handling.
# EDU: Benefits:
# EDU: 1. Loose coupling between components
# EDU: 2. Easy to add new observers
# EDU: 3. Runtime subscription management

def register_observer(observer):
    """Register a new observer for events."""
    observers.append(observer)
```

**Step 3: Commit (Docs Auto-Generated)**
```bash
git add jarvis/actions/new_feature.py
git commit -m "Add new feature with observer pattern"
```

**Pre-commit hook runs automatically**:
```
🔍 Running Jarvis pre-commit hooks on branch: dev
📝 Python files modified, generating documentation...
✅ Documentation generated successfully
   → Created: jarvis/docs/content/educational/new_feature.md
📁 Staged updated documentation files
✨ Pre-commit hooks completed successfully
```

**Result**: Your commit includes both code AND generated docs!

---

### Scenario 2: Multiple Commits Leading to a Release

**Dev Branch Work** (over several days):
```bash
# Day 1
git commit -m "Start new feature"

# Day 2
git commit -m "WIP: trying different approach"

# Day 3
git commit -m "Fixed bug in approach"

# Day 4
git commit -m "Add extensive educational comments"

# Day 5
git commit -m "Final polishing and cleanup"
```

Each commit:
- Preserves your full history in dev
- Auto-generates docs from comments
- Keeps your experimental work documented

**When Ready for Release**:
```bash
git checkout main
git merge --squash dev
git commit -m "Release v2.0: New feature with observer pattern

Implemented observer pattern for event handling system.
Includes comprehensive documentation of design patterns used.

🤖 Generated with Claude Code"

git push origin main
```

**Result**:
- Main has 1 clean commit (not 5 messy ones)
- All documentation is included
- Dev still has full history

---

## Branch Management Strategy

### What Lives Where

**Dev Branch** (local only):
- ✅ All commits (messy, experimental, everything)
- ✅ Code with ALL comments (#EDU, #NOTE, #TOCLEAN, etc.)
- ✅ Generated documentation
- ❌ Never pushed to GitHub (keep it private)

**Main Branch** (on GitHub):
- ✅ Clean, squashed commits
- ✅ Production-ready code
- ✅ Generated documentation
- ❌ No experimental commits
- ❌ No tagged comments (optional: can keep or strip)

---

## Tag Management

### Which Tags to Keep vs. Strip

**Development Tags** (keep in dev, optional in main):
- `#EDU` - Educational content → Becomes documentation
- `#NOTE` - Implementation notes → Useful for maintenance
- `#IMPORTANT` - Critical information → Keep in production

**Cleanup Tags** (keep in dev, strip from main):
- `#TOCLEAN` - Temporary notes → Remove before release
- `#FIXME` - Known issues → Should be fixed before main
- `#TODO` - Future work → Not for production
- `#HACK` - Workarounds → Fix before release
- `#DEBUG` - Debug code → Remove from production

**Current Configuration**:
The pre-commit hook on main will **warn** if it finds cleanup tags, but allows educational tags.

To strip ALL tags before merging, use:
```bash
python jarvis/utils/strip_comments.py jarvis/ --output jarvis_clean/ --recursive
# Then commit jarvis_clean/ instead of jarvis/
```

---

## Documentation Updates

### How Docs Stay in Sync

**Automatic Sync**:
```
Change code → Commit → Pre-commit hook runs → Docs updated → Both committed together
```

**Manual Regeneration** (if needed):
```bash
# Regenerate all docs
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/

# Commit updated docs
git add jarvis/docs/
git commit -m "Regenerate documentation"
```

---

## Common Workflows

### Workflow: Emergency Fix on Main

If you need to fix something directly on main:

```bash
# 1. Fix on main
git checkout main
# Make fix
git commit -m "Hotfix: Critical bug"

# 2. Merge back to dev to keep in sync
git checkout dev
git merge main
```

### Workflow: Rebase Dev on Main

If main has changes (e.g., from another contributor):

```bash
git checkout dev
git rebase main
```

### Workflow: Start Feature Branch

For larger features:

```bash
# Create feature branch from dev
git checkout dev
git checkout -b feature/new-thing

# Work on feature
git commit -m "WIP: new feature"

# When done, merge to dev
git checkout dev
git merge feature/new-thing

# Then squash merge dev to main as usual
```

---

## Best Practices

### DO ✅

1. **Commit frequently in dev** - Don't worry about messy history
2. **Use descriptive tags** - #EDU, #NOTE help organize documentation
3. **Test before merging to main** - Ensure everything works
4. **Write clear squash commit messages** - This is what GitHub shows
5. **Keep dev local** - Your messy history is your business

### DON'T ❌

1. **Don't commit directly to main** - Always squash merge from dev
2. **Don't skip pre-commit hook** - It keeps docs synchronized
3. **Don't push dev to public GitHub** - Keep your process private
4. **Don't forget to pull main into dev** - Stay in sync
5. **Don't delete dev branch** - It's your source of truth

---

## Troubleshooting Integration Issues

### Merge Conflicts

If you get conflicts during squash merge:

```bash
git checkout main
git merge --squash dev
# If conflicts occur:
git status  # See conflicting files
# Fix conflicts manually
git add <resolved-files>
git commit -m "Resolve conflicts and merge dev"
```

### Docs Out of Sync

If docs don't match code:

```bash
# Regenerate all documentation
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/

# Commit updated docs
git add jarvis/docs/
git commit -m "docs: Regenerate documentation"
```

### Hook Not Running

If pre-commit hook doesn't run:

```bash
# Ensure it's executable
chmod +x .git/hooks/pre-commit

# Test manually
.git/hooks/pre-commit
```

---

## Advanced: Custom Integration

### Adding Custom Tags

Edit `jarvis/utils/extract_comments.py`:

```python
SUPPORTED_TAGS = [
    'EDU',
    'NOTE',
    'CUSTOM',  # Add your tag
    # ...
]
```

Edit `jarvis/utils/generate_docs.py`:

```python
self.tag_categories = {
    'CUSTOM': {
        'title': 'Custom Documentation',
        'description': 'Your custom content',
        'dir': 'custom'
    },
    # ...
}
```

### Customizing Documentation Output

Modify `jarvis/utils/generate_docs.py` to change:
- Markdown formatting
- File organization
- Frontmatter metadata
- Navigation structure

---

## Summary

The integration works like this:

1. **Dev Branch**: Your workshop where you experiment freely
2. **Pre-commit Hook**: Automatically extracts docs when you commit
3. **Squash Merge**: Presents a clean version to the world
4. **GitHub Actions**: Publishes beautiful documentation

Everything is automated. You just write code and commit!

---

**Next**:
- [05_GITHUB_ACTIONS_SETUP.md](./05_GITHUB_ACTIONS_SETUP.md) - GitHub Actions details
- [07_TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md) - Common issues
