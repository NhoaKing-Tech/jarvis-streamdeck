# Workflow 1: Squash Merge Dev into Main

**Difficulty**: Beginner-Friendly
**Time Required**: 15-20 minutes (first time)
**Prerequisites**: Basic git knowledge (commit, branch, push)

---

## Table of Contents

1. [What is a Squash Merge?](#what-is-a-squash-merge)
2. [Why Use Squash Merge?](#why-use-squash-merge)
3. [Before You Start](#before-you-start)
4. [Step-by-Step Instructions](#step-by-step-instructions)
5. [Understanding Each Step](#understanding-each-step)
6. [Common Mistakes to Avoid](#common-mistakes-to-avoid)
7. [Verification Checklist](#verification-checklist)

---

## What is a Squash Merge?

Imagine you've been working on a project and made 20 commits:
- "trying this approach"
- "oops, fixed typo"
- "experimenting with feature"
- "removed debug code"
- etc.

A **squash merge** takes ALL those commits and combines them into ONE single commit.

**Think of it like this**:
- Regular merge: "Here are all 20 steps I took to build this feature"
- Squash merge: "Here's the final feature, complete and polished"

---

## Why Use Squash Merge?

### Your Situation

You have a `dev` branch with messy commits that look like this:
```
* d436db3 Commit before git workflows implementation
* fbd1092 Polishing codebase and documentation
* e0a3efb Learn branch_manager.py and include comments
* 7151549 FIX jarvis_prod from being tracked
* a0afae7 Restructure documentation
* 33c9c63 FIRST COMMIT ON DEV WITH GIT HOOKS TO TEST IT
* ef9f901 feat: Complete annotation workflow system
* 273fb63 BEFORE DOCS
* af1a064 COMPLETE REFACTOR TO SEPARATE CONCERNS
... (and many more)
```

This is perfectly fine for your development work! But for GitHub (your portfolio), you want to show:
```
* abc1234 Initial release of Jarvis StreamDeck system
```

### Benefits

✅ **Clean History**: Employers see professional, well-organized commits
✅ **Hide Experiments**: Your trial-and-error stays private
✅ **Clear Intent**: One commit = one feature or milestone
✅ **Professional**: Industry standard for merging feature branches

---

## Before You Start

### 1. Check Your Current Branch
```bash
git branch
```

You should see:
```
* dev          ← You should be here
  main
```

If you're not on `dev`, switch to it:
```bash
git checkout dev
```

### 2. Make Sure Everything is Committed
```bash
git status
```

You should see:
```
On branch dev
nothing to commit, working tree clean
```

If you see uncommitted changes:
```bash
git add .
git commit -m "Save work before merge"
```

### 3. Verify Your Branches Exist
```bash
git branch -a
```

You should see both `dev` and `main`:
```
* dev
  main
  remotes/origin/dev
  remotes/origin/main
```

---

## Step-by-Step Instructions

### Step 1: Switch to Main Branch

**Command**:
```bash
git checkout main
```

**What you'll see**:
```
Switched to branch 'main'
```

**What this does**: You're now working on the `main` branch. Any changes here will affect what people see on GitHub.

---

### Step 2: Perform the Squash Merge

**Command**:
```bash
git merge --squash dev
```

**What you'll see**:
```
Squashing commit d436db3
Squashing commit fbd1092
Squashing commit e0a3efb
... (all your commits)
Automatic merge went well; stopped before committing as requested
```

**What this does**:
- Takes ALL changes from `dev` branch
- Combines them into one set of changes
- **Doesn't commit yet** - gives you a chance to write a good commit message

**Important**: At this point, the changes are **staged** but **not committed**.

---

### Step 3: Check What Will Be Committed

**Command**:
```bash
git status
```

**What you'll see**:
```
On branch main
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
        modified:   jarvis/actions/actions.py
        modified:   jarvis/core/application.py
        modified:   jarvis/core/lifecycle.py
        ... (all your modified files)
```

**What this means**: All changes from `dev` are ready to be committed as one commit.

---

### Step 4: Create the Single Commit

**Command**:
```bash
git commit -m "Initial release of Jarvis StreamDeck system

This commit represents the complete implementation of the Jarvis
personal assistant system using ElGato StreamDeck XL.

Features:
- Custom action system for system automation
- Dynamic layout management
- Extensive configuration system
- Integration with Linux system tools (ydotool, wmctrl)
- Modular architecture with clean separation of concerns

Built on top of python-elgato-streamdeck library with custom
enhancements for personal productivity workflows."
```

**What you'll see**:
```
[main abc1234] Initial release of Jarvis StreamDeck system
 23 files changed, 3421 insertions(+), 125 deletions(-)
```

**What this does**: Creates ONE beautiful commit with all your changes.

**Pro Tip**: You can customize this commit message to match your style!

---

### Step 5: Verify the Merge

**Command**:
```bash
git log --oneline -5
```

**What you'll see**:
```
abc1234 Initial release of Jarvis StreamDeck system
... (older commits from main branch if any)
```

**What to check**: You should see your new commit at the top!

---

### Step 6: Compare with Dev Branch

**Command**:
```bash
git log --oneline --graph --all -10
```

**What you'll see**:
```
* abc1234 (HEAD -> main) Initial release of Jarvis StreamDeck system
| * d436db3 (dev) Commit before git workflows implementation
| * fbd1092 Polishing codebase and documentation
| * e0a3efb Learn branch_manager.py and include comments
... (dev branch history preserved)
```

**What this shows**:
- `main` has 1 clean commit
- `dev` still has all your detailed history
- Both branches have the **same code**, different history!

---

### Step 7: Verify Files Are Identical

**Command**:
```bash
diff -r <(git show dev:jarvis) <(git show main:jarvis) --exclude=*.pyc
```

**What you'll see**:
```
(No output means files are identical)
```

**What this proves**: The code in `dev` and `main` is exactly the same, only the commit history differs.

---

### Step 8: Push to GitHub (When Ready)

**Command**:
```bash
git push origin main
```

**What you'll see**:
```
Enumerating objects: 45, done.
Counting objects: 100% (45/45), done.
Delta compression using up to 8 threads
Compressing objects: 100% (23/23), done.
Writing objects: 100% (24/24), 15.42 KiB | 5.14 MiB/s, done.
Total 24 (delta 18), reused 0 (delta 0), pack-reused 0
To github.com:yourusername/jarvis-streamdeck.git
   old1234..abc1234  main -> main
```

**What this does**: Publishes your clean `main` branch to GitHub!

**Note**: You typically do NOT push the `dev` branch to GitHub, keeping it local.

---

## Understanding Each Step

### Why Switch to Main First?

Think of git branches like parallel universes. To merge changes INTO `main`, you need to "be in" main first.

**Analogy**: You can't receive a package at your house if you're not home. Similarly, you can't merge into main unless you're "on" main.

---

### What Does --squash Do?

The `--squash` flag tells git: "Take all the changes from dev, but don't copy the commit history."

**Without --squash** (regular merge):
```
main: A -- B -- C -- D -- E -- F (all dev commits copied)
```

**With --squash**:
```
main: A -- X (one commit with all changes from B through F)
```

---

### Why Not Commit Automatically?

Git gives you a chance to:
1. Review what will be committed (`git status`)
2. Write a **good commit message** (very important!)
3. Back out if something looks wrong (`git reset`)

---

### Can I Undo This?

**Before pushing**: YES! Easy to undo.
```bash
git reset --hard HEAD~1  # Removes the squash commit
git checkout dev         # Go back to dev branch
```

**After pushing**: YES, but more complex. See [07_TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md).

---

## Common Mistakes to Avoid

### ❌ Mistake 1: Merging While on Dev Branch

**Wrong**:
```bash
git checkout dev
git merge --squash main  # WRONG DIRECTION!
```

**Why it's wrong**: This would merge `main` into `dev`, opposite of what you want.

**Correct**:
```bash
git checkout main        # Switch to DESTINATION
git merge --squash dev   # Merge FROM source
```

**Memory trick**: "I'm on main, I'm merging dev into me"

---

### ❌ Mistake 2: Forgetting to Commit

After `git merge --squash dev`, the changes are **staged but not committed**.

**Signs you forgot**:
- You switch branches and changes disappear
- `git status` shows "Changes to be committed"

**Solution**:
```bash
git commit -m "Your commit message"
```

---

### ❌ Mistake 3: Pushing Dev Branch to GitHub

**Why avoid**: Your `dev` branch is your messy workshop. Keep it local!

**If you accidentally pushed dev**:
```bash
git push origin --delete dev  # Remove from GitHub
```

---

### ❌ Mistake 4: Bad Commit Message

**Bad**:
```bash
git commit -m "stuff"
```

**Good**:
```bash
git commit -m "Initial release of Jarvis StreamDeck system

Complete implementation with action system, layouts, and configuration.
Built for personal productivity automation on Linux."
```

**Why it matters**: This commit message will be visible on GitHub. Make it professional!

---

## Verification Checklist

After completing the squash merge, verify:

- [ ] I am on the `main` branch (`git branch` shows `* main`)
- [ ] `git log` shows one clean commit on top
- [ ] `git status` shows "nothing to commit, working tree clean"
- [ ] My `dev` branch still exists with full history
- [ ] Files in `main` match files in `dev` (same code, different history)
- [ ] Commit message is clear and professional
- [ ] (Optional) I've pushed to GitHub and it looks good

---

## What's Next?

### Option A: Continue Working on Dev

After the squash merge, you can continue working on `dev`:

```bash
git checkout dev
# Make more changes
git add .
git commit -m "Add new feature"
```

When ready for the next release:
```bash
git checkout main
git merge --squash dev
git commit -m "Version 2.0 with new features"
```

### Option B: Set Up Documentation Pipeline

Now that you understand squash merge, learn how to automate documentation:

📖 **Next**: [02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md](./02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md)

---

## Real-World Analogy

Think of your project like writing a book:

- **Dev branch**: Your rough drafts, notes, deleted scenes, experiments
- **Main branch**: The published book that readers see
- **Squash merge**: Editing all your drafts into the final published version

Readers don't need to see every draft you wrote. They just want the polished final product!

---

## Questions?

**Q: Will I lose my dev branch history?**
A: No! Dev branch keeps all commits. Only main has the squashed commit.

**Q: Can I do multiple squash merges?**
A: Yes! Each time you squash merge, you create a new single commit.

**Q: What if I have merge conflicts?**
A: See [07_TROUBLESHOOTING.md](./07_TROUBLESHOOTING.md) section on "Handling Merge Conflicts"

**Q: Can I squash merge in the other direction?**
A: Technically yes, but don't! Always squash merge FROM dev TO main.

---

**Congratulations!** 🎉

You now understand squash merging! This is a professional workflow used by developers worldwide.

**Next Steps**:
- Try it yourself with a test repository first
- Read Workflow 2 to complete your documentation pipeline
- See how both workflows integrate in [04_INTEGRATION_GUIDE.md](./04_INTEGRATION_GUIDE.md)
