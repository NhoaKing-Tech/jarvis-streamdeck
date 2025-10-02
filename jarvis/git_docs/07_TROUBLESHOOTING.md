# Troubleshooting Guide

Common issues and solutions for the git workflow and documentation pipeline.

---

## Git Hook Issues

### Hook Doesn't Execute

**Symptom**: Commit completes without running hook
**Cause**: Hook not executable or wrong location

**Solution**:
```bash
# Make hook executable
chmod +x .git/hooks/pre-commit

# Verify location
ls -la .git/hooks/pre-commit
# Should show: -rwxr-xr-x (note the x's)

# Test hook manually
.git/hooks/pre-commit
```

### Hook Fails with "Python not found"

**Symptom**: Error message "Python not found"
**Cause**: Python not in PATH

**Solution**:
```bash
# Check Python installation
which python python3

# If using conda, activate environment first
conda activate jarvis-busybee

# Or edit hook to use specific Python path
# In .git/hooks/pre-commit, change:
PYTHON_CMD="/full/path/to/python"
```

### Hook Blocks Commit

**Symptom**: Commit is rejected by hook
**Cause**: Hook detected an issue (tagged comments on main, etc.)

**Solutions**:

**Option 1**: Fix the issue (recommended)
```bash
# Follow the instructions in the hook error message
```

**Option 2**: Skip the hook (NOT recommended)
```bash
git commit --no-verify -m "Message"
```

---

## Documentation Generation Issues

### No Documentation Generated

**Symptom**: Hook runs but no .md files created
**Cause**: No tagged comments found, or script error

**Solution**:
```bash
# Test manually to see errors
python jarvis/utils/extract_comments.py jarvis/ --recursive

# If no comments found, verify files have tags:
grep -r "#EDU" jarvis/*.py

# Test doc generation
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/
```

### Import Error in Scripts

**Symptom**: `ModuleNotFoundError: No module named 'extract_comments'`
**Cause**: Scripts not in Python path

**Solution**:
```bash
# Run from repository root
cd /path/to/jarvis-streamdeck

# Or use absolute imports
cd jarvis/utils
python generate_docs.py ../  --output ../docs/content/
```

### Documentation Not Staged

**Symptom**: Docs generated but not in commit
**Cause**: Git doesn't see the files

**Solution**:
```bash
# Manually add docs
git add jarvis/docs/content/

# Or modify hook to be more verbose
# Check hook output for errors
```

---

## Squash Merge Issues

### Merge Conflicts

**Symptom**: `git merge --squash dev` shows conflicts
**Cause**: Main and dev have diverged

**Solution**:
```bash
# See what's conflicting
git status

# Option 1: Accept all changes from dev
git checkout --theirs <file>
git add <file>

# Option 2: Manually resolve
# Edit files, remove conflict markers
git add <resolved-file>

# Continue with commit
git commit -m "Merge dev with conflict resolution"
```

### Lost Commits After Merge

**Symptom**: Commits seem to have disappeared
**Cause**: This is normal for squash merge! Dev still has them.

**Solution**:
```bash
# Verify dev still has commits
git checkout dev
git log --oneline

# Main should have fewer commits (expected)
git checkout main
git log --oneline

# Both should have same final code
git diff dev --stat  # Should show no differences
```

### Accidentally Merged Wrong Direction

**Symptom**: Merged main into dev instead of dev into main
**Cause**: Wrong branch selected

**Solution**:
```bash
# Undo the merge (if not pushed)
git checkout dev
git reset --hard HEAD~1  # Remove merge commit

# Start over correctly
git checkout main  # Switch to destination
git merge --squash dev  # Merge from source
```

---

## GitHub Issues

### Push Rejected

**Symptom**: `git push origin main` fails
**Cause**: Remote has changes you don't have

**Solution**:
```bash
# Pull changes first
git pull origin main

# If conflicts, resolve them
# Then push
git push origin main
```

### Actions Workflow Not Running

**Symptom**: No workflow run after push
**Cause**: Workflow disabled or misconfigured

**Solutions**:

1. **Check Actions are enabled**:
   - Go to Settings → Actions → General
   - Ensure "Allow all actions" is selected

2. **Check workflow file**:
```bash
# Verify file exists
ls .github/workflows/deploy-docs.yml

# Check for syntax errors
# View on GitHub → Actions → Should show workflow
```

3. **Check file paths**:
   - Workflow triggers on changes to `jarvis/docs/**`
   - If docs are elsewhere, update workflow

### GitHub Pages Not Deploying

**Symptom**: Workflow succeeds but site doesn't update
**Cause**: Pages not configured correctly

**Solution**:
1. Go to Settings → Pages
2. Source: "GitHub Actions" (not "Deploy from branch")
3. Wait 3-5 minutes after workflow completes
4. Check workflow logs for deployment URL

### Permission Denied on Deploy

**Symptom**: Workflow fails with "403 Forbidden"
**Cause**: Workflow doesn't have write permissions

