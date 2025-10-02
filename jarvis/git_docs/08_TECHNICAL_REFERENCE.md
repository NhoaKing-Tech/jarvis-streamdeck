# Technical Reference

API documentation and technical details for the documentation pipeline scripts.

---

## Script Overview

| Script | Purpose | Location |
|--------|---------|----------|
| `extract_comments.py` | Parse Python files for tagged comments | `jarvis/utils/` |
| `strip_comments.py` | Remove tagged comments from code | `jarvis/utils/` |
| `generate_docs.py` | Convert comments to markdown | `jarvis/utils/` |
| `pre-commit-hook.sh` | Git hook for automation | `jarvis/utils/` → `.git/hooks/` |

---

## extract_comments.py

### Purpose
Extracts comments with special tags from Python source files.

### Usage
```bash
# Single file
python extract_comments.py <file.py>

# Directory (recursive)
python extract_comments.py <directory> --recursive

# Specific tags only
python extract_comments.py <file.py> --tags EDU NOTE

# JSON output
python extract_comments.py <file.py> --output json
```

### Supported Tags (Default)
- EDU, NOTE, TOCLEAN, FIXME, TODO, HACK, DEBUG, IMPORTANT, REVIEW, OPTIMIZE

### Python API
```python
from extract_comments import CommentExtractor

# Create extractor
extractor = CommentExtractor(tag_list=['EDU', 'NOTE'])

# Extract from file
result = extractor.extract_from_file('path/to/file.py')

# Access results
for tag, blocks in result.comments_by_tag.items():
    for block in blocks:
        print(f"{tag}: {block.get_text()}")
```

### Classes

**CommentExtractor**
```python
class CommentExtractor:
    def __init__(self, tag_list=None)
    def extract_from_file(file_path) -> ExtractionResult
    def extract_from_directory(directory, recursive=True) -> Dict[str, ExtractionResult]
```

**CommentBlock**
```python
@dataclass
class CommentBlock:
    tag: str              # Tag type (EDU, NOTE, etc.)
    lines: List[str]      # Comment lines without tag prefix
    line_number: int      # Starting line number
    file_path: str        # Source file path
    context: str          # Function/class context (optional)

    def get_text() -> str  # Get full comment text
    def to_dict() -> dict  # Serialize to dictionary
```

**ExtractionResult**
```python
@dataclass
class ExtractionResult:
    file_path: str
    total_comments: int
    comments_by_tag: Dict[str, List[CommentBlock]]
    untagged_comments: List[str]
```

---

## strip_comments.py

### Purpose
Removes tagged comments from Python files to create clean production code.

### Usage
```bash
# Single file (dry run)
python strip_comments.py <file.py> --dry-run

# Single file (overwrite)
python strip_comments.py <file.py>

# Single file (new file)
python strip_comments.py <file.py> --output <clean_file.py>

# Directory (recursive)
python strip_comments.py <directory> --output <output_dir> --recursive

# Custom tags
python strip_comments.py <file.py> --strip-tags EDU TOCLEAN
```

### Default Behavior
**Strips**: EDU, NOTE, TOCLEAN, FIXME, TODO, HACK, DEBUG, REVIEW
**Keeps**: IMPORTANT, OPTIMIZE (and all regular comments)

### Python API
```python
from strip_comments import CommentStripper

# Create stripper
stripper = CommentStripper(
    strip_tags=['EDU', 'TOCLEAN'],
    keep_tags=['IMPORTANT']
)

# Strip file
result = stripper.strip_file(
    'input.py',
    'output.py',
    dry_run=False
)

# Access results
print(f"Removed {result['lines_removed']} lines")
print(f"Reduction: {result['reduction_percent']:.1f}%")
```

### Classes

**CommentStripper**
```python
class CommentStripper:
    def __init__(self, strip_tags=None, keep_tags=None)
    def strip_file(input_path, output_path=None, dry_run=False) -> dict
    def strip_directory(input_dir, output_dir=None, recursive=True) -> dict
```

