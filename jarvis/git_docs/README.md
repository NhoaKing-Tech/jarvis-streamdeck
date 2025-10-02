# Git Workflow Documentation

**Welcome!** This directory contains comprehensive documentation for implementing a professional git workflow with automated documentation generation.

---

## Quick Links

| Document | Description | For |
|----------|-------------|-----|
| **[00_OVERVIEW.md](./00_OVERVIEW.md)** | **START HERE** - System overview and architecture | Everyone |
| [01_WORKFLOW_1_SQUASH_MERGE.md](./01_WORKFLOW_1_SQUASH_MERGE.md) | Beginner-friendly guide to squash merging | Git beginners |
| [02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md](./02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md) | Documentation automation explained | Technical writers |
| [03_SETUP_INSTRUCTIONS.md](./03_SETUP_INSTRUCTIONS.md) | Step-by-step implementation guide | First-time setup |
| [04_INTEGRATION_GUIDE.md](./04_INTEGRATION_GUIDE.md) | How workflows work together | Understanding integration |
| [07_TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md) | Common issues and solutions | Problem solving |
| [08_TECHNICAL_REFERENCE.md](./08_TECHNICAL_REFERENCE.md) | API and script details | Developers |
| [09_QUARTZ_PREVIEW.md](./09_QUARTZ_PREVIEW.md) | Local Quartz setup and how it works | Preview setup |
| [10_GIT_HOOKS.md](./10_GIT_HOOKS.md) | Pre-commit & post-commit hooks explained | Automation |
| [11_TAG_USAGE_GUIDE.md](./11_TAG_USAGE_GUIDE.md) | **NEW!** Which tags to keep vs. strip | Tag usage |

---

## What This System Does

### Problem
You want to:
1. Show clean, professional code on GitHub for your portfolio
2. Keep detailed educational comments for your own learning
3. Auto-generate documentation from those comments
4. Deploy beautiful documentation to GitHub Pages

### Solution
This system provides:
- **Workflow 1**: Squash merge dev → main for clean git history
- **Workflow 2**: Automated documentation extraction from code comments
- **CI/CD**: GitHub Actions deploys docs automatically
- **Docs-as-Code**: Single-source documentation principles

---

## Getting Started

### 1. Read the Overview
Start with [00_OVERVIEW.md](./00_OVERVIEW.md) to understand the big picture.

### 2. Learn the Workflows
- [01_WORKFLOW_1_SQUASH_MERGE.md](./01_WORKFLOW_1_SQUASH_MERGE.md) - Clean git history
- [02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md](./02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md) - Auto-docs

### 3. Implement the System
Follow [03_SETUP_INSTRUCTIONS.md](./03_SETUP_INSTRUCTIONS.md) step-by-step.

### 4. Daily Usage
```bash
# Work in dev
git checkout dev

# Make changes, commit
git add .
git commit -m "Add feature"
# (Pre-commit hook auto-generates docs)

# When ready for release
git checkout main
git merge --squash dev
git commit -m "Release v1.0"
git push origin main
# (GitHub Actions auto-deploys docs)
```

---

## What You'll Build

### Local Repository Structure
```
jarvis-streamdeck/
├── jarvis/                    # Your code
│   ├── actions/
│   │   └── actions.py        # With #EDU comments in dev
│   ├── docs/
│   │   └── content/          # Auto-generated markdown
│   ├── utils/
│   │   ├── extract_comments.py
│   │   ├── strip_comments.py
│   │   └── generate_docs.py
│   └── git_docs/             # This documentation!
├── .git/hooks/
│   └── pre-commit            # Auto-runs on commit
└── .github/workflows/
    └── deploy-docs.yml       # Auto-deploys to Pages
```

### GitHub Repository
- **Main Branch**: Clean code + auto-generated docs
- **GitHub Pages**: Beautiful documentation site
- **Actions**: Automated deployment

---

## Key Features

### ✅ Clean Git History
One polished commit instead of dozens of "WIP", "fix typo", etc.

### ✅ Docs-as-Code
Documentation lives in code as comments, auto-extracted to markdown.

### ✅ Single-Sourcing
One source of truth (comments) → multiple outputs (docs, website).

### ✅ CI/CD Automation
- Pre-commit hook: Generates docs automatically
- GitHub Actions: Deploys to Pages automatically

### ✅ Portfolio-Ready
Demonstrates professional practices for technical writing roles.

---

## For Different Audiences

### Git Beginners
1. Read [01_WORKFLOW_1_SQUASH_MERGE.md](./01_WORKFLOW_1_SQUASH_MERGE.md)
2. Practice squash merge on a test repo first
3. Then implement full system

### Technical Writers
1. Read [02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md](./02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md)
2. Understand Docs-as-Code principles
3. See how it showcases your skills

### Developers
1. Check [08_TECHNICAL_REFERENCE.md](./08_TECHNICAL_REFERENCE.md)
2. Review Python script APIs
3. Customize for your needs