**Solution**:
1. Settings → Actions → General
2. "Workflow permissions"
3. Select "Read and write permissions"
4. Enable "Allow GitHub Actions to create and approve pull requests"
5. Save

---

## Documentation Site Issues

### 404 Not Found on GitHub Pages

**Symptom**: Site shows 404 error
**Causes and Solutions**:

**Cause 1**: Site not yet deployed
```
Wait 3-5 minutes after first push
```

**Cause 2**: Wrong URL
```
Correct URL format:
https://USERNAME.github.io/REPO-NAME/

NOT:
https://github.com/USERNAME/REPO-NAME/
```

**Cause 3**: Base URL wrong in Quartz config
```yaml
# In .github/workflows/deploy-docs.yml, verify:
baseUrl: "USERNAME.github.io/REPO-NAME"
```

### Broken Links in Documentation

**Symptom**: Links return 404
**Cause**: Relative path issues

**Solution**:
```markdown
# Use relative paths
[Link](./other-doc.md)

# NOT absolute paths
[Link](/jarvis/docs/other-doc.md)
```

### Styling Looks Wrong

**Symptom**: Site loads but looks unstyled
**Cause**: Quartz assets not loading

**Solution**:
Check workflow:
```yaml
# Ensure this step exists in deploy-docs.yml
- name: Install Quartz
  run: |
    git clone https://github.com/jackyzha0/quartz.git
    cd quartz
    npm install
```

---

## Python Script Issues

### extract_comments.py Errors

**Error**: `SyntaxError` when processing file
**Solution**:
```python
# File has syntax errors
# Fix the Python file first
python -m py_compile jarvis/problematic_file.py
```

**Error**: `FileNotFoundError`
**Solution**:
```bash
# Run from repository root
cd /path/to/jarvis-streamdeck
python jarvis/utils/extract_comments.py jarvis/
```

### strip_comments.py Issues

**Error**: Removes too many comments
**Solution**:
```python
# Specify exact tags to strip
python jarvis/utils/strip_comments.py file.py \
  --strip-tags EDU TOCLEAN FIXME
```

**Error**: Doesn't remove tagged comments
**Cause**: Regex doesn't match format

**Solution**:
Ensure comments match pattern:
```python
# Correct formats:
# EDU: Comment
#EDU: Comment
# EDU Comment
# EDU:Comment

# Won't match:
##EDU: (double ##)
# EDU - Comment (dash instead of colon)
```

---

## Conda/Environment Issues

### Environment Not Activating

**Symptom**: Hook can't activate conda environment
**Cause**: Conda not initialized for bash

**Solution**:
```bash
# Initialize conda
conda init bash

# Reload shell
source ~/.bashrc

# Or modify hook to skip conda
# Edit .git/hooks/pre-commit, comment out conda activation
```

---

## Quick Fixes

### "Just Make It Work" Solutions

**Bypass hook temporarily**:
```bash
git commit --no-verify -m "Message"
```

**Force regenerate all docs**:
```bash
rm -rf jarvis/docs/content/
python jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/
git add jarvis/docs/
git commit -m "Regenerate all documentation"
```

**Reset main to match dev**:
```bash
git checkout main
git reset --hard dev
git push --force origin main  # DANGEROUS! Only if you're alone
```

**Undo last commit (not pushed)**:
```bash
git reset --soft HEAD~1  # Keeps changes staged
# or
git reset --hard HEAD~1  # Deletes changes
```

---

## Getting Help

### Debug Mode

Run scripts with verbose output:
```bash
# Add debug to Python scripts
python -v jarvis/utils/extract_comments.py jarvis/

# Check git hook output
bash -x .git/hooks/pre-commit
```

### Check Logs

**Git Hook Log**:
```bash
# Hook output is shown during commit
# No log file, but you can add logging:
# Edit .git/hooks/pre-commit, add:
exec > >(tee /tmp/pre-commit.log) 2>&1
```

**GitHub Actions Log**:
1. Go to repository → Actions
2. Click on workflow run
3. Click on job
4. Expand steps to see detailed logs

---

## Still Stuck?

1. **Read the error message carefully** - It usually tells you what's wrong
2. **Check the script manually** - Run Python scripts outside the hook
3. **Verify your environment** - Python version, dependencies, etc.
4. **Start fresh** - Create test repository to isolate the issue
5. **Check documentation** - Re-read relevant guide sections

---

## Common Error Messages

| Error | Likely Cause | Fix |
|-------|--------------|-----|
| "Permission denied" | File not executable | `chmod +x <file>` |
| "No such file" | Wrong directory | `cd` to repo root |
| "Module not found" | Import path issue | Run from correct directory |
| "Merge conflict" | Branches diverged | Resolve conflicts manually |
| "403 Forbidden" (GitHub) | Permissions issue | Check workflow permissions |
| "404 Not Found" (Pages) | Site not deployed yet | Wait 3-5 minutes |

---

**Remember**: Most issues are fixable! Take a breath, read the error, and try the solutions above.

**Need more help?** Check [08_TECHNICAL_REFERENCE.md](./08_TECHNICAL_REFERENCE.md) for script details.
