# Tag Usage Guide: What to Keep vs. Strip

**Audience**: Developers using the documentation system
**Purpose**: Guide for using comment tags effectively

---

## Table of Contents

1. [Tag Philosophy](#tag-philosophy)
2. [Production Tags (Keep)](#production-tags-keep)
3. [Development Tags (Strip)](#development-tags-strip)
4. [Tag Usage Examples](#tag-usage-examples)
5. [Configuration](#configuration)
6. [Best Practices](#best-practices)
7. [Decision Tree](#decision-tree)

---

## Tag Philosophy

### The Core Principle

**Production code should be clean, professional, and helpful to developers.**

### Two Categories of Comments

```
┌─────────────────────────────────────────────────────────┐
│  PRODUCTION COMMENTS (Keep in main branch)             │
│  • Help developers understand the code                  │
│  • Provide critical information                         │
│  • Document non-obvious decisions                       │
│  • Professional and concise                             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  DEVELOPMENT COMMENTS (Strip from main branch)         │
│  • Educational explanations (too verbose)               │
│  • Temporary notes and cleanup markers                  │
│  • Debug and review comments                            │
│  • Learning resources                                   │
│  • Become documentation instead                         │
└─────────────────────────────────────────────────────────┘
```

---

## Production Tags (Keep)

These tags provide **value to developers** reading the code.

### `#NOTE` ✅ - Implementation Notes

**Purpose**: Document important implementation details

**Keep because**:
- Helps developers understand non-obvious decisions
- Explains "why" not just "what"
- Documents assumptions and constraints

**Examples**:
```python
# NOTE: This assumes only one StreamDeck device is connected.
# NOTE: Must be called before deck.open() or device won't initialize.
# NOTE: We use threading here because the StreamDeck library is blocking.
```

**When to use**:
- Explaining design decisions
- Documenting assumptions
- Clarifying non-obvious behavior
- Warning about constraints

---

### `#IMPORTANT` ✅ - Critical Information

**Purpose**: Highlight critical information developers MUST know

**Keep because**:
- Prevents bugs and errors
- Documents safety requirements
- Alerts to breaking changes

**Examples**:
```python
# IMPORTANT: This function must be called from the main thread only.
# IMPORTANT: Changing this value will break backward compatibility.
# IMPORTANT: Do not modify this list while iterating over it.
```

**When to use**:
- Safety-critical information
- Thread-safety requirements
- API contracts
- Breaking change warnings

---

### `#OPTIMIZE` ✅ - Performance Considerations

**Purpose**: Document performance implications and optimization opportunities

**Keep because**:
- Helps future optimization efforts
- Explains performance trade-offs
- Shows areas for improvement

**Examples**:
```python
# OPTIMIZE: This could be cached for better performance in high-load scenarios.
# OPTIMIZE: Consider using a set instead of list for O(1) lookup.
# OPTIMIZE: This loop could be vectorized with numpy for 10x speedup.
```

**When to use**:
- Known performance bottlenecks
- Trade-offs made for readability
- Future optimization opportunities
- Performance-critical sections

---

### `#TODO` ✅ - Future Work

**Purpose**: Track future improvements and planned features

**Keep because**:
- Documents planned enhancements transparently
- Tracks technical roadmap in the code
- Shows active development and improvement plans
- Helps contributors identify areas to work on

**Examples**:
```python
# TODO: Add support for multiple StreamDeck devices
# TODO: Implement configuration validation
# TODO: Add retry logic for network failures
```

**When to use**:
- Planned feature additions
- Known improvements needed
- Future enhancements
- Features to implement

---

### `#FIXME` ✅ - Known Issues

**Purpose**: Document known issues and limitations transparently

**Keep because**:
- Transparency about known problems
- Helps developers avoid pitfalls
- Shows honest assessment of code quality
- Guides where testing/caution is needed

**Examples**:
```python
# FIXME: This doesn't handle None input gracefully
# FIXME: Race condition possible under high load
# FIXME: Memory usage grows unbounded for large datasets
```

**When to use**:
- Known bugs that aren't critical
- Edge cases not yet handled
- Issues that need investigation
- Problems with workarounds in place

---

### `#HACK` ✅ - Workarounds and Technical Debt

**Purpose**: Document workarounds and temporary solutions honestly

**Keep because**:
- Documents technical debt transparently
- Explains why "proper" solution isn't used
- Warns developers about fragile code
- Shows areas needing future refactoring

**Examples**:
```python
# HACK: Sleep to avoid race condition (library issue, fixed in v2.0)
# HACK: Hardcoded timeout due to library API limitations
# HACK: Manual memory management until we upgrade Python version
```

**When to use**:
- Working around external library bugs
- Temporary solutions due to time constraints
- Compromises for compatibility
- Areas of technical debt

---

## Development Tags (Strip)

These tags are **development artifacts** that don't belong in production.

### `#EDU` ❌ - Educational Content

**Purpose**: Explain concepts for learning (too verbose for production)

**Strip because**:
- Too detailed for production code
- Makes code hard to read
- Belongs in documentation instead

**Examples**:
```python
# EDU: Observer Pattern Implementation
# EDU: ====================================
# EDU: This implements the Observer pattern where observers
# EDU: subscribe to events and get notified when they occur.
# EDU: Benefits:
# EDU: 1. Loose coupling between components
# EDU: 2. Easy to add new observers
# EDU: 3. Runtime subscription management
```

**Instead**: Extract to documentation!

**What happens**:
- ✅ Extracted to markdown → `docs/content/educational/`
- ✅ Becomes beautiful documentation
- ❌ Removed from production code

---

### `#TOCLEAN` ❌ - Needs Polishing

**Purpose**: Mark code that needs cleanup or refinement

**Strip because**:
- Indicates incomplete work
- Production code should be polished
- Should be cleaned before release

**Examples**:
```python
# TOCLEAN: This whole section needs refactoring
# TOCLEAN: Variable names are confusing, rename them
# TOCLEAN: Extract this logic into a separate function
```

**What to do**: Clean it up before merging to main!

---

### `#DEBUG` ❌ - Debugging Aids

**Purpose**: Mark debug code, print statements, etc.

**Strip because**:
- Not needed in production
- Creates noise in logs
- Should use proper logging instead

**Examples**:
```python
# DEBUG: Print state for troubleshooting
# DEBUG: Uncomment to see intermediate values
# DEBUG: Temporary assertion to track down bug
```

**What to do**: Remove debug code, use logging framework instead

---

### `#REVIEW` ❌ - Needs Review

**Purpose**: Mark code that needs review or indicates uncertainty

**Strip because**:
- Code should be reviewed before production
- Indicates lack of confidence
- Should be resolved through code review

**Examples**:
```python
# REVIEW: Is this the best approach?
# REVIEW: Not sure if this handles all edge cases
# REVIEW: Does this need error handling?
```

**What to do**: Get it reviewed, resolve questions, then remove tag

---

## Tag Usage Examples

### Good Production Comments ✅

```python
# NOTE: This function is called from a signal handler, keep it lightweight
def signal_handler(signum, frame):
    cleanup()

# IMPORTANT: Do not call this while holding a lock, will cause deadlock
def acquire_resource():
    with self.lock:
        ...

# OPTIMIZE: Consider using bisect for O(log n) instead of O(n)
def find_item(items, target):
    for item in items:  # Linear search
        if item == target:
            return item
```

**Why good**: Concise, professional, adds value for developers

---

### Bad Production Comments ❌

```python
# EDU: This is a factory pattern implementation. The factory pattern
# EDU: is a creational design pattern that provides an interface for
# EDU: creating objects in a superclass, but allows subclasses to
# EDU: alter the type of objects that will be created...
# (50 more lines of explanation)
def create_handler(type):  # Too verbose!
    ...

# TOCLEAN: This is messy, refactor later
# DEBUG: Print everything for troubleshooting
# REVIEW: Not sure if this is the best approach
def sketchy_function():  # Development tags don't belong in production!
    ...
```

**Why bad**: Too verbose for production, development-only tags

---

## Configuration

### Current Configuration

Located in `jarvis/utils/strip_comments.py`:

```python
# Tags STRIPPED from production
DEFAULT_STRIP_TAGS = [
    'EDU',      # Educational content - too verbose for production
    'TOCLEAN',  # Temporary notes - definitely remove
    'DEBUG',    # Debug comments should not be in production
    'REVIEW',   # Review comments are for development
]

# Tags KEPT in production (transparent about code quality)
KEEP_TAGS = [
    'NOTE',       # Implementation notes - helpful for developers
    'IMPORTANT',  # Critical information should stay
    'OPTIMIZE',   # Performance notes are useful
    'TODO',       # Future work - track in code (transparent roadmap)
    'FIXME',      # Known issues - transparent about problems
    'HACK',       # Workarounds - document technical debt
]
```

**Philosophy**: Keep TODO, FIXME, and HACK to show **transparent engineering** - being honest about known limitations, technical debt, and planned improvements demonstrates professionalism and self-awareness.

### Customizing Tags

You can customize which tags to strip/keep:

```python
from strip_comments import CommentStripper

# Strip everything except IMPORTANT and NOTE
stripper = CommentStripper(
    strip_tags=['EDU', 'TOCLEAN', 'TODO', 'FIXME', 'HACK', 'DEBUG', 'REVIEW', 'OPTIMIZE'],
    keep_tags=['IMPORTANT', 'NOTE']
)

# Or keep everything (no stripping)
stripper = CommentStripper(
    strip_tags=[],
    keep_tags=['EDU', 'NOTE', 'TOCLEAN', 'FIXME', 'TODO', 'HACK', 'DEBUG', 'REVIEW', 'IMPORTANT', 'OPTIMIZE']
)
```

---

## Best Practices

### Writing Production Comments

**DO** ✅:
- Keep them concise (1-2 lines max)
- Explain "why" not "what" (code shows what)
- Add value for future developers
- Use proper grammar and spelling
- Be professional

**DON'T** ❌:
- Write essays (use #EDU tags for docs instead)
- State the obvious
- Use slang or jokes (be professional)
- Leave debug code or #TOCLEAN markers
- Leave #REVIEW questions unresolved

---

### Example Transformation

**Before (Development)**:
```python
# EDU: Lambda Functions in Python
# EDU: ============================
# EDU: Lambda functions are small anonymous functions defined with
# EDU: the lambda keyword. They can have any number of arguments
# EDU: but only one expression. The expression is evaluated and returned.
# EDU:
# EDU: Syntax: lambda arguments: expression
# EDU:
# EDU: Benefits:
# EDU: - Concise for simple operations
# EDU: - Can be used inline
# EDU: - Useful for functional programming
# EDU:
# TOCLEAN: Refactor variable names for clarity
# DEBUG: Print values for troubleshooting
# REVIEW: Is this the best approach?

# IMPORTANT: Only works with positive integers
# TODO: Add support for negative integers
# FIXME: Doesn't validate input type
def process_items(items):
    # Filter using lambda
    return filter(lambda x: x > 0, items)
```

**After (Production)**:
```python
# IMPORTANT: Only works with positive integers
# TODO: Add support for negative integers
# FIXME: Doesn't validate input type
def process_items(items):
    return filter(lambda x: x > 0, items)
```

**What happened**:
- ✅ **#EDU content** → Extracted to `docs/content/educational/lambda-functions.md`
- ✅ **#IMPORTANT, #TODO, #FIXME** → Kept in production (transparent engineering)
- ❌ **#TOCLEAN, #DEBUG, #REVIEW** → Stripped (development-only tags)

---

### When to Use Each Tag

```
WRITING CODE:
├─ Is it critical/safety info? → #IMPORTANT (keep in production)
├─ Is it explaining implementation? → #NOTE (keep in production)
├─ Is it about performance? → #OPTIMIZE (keep in production)
├─ Is it planned future work? → #TODO (keep - shows roadmap)
├─ Is it a known issue/limitation? → #FIXME (keep - shows honesty)
├─ Is it a workaround/tech debt? → #HACK (keep - documents debt)
├─ Is it teaching a concept? → #EDU (strip - becomes docs)
├─ Is it temporary/messy? → #TOCLEAN (strip - clean before commit)
├─ Is it for debugging? → #DEBUG (strip - remove before commit)
└─ Does it need review? → #REVIEW (strip - resolve before commit)
```

---

## Decision Tree

### Should This Comment Be in Production?

```
┌─────────────────────────────────────────────────┐
│  Ask: Does this help developers understand      │
│  or work with this code effectively?             │
└──────────────────┬──────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
        YES                 NO
         │                   │
         ▼                   ▼
┌─────────────────┐   ┌──────────────────────┐
│ Is it:          │   │ Is it:               │
│ • Critical?     │   │ • Long educational   │
│ • Important?    │   │   explanation?       │
│ • Non-obvious?  │   │ • Temporary/debug?   │
│ • Performance?  │   │ • Needs cleanup?     │
│ • TODO/roadmap? │   │ • Needs review?      │
│ • Known issue?  │   │                      │
│ • Tech debt?    │   │                      │
└────────┬────────┘   └──────────┬───────────┘
         │                       │
        YES                     YES
         │                       │
         ▼                       ▼
    ┌─────────┐           ┌───────────────┐
    │  KEEP   │           │  STRIP        │
    │ (prod)  │           │ (to docs or   │
    │         │           │  just remove) │
    └─────────┘           └───────────────┘
```

---

## Summary

### Quick Reference Table

| Tag | Keep? | Production | Documentation | Rationale |
|-----|-------|-----------|---------------|-----------|
| `#NOTE` | ✅ Yes | Stays in code | Also extracted | Helpful implementation notes |
| `#IMPORTANT` | ✅ Yes | Stays in code | Also extracted | Critical information |
| `#OPTIMIZE` | ✅ Yes | Stays in code | Also extracted | Performance considerations |
| `#TODO` | ✅ Yes | Stays in code | Also extracted | Transparent roadmap |
| `#FIXME` | ✅ Yes | Stays in code | Also extracted | Honest about limitations |
| `#HACK` | ✅ Yes | Stays in code | Also extracted | Documents technical debt |
| `#EDU` | ❌ No | Removed | Extracted to docs | Too verbose for production |
| `#TOCLEAN` | ❌ No | Removed | Not extracted | Clean before commit |
| `#DEBUG` | ❌ No | Removed | Not extracted | Remove debug code |
| `#REVIEW` | ❌ No | Removed | Not extracted | Resolve before commit |

---

### The Golden Rule

```
Production comments should answer:
  "What does a developer need to know to work with this code safely and effectively?"

This includes:
  ✅ Critical safety information
  ✅ Non-obvious implementation details
  ✅ Performance considerations
  ✅ Known limitations and future plans (transparent engineering)

NOT:
  ❌ Long educational essays (use #EDU → docs)
  ❌ Temporary notes that need cleanup
  ❌ Debug code and review questions
```

---

## Related Documentation

- **[02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md](./02_WORKFLOW_2_DOCUMENTATION_PIPELINE.md)** - How tags become documentation
- **[08_TECHNICAL_REFERENCE.md](./08_TECHNICAL_REFERENCE.md)** - strip_comments.py API
- **[10_GIT_HOOKS.md](./10_GIT_HOOKS.md)** - Automated tag processing

---

## Quick Command Reference

### Check What Will Be Stripped

```bash
# Dry run to see what would be removed
python jarvis/utils/strip_comments.py jarvis/actions/actions.py --dry-run
```

### Strip Comments from File

```bash
# Create clean version
python jarvis/utils/strip_comments.py jarvis/actions/actions.py \
  --output jarvis_clean/actions/actions.py
```

### Custom Tag Configuration

```bash
# Strip only EDU and TOCLEAN tags (keep everything else)
python jarvis/utils/strip_comments.py jarvis/actions/actions.py \
  --strip-tags EDU TOCLEAN DEBUG REVIEW \
  --output clean.py
```

---

**Remember**: Production code should be clean, professional, and helpful. Educational content belongs in documentation, but transparency about limitations, future work, and technical debt demonstrates engineering maturity! 📚
