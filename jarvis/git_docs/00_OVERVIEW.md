# Git Workflow System Overview

**Author**: NhoaKing
**Project**: jarvis-streamdeck
**Purpose**: Portfolio project demonstrating Docs-as-Code (DaC), CI/CD, technical writing skills, and abiliy to design professional git workflows. Shows also Python programming skills.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [The Two Workflows](#the-two-workflows)
4. [Key Principles](#key-principles)
5. [Quick Start](#quick-start)
6. [Document Index](#document-index)

---

## Introduction

This system implements a professional git workflow that achieves two main objectives:

1. **Clean Production Code**: Push only clean, production-ready code to GitHub (main branch)
2. **Automated Documentation**: Generate and deploy documentation from code comments automatically

The implementation showcases:
- **Docs-as-Code (DaC)** principles: Documentation lives in code as comments
- **Single-sourcing**: One source of truth (comments) generates multiple outputs
- **CI/CD**: Automated pipelines handle documentation generation and deployment
- **Git best practices**: Branch management, squash merges, and clean history

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         LOCAL REPOSITORY                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────┐              ┌─────────────────┐          │
│  │   dev branch   │              │  main branch    │          │
│  │                │              │                 │          │
│  │ • Full code    │  Squash      │ • Clean code   │          │
│  │ • All comments │  Merge       │ • No tags      │          │
│  │ • Tagged notes │  ──────────> │ • Production   │          │
│  │ • Messy history│              │ • Clean history│          │
│  └────────────────┘              └─────────────────┘          │
│         │                                  │                   │
│         │ Pre-commit Hook                  │                   │
│         ↓                                  ↓                   │
│  ┌─────────────────────┐          Push to GitHub              │
│  │ Extract Comments    │                  │                   │
│  │ Generate Markdown   │                  │                   │
│  └─────────────────────┘                  │                   │
│                                            │                   │
└────────────────────────────────────────────┼───────────────────┘
                                             │
                                             ↓
                    ┌─────────────────────────────────────┐
                    │         GITHUB REMOTE               │
                    ├─────────────────────────────────────┤
                    │  origin/main (clean production)     │
                    │         │                            │
                    │         ↓                            │
                    │  GitHub Actions Workflow             │
                    │         │                            │
                    │         ↓                            │
                    │  Deploy to GitHub Pages (Quartz)    │
                    └─────────────────────────────────────┘
```

---

## The Two Workflows

### Workflow 1: Squash Merge Dev into Main

**Problem**: Your dev branch has a messy commit history with experimental code and extensive comments.

**Solution**: Use squash merge to condense all dev commits into one clean commit on main.

**Result**:
- Main branch shows clean, professional code
- Dev branch preserves full history and comments
- GitHub displays only the polished version

📖 **See**: [01_WORKFLOW_1_SQUASH_MERGE.md](./01_WORKFLOW_1_SQUASH_MERGE.md)

---

### Workflow 2: Automated Documentation Pipeline

**Problem**: Code has extensive educational comments that would clutter production code but are valuable as documentation.

**Solution**: Extract comments with special tags (like `#EDU`, `#NOTE`, `#TOCLEAN`) and convert them to markdown documentation.

**Result**:
- Production code is clean and concise
- Educational content becomes beautiful documentation
- Documentation auto-updates when code changes
- Deployed to GitHub Pages via Quartz

📖 **See**: [02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md](./02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md)

---

## Key Principles

### 1. Docs-as-Code (DaC)
Documentation lives alongside code as comments. This ensures:
- Documentation stays synchronized with code
- Easy for developers to update
- Version controlled with code

### 2. Single-Sourcing
One source (code comments) generates multiple outputs:
- Markdown files for documentation
- GitHub Pages site via Quartz
- Future: PDF, searchable docs, etc.

### 3. CI/CD Integration
Automation at every step:
- **Git Hooks**: Pre-commit triggers documentation extraction
- **GitHub Actions**: Auto-deploy to GitHub Pages on push
- **No manual steps**: Write code, commit, done!

### 4. Branch Strategy
- **dev**: Development work with all comments and messy history
- **main**: Clean production code with single squashed commit
- **No duplication**: Same codebase, different views

---

## Quick Start

### First Time Setup
```bash
# 1. Read Workflow 1 to understand squash merge
cat jarvis/git_docs/01_WORKFLOW_1_SQUASH_MERGE.md

# 2. Read Workflow 2 to understand documentation pipeline
cat jarvis/git_docs/02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md

# 3. Set up the system (scripts, hooks, GitHub Actions)
cat jarvis/git_docs/03_SETUP_INSTRUCTIONS.md
```

### Daily Workflow
```bash
# Work in dev branch
git checkout dev

# Make changes, test, commit normally
git add .
git commit -m "Add new feature"

# Pre-commit hook automatically generates docs
# When ready to publish:
# 1. Merge to main (see Workflow 1 guide)
# 2. Push to GitHub
# 3. GitHub Actions deploys docs automatically
```

---

## Document Index

| Document | Purpose | Audience |
|----------|---------|----------|
| [00_OVERVIEW.md](./00_OVERVIEW.md) | This file - system overview | Everyone |
| [01_WORKFLOW_1_SQUASH_MERGE.md](./01_WORKFLOW_1_SQUASH_MERGE.md) | Step-by-step squash merge guide | Beginners |
| [02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md](./02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md) | Documentation automation explained | Technical writers |
| [03_SETUP_INSTRUCTIONS.md](./03_SETUP_INSTRUCTIONS.md) | Complete setup guide | First-time users |
| [04_INTEGRATION_GUIDE.md](./04_INTEGRATION_GUIDE.md) | How both workflows work together | Advanced users |
| [05_GITHUB_ACTIONS_SETUP.md](./05_GITHUB_ACTIONS_SETUP.md) | GitHub Actions configuration | DevOps |
| [06_QUARTZ_DEPLOYMENT.md](./06_QUARTZ_DEPLOYMENT.md) | Quartz static site deployment | Docs team |
| [07_TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md) | Common issues and solutions | Everyone |
| [08_TECHNICAL_REFERENCE.md](./08_TECHNICAL_REFERENCE.md) | Script details and API | Developers |

---

## Benefits for Portfolio

This system demonstrates:

✅ **Technical Writing Skills**: Clear, structured documentation for complex technical systems
✅ **Docs-as-Code Expertise**: Single-sourcing, automation, version control
✅ **CI/CD Knowledge**: Git hooks, GitHub Actions, automated pipelines
✅ **Git Proficiency**: Branch management, squash merges, workflow design
✅ **Python Programming**: Custom tooling for documentation extraction
✅ **Static Site Generation**: Quartz integration, GitHub Pages deployment

Perfect for a Technical Writer position at Google! 🎯

---

## Next Steps

1. **Read Workflow 1**: Understand squash merge process → [01_WORKFLOW_1_SQUASH_MERGE.md](./01_WORKFLOW_1_SQUASH_MERGE.md)
2. **Read Workflow 2**: Understand documentation pipeline → [02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md](./02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md)
3. **Follow Setup**: Implement the system → [03_SETUP_INSTRUCTIONS.md](./03_SETUP_INSTRUCTIONS.md)

---

**Questions?** See [07_TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md)