### Want to Preview Docs Locally?
1. Read [09_QUARTZ_PREVIEW.md](./09_QUARTZ_PREVIEW.md)
2. Set up local Quartz installation
3. Preview before pushing to GitHub

### Hiring Managers
1. Read [00_OVERVIEW.md](./00_OVERVIEW.md)
2. See the deployed documentation site
3. Note the professional workflow implementation

---

## Document Index

### Core Guides
| # | Document | Purpose |
|---|----------|---------|
| 00 | [OVERVIEW.md](./00_OVERVIEW.md) | System architecture and benefits |
| 01 | [WORKFLOW_1_SQUASH_MERGE.md](./01_WORKFLOW_1_SQUASH_MERGE.md) | Squash merge tutorial |
| 02 | [WORKFLOW_2_DOCUMENTATION_PIPELINE.md](./02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md) | Documentation automation |
| 03 | [SETUP_INSTRUCTIONS.md](./03_SETUP_INSTRUCTIONS.md) | Implementation guide |
| 04 | [INTEGRATION_GUIDE.md](./04_INTEGRATION_GUIDE.md) | How workflows integrate |

### Reference
| # | Document | Purpose |
|---|----------|---------|
| 07 | [TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md) | Common issues |
| 08 | [TECHNICAL_REFERENCE.md](./08_TECHNICAL_REFERENCE.md) | Script API docs |
| 09 | [QUARTZ_PREVIEW.md](./09_QUARTZ_PREVIEW.md) | Local preview setup |
| 10 | [GIT_HOOKS.md](./10_GIT_HOOKS.md) | Git hooks automation |
| 11 | [TAG_USAGE_GUIDE.md](./11_TAG_USAGE_GUIDE.md) | Tag usage best practices |

---

## Common Questions

### "Why two workflows?"
Workflow 1 (squash merge) creates clean git history. Workflow 2 (doc pipeline) creates beautiful documentation. Together, they create a professional repository perfect for portfolios.

### "Will I lose my commit history?"
No! Dev branch keeps all your commits. Only main has the squashed commits.

### "Can I use this without GitHub Pages?"
Yes! The documentation generation works locally. GitHub Pages deployment is optional.

### "Do I have to use both workflows?"
No. You can use squash merge without doc automation, or doc automation without squash merge. But they're designed to work together.

### "Is this industry standard?"
Squash merge: Yes, very common.
Docs-as-Code: Yes, best practice.
This exact combination: Customized for portfolio/learning.

---

## Success Stories

This workflow demonstrates:
- ✅ Git proficiency (branch management, merge strategies)
- ✅ Python programming (custom tooling)
- ✅ CI/CD implementation (hooks, GitHub Actions)
- ✅ Docs-as-Code expertise (single-sourcing, automation)
- ✅ Static site generation (Quartz, GitHub Pages)
- ✅ Technical writing (clear documentation)

Perfect for applications to:
- Technical Writer positions
- Developer Documentation roles
- DevOps positions
- Software Engineering roles

---

## Support

### Something Not Working?
Check [07_TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md)

### Want to Customize?
See [08_TECHNICAL_REFERENCE.md](./08_TECHNICAL_REFERENCE.md)

### Need Clarification?
Re-read the relevant guide - they're written for beginners!

---

## Implementation Checklist

Use this to track your progress:

- [ ] Read 00_OVERVIEW.md
- [ ] Understand Workflow 1 (squash merge)
- [ ] Understand Workflow 2 (doc pipeline)
- [ ] Install pre-commit hook
- [ ] Test documentation generation
- [ ] Configure GitHub repository
- [ ] Set up GitHub Actions
- [ ] Perform first squash merge
- [ ] Deploy to GitHub Pages
- [ ] Verify everything works

Estimated time: 1 hour for first-time setup

---

## Next Steps After Setup

Once your system is running:

1. **Add More Tags**: Customize tag categories in scripts
2. **Improve Comments**: Add more educational content to your code
3. **Customize Theme**: Modify Quartz configuration
4. **Share Your Work**: Use this in job applications!

---

## Credits

**Created by**: NhoaKing
**Project**: jarvis-streamdeck
**Purpose**: Portfolio demonstration for technical writing position
**Tools Used**:
- Git for version control
- Python for scripting
- Quartz for static site generation
- GitHub Actions for CI/CD
- GitHub Pages for hosting

---

## License

This documentation and associated scripts are part of the jarvis-streamdeck project.
Feel free to adapt this workflow for your own projects!

---

**🎉 Ready to get started?** → Open [00_OVERVIEW.md](./00_OVERVIEW.md)

**📚 Need to implement?** → Jump to [03_SETUP_INSTRUCTIONS.md](./03_SETUP_INSTRUCTIONS.md)

**🆘 Having issues?** → Check [07_TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md)