---

## generate_docs.py

### Purpose
Generates markdown documentation from extracted comments.

### Usage
```bash
# Generate from directory
python generate_docs.py <source_dir> --output <docs_dir>

# Custom title
python generate_docs.py jarvis/ --output docs/ --title "My Docs"

# No frontmatter
python generate_docs.py jarvis/ --output docs/ --no-frontmatter
```

### Output Structure
```
docs/
├── index.md                 # Main index
├── educational/
│   ├── index.md            # Category index
│   ├── actions.md          # Generated from actions.py
│   └── application.md      # Generated from application.py
├── notes/
│   ├── index.md
│   └── implementation.md
└── important/
    └── index.md
```

### Python API
```python
from generate_docs import MarkdownGenerator, generate_docs_from_directory

# Quick generation
result = generate_docs_from_directory(
    source_dir='jarvis/',
    output_dir='docs/content/',
    site_title='My Documentation'
)

# Or use generator directly
generator = MarkdownGenerator(
    output_dir='docs/',
    site_title='My Docs',
    add_frontmatter=True
)

# Generate from extraction result
from extract_comments import CommentExtractor
extractor = CommentExtractor()
result = extractor.extract_from_file('file.py')
files = generator.generate_docs_from_result(result)
```

### Classes

**MarkdownGenerator**
```python
class MarkdownGenerator:
    def __init__(self, output_dir, site_title="Jarvis Documentation", add_frontmatter=True)
    def generate_frontmatter(title, tags=None, description=None) -> str
    def generate_doc_for_tag(tag, blocks, source_file) -> str
    def generate_docs_from_result(result: ExtractionResult) -> Dict[str, Path]
    def generate_category_index(tag, files) -> Path
    def generate_main_index(files_by_category) -> Path
```

---

## pre-commit-hook.sh

### Purpose
Git hook that automates documentation generation on commit.

### Installation
```bash
cp jarvis/utils/pre-commit-hook.sh .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

### Behavior

**On Dev Branch**:
1. Detects modified Python files
2. Runs `generate_docs.py`
3. Stages generated markdown files
4. Allows commit to proceed

**On Main Branch**:
1. Checks for tagged comments (should be clean)
2. Warns if development tags found
3. Verifies documentation exists
4. Allows commit if clean

**On Other Branches**:
- Basic validation only
- No automatic doc generation

### Configuration

Edit the hook to customize:

```bash
# Change Python command
PYTHON_CMD="python3"  # or "/usr/bin/python"

# Disable conda activation
# Comment out these lines:
# if conda info --envs | grep -q "jarvis-busybee"; then
#     conda activate jarvis-busybee
# fi

# Add logging
exec > >(tee /tmp/pre-commit.log) 2>&1

# Change doc output directory
# Modify this line:
$PYTHON_CMD jarvis/utils/generate_docs.py jarvis/ --output jarvis/docs/content/
```

### Bypass Hook
```bash
# Skip hook for one commit (emergency only!)
git commit --no-verify -m "Message"
```

---

## GitHub Actions Workflow

### File
`.github/workflows/deploy-docs.yml`

### Triggers
- Push to `main` branch
- Changes to `jarvis/docs/**`
- Manual dispatch via Actions tab

### Steps
1. Checkout repository
2. Setup Node.js 18
3. Install Quartz
4. Copy documentation to Quartz
5. Configure Quartz
6. Build static site
7. Deploy to GitHub Pages

### Customization

**Change Quartz version**:
```yaml
- name: Install Quartz
  run: |
    git clone --branch v4.0.0 https://github.com/jackyzha0/quartz.git
```

**Change Node version**:
```yaml
- uses: actions/setup-node@v4
  with:
    node-version: '20'  # or '16', '18'
```

**Change base URL**:
```yaml
# In quartz.config.ts generation:
baseUrl: "your-username.github.io/your-repo"
```

---

## Tag System Reference

### Tag Format
```python
# TAG: Content
# TAG Content
#TAG: Content
```

All variations work. Tag name is case-insensitive.

### Multi-Line Blocks
```python
# EDU: First line
# EDU: Second line
# Continuation (no tag = continues previous tag)
# More content
```

Lines without tags after a tagged line continue the block until:
- A non-comment line appears
- A different tag appears
- End of file

### Tag Categories

**Documentation Tags** (extracted to markdown):
- `EDU` → `educational/` directory
- `NOTE` → `notes/` directory
- `IMPORTANT` → `important/` directory

**Development Tags** (typically stripped):
- `TOCLEAN`, `FIXME`, `TODO`, `HACK`, `DEBUG`, `REVIEW`

### Adding Custom Tags

**1. Edit `extract_comments.py`**:
```python
SUPPORTED_TAGS = [
    'EDU',
    'MYTAG',  # Add here
    # ...
]
```

**2. Edit `generate_docs.py`**:
```python
self.tag_categories = {
    'MYTAG': {
        'title': 'My Custom Docs',
        'description': 'Custom documentation category',
        'dir': 'custom'
    },
    # ...
}
```

**3. Optionally edit `strip_comments.py`**:
```python
DEFAULT_STRIP_TAGS = [
    'EDU',
    'MYTAG',  # If you want it stripped from production
    # ...
]
```

---

## Performance Characteristics

### extract_comments.py
- **Complexity**: O(n) where n = number of lines
- **Memory**: Loads entire file into memory
- **Speed**: ~1000 files/second on typical hardware

### strip_comments.py
- **Complexity**: O(n) where n = number of lines
- **Memory**: Loads entire file into memory
- **Speed**: ~500 files/second (slower due to writing)

### generate_docs.py
- **Complexity**: O(n*m) where n = files, m = comments per file
- **Memory**: Processes one file at a time
- **Speed**: ~100 files/second (slower due to markdown generation)

### Pre-commit Hook
- **Total time**: 1-5 seconds for typical repository
- **Breakdown**:
  - Python startup: 0.5s
  - Extract comments: 1-2s
  - Generate markdown: 1-2s
  - Git staging: 0.5s

---

## File Formats

### ExtractionResult JSON
```json
{
  "file_path": "jarvis/actions.py",
  "total_comments": 15,
  "comments_by_tag": {
    "EDU": [
      {
        "tag": "EDU",
        "lines": ["Comment line 1", "Comment line 2"],
        "line_number": 42,
        "file_path": "jarvis/actions.py",
        "context": "function: init_module"
      }
    ]
  },
  "untagged_comments": ["Regular comment"]
}
```

### Generated Markdown Frontmatter
```yaml
---
title: "Educational Content: Actions"
tags: [edu, auto-generated]
description: "Educational Content from actions.py"
date: 2025-10-02
---
```

---

## Dependencies

### Python Scripts
- **Python**: 3.7+
- **Standard library only**: No external dependencies required
- **Optional**: `pathlib`, `dataclasses` (included in Python 3.7+)

### Git Hook
- **Bash**: 4.0+
- **Git**: 2.0+
- **Python**: 3.7+ (called by hook)
- **Optional**: Conda (for environment activation)

### GitHub Actions
- **Node.js**: 18+ (installed by workflow)
- **Quartz**: Latest (cloned by workflow)
- **GitHub Pages**: Enabled in repository settings

---

## Exit Codes

**Python Scripts**:
- `0`: Success
- `1`: Error (file not found, syntax error, etc.)

**Pre-commit Hook**:
- `0`: Success, allow commit
- `1`: Failure, block commit

---

**For more examples and use cases, see the individual guides:**
- [02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md](./02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md)
- [03_SETUP_INSTRUCTIONS.md](./03_SETUP_INSTRUCTIONS.md)
