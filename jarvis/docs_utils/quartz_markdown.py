#!/usr/bin/env python3
"""
Generate Quartz-optimized Markdown documentation from Python docstrings.

This script extracts docstrings and comments directly from the Python source files
and formats them as Markdown files suitable for Quartz static site generation.
"""

import ast
import os
from pathlib import Path
import inspect
import importlib.util
import sys
import tokenize
import io
from collections import defaultdict

def classify_comment(comment_line: str):
    """Classify a comment based on annotation prefixes."""
    stripped = comment_line.strip()

    if stripped.startswith('DEV:'):
        return 'DEV', stripped[4:].strip()
    elif stripped.startswith('ARCH:'):
        return 'ARCH', stripped[5:].strip()
    elif stripped.startswith('EDU:'):
        return 'EDU', stripped[4:].strip()
    elif stripped.startswith('PROD:'):
        return 'PROD', stripped[5:].strip()
    else:
        return 'REGULAR', stripped

def extract_comments(file_path):
    """Extract all comments from a Python file using tokenization with annotation support."""
    comments = []
    comment_blocks = []
    dev_comments = {'DEV': [], 'ARCH': [], 'EDU': [], 'PROD': [], 'REGULAR': []}

    try:
        with open(file_path, 'rb') as f:
            tokens = list(tokenize.tokenize(f.readline))

        current_block = []
        last_line = 0

        for token in tokens:
            if token.type == tokenize.COMMENT:
                comment_text = token.string.lstrip('#').strip()
                line_num = token.start[0]

                # Classify the comment
                comment_type, clean_content = classify_comment(comment_text)

                # Store in appropriate category
                dev_comments[comment_type].append({
                    'line': line_num,
                    'text': clean_content,
                    'original': comment_text
                })

                # Group consecutive comments into blocks (prioritize DEV/ARCH/EDU for docs)
                if comment_type in ['DEV', 'ARCH', 'EDU']:
                    if last_line > 0 and line_num == last_line + 1:
                        current_block.append((line_num, clean_content, comment_type))
                    else:
                        # Save previous block if it exists
                        if current_block:
                            comment_blocks.append(current_block)
                        # Start new block
                        current_block = [(line_num, clean_content, comment_type)]

                last_line = line_num
                comments.append({
                    'line': line_num,
                    'text': clean_content,
                    'type': comment_type
                })

        # Don't forget the last block
        if current_block:
            comment_blocks.append(current_block)

    except Exception as e:
        print(f"Warning: Could not extract comments from {file_path}: {e}")

    return comments, comment_blocks, dev_comments

def extract_module_info(file_path):
    """Extract module docstring, function information, and all comments from Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse the AST to extract docstrings and structure
    tree = ast.parse(content)

    module_doc = ast.get_docstring(tree) or ""
    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_doc = ast.get_docstring(node) or ""
            functions.append({
                'name': node.name,
                'docstring': func_doc,
                'line': node.lineno
            })
        elif isinstance(node, ast.ClassDef):
            class_doc = ast.get_docstring(node) or ""
            classes.append({
                'name': node.name,
                'docstring': class_doc,
                'line': node.lineno
            })

    # Extract all comments with annotation support
    comments, comment_blocks, dev_comments = extract_comments(file_path)

    return {
        'module_docstring': module_doc,
        'functions': functions,
        'classes': classes,
        'comments': comments,
        'comment_blocks': comment_blocks,
        'dev_comments': dev_comments,
        'file_name': file_path.stem
    }

def generate_quartz_markdown(module_info, output_path):
    """Generate Quartz-optimized Markdown file with comprehensive documentation."""
    content = []

    # Add Quartz frontmatter
    content.append("---")
    content.append(f"title: {module_info['file_name']}")
    content.append("tags:")
    content.append("  - jarvis")
    content.append("  - python")
    content.append("  - documentation")
    content.append("date: 2025-09-21")
    content.append("---")
    content.append("")

    # Module title and description
    content.append(f"# {module_info['file_name']}")
    content.append("")

    if module_info['module_docstring']:
        content.append(module_info['module_docstring'])
        content.append("")

    # Add development-focused comment sections
    dev_comments = module_info.get('dev_comments', {})

    # Architecture & Design sections
    if dev_comments.get('ARCH'):
        content.append("## Architecture & Design Decisions")
        content.append("")
        for comment in dev_comments['ARCH']:
            content.append(f"**Line {comment['line']}:** {comment['text']}")
            content.append("")

    # Educational content
    if dev_comments.get('EDU'):
        content.append("## Educational Notes & Computer Science Concepts")
        content.append("")

        # Group educational comments into blocks
        edu_blocks = []
        current_block = []
        last_line = 0

        for comment in dev_comments['EDU']:
            if last_line > 0 and comment['line'] == last_line + 1:
                current_block.append(comment)
            else:
                if current_block:
                    edu_blocks.append(current_block)
                current_block = [comment]
            last_line = comment['line']

        if current_block:
            edu_blocks.append(current_block)

        for i, block in enumerate(edu_blocks):
            if len(block) > 1:
                # Multi-line educational block
                title = block[0]['text'][:50] + "..." if len(block[0]['text']) > 50 else block[0]['text']
                content.append(f"### {title}")
                content.append("")
                content.append("```")
                for comment in block:
                    content.append(comment['text'])
                content.append("```")
                content.append("")
            else:
                # Single educational comment
                content.append(f"- **Line {block[0]['line']}:** {block[0]['text']}")

        content.append("")

    # Development notes
    if dev_comments.get('DEV'):
        content.append("## Development Notes & Implementation Details")
        content.append("")
        for comment in dev_comments['DEV']:
            content.append(f"- **Line {comment['line']}:** {comment['text']}")
        content.append("")

    # Table of contents for classes
    if module_info.get('classes'):
        content.append("## Classes")
        content.append("")
        for cls in module_info['classes']:
            if not cls['name'].startswith('_'):  # Skip private classes
                content.append(f"- [[#{cls['name']}|{cls['name']}]]")
        content.append("")

    # Table of contents for functions
    if module_info['functions']:
        content.append("## Functions")
        content.append("")
        for func in module_info['functions']:
            if not func['name'].startswith('_'):  # Skip private functions
                content.append(f"- [[#{func['name']}|{func['name']}()]]")
        content.append("")

    # Class documentation
    for cls in module_info.get('classes', []):
        if cls['name'].startswith('_'):  # Skip private classes
            continue

        content.append(f"## {cls['name']}")
        content.append("")
        content.append(f"```python")
        content.append(f"class {cls['name']}:")
        content.append(f"```")
        content.append("")

        if cls['docstring']:
            # Process the docstring to make it Quartz-friendly
            docstring = cls['docstring']
            docstring = docstring.replace('Args:', '**Args:**')
            docstring = docstring.replace('Returns:', '**Returns:**')
            docstring = docstring.replace('Note:', '**Note:**')
            docstring = docstring.replace('Attributes:', '**Attributes:**')

            content.append(docstring)
            content.append("")

    # Function documentation
    for func in module_info['functions']:
        if func['name'].startswith('_'):  # Skip private functions
            continue

        content.append(f"## {func['name']}")
        content.append("")
        content.append(f"```python")
        content.append(f"def {func['name']}():")
        content.append(f"```")
        content.append("")

        if func['docstring']:
            # Process the docstring to make it Quartz-friendly
            docstring = func['docstring']
            # Convert sections to proper markdown
            docstring = docstring.replace('Args:', '**Args:**')
            docstring = docstring.replace('Returns:', '**Returns:**')
            docstring = docstring.replace('Note:', '**Note:**')
            docstring = docstring.replace('Raises:', '**Raises:**')

            content.append(docstring)
            content.append("")

    # Add production comments section (these will stay in production code)
    if dev_comments.get('PROD'):
        content.append("## Production Code Comments")
        content.append("")
        content.append("Essential comments that remain in the production codebase:")
        content.append("")
        for comment in dev_comments['PROD']:
            content.append(f"- **Line {comment['line']}:** {comment['text']}")
        content.append("")

    # Add other regular comments for context (limited to avoid overwhelming)
    regular_comments = dev_comments.get('REGULAR', [])
    if regular_comments:
        content.append("## Additional Code Context")
        content.append("")
        content.append("Other contextual comments from the codebase:")
        content.append("")

        for comment in regular_comments[:15]:  # Limit to first 15
            if len(comment['text']) > 10:  # Skip very short comments
                content.append(f"- **Line {comment['line']}:** {comment['text']}")

        if len(regular_comments) > 15:
            content.append(f"- ... and {len(regular_comments) - 15} more contextual comments")
        content.append("")

    # Write the file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))

def main():
    """Generate Quartz documentation for all jarvis modules."""

    # Create output directory (relative to docs_utils, output to ../docs/content/)
    output_dir = Path("../docs/content")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Python files to process (relative to jarvis/docs directory)
    python_files = [
        # Root level files
        Path("../../setup.py"),

        # Core jarvis files
        Path("../main.py"),
        Path("../actions/actions.py"),
        Path("../core/application.py"),
        Path("../core/lifecycle.py"),
        Path("../core/logic.py"),
        Path("../ui/render.py"),
        Path("../ui/layouts.py"),
        Path("../config/setup_config.py"),
        Path("../config/initialization.py"),
        Path("../utils/terminal_prints.py"),
        Path("../utils/reset_jarvis.py"),
        Path("../tests/grid_test.py"),
    ]

    # Generate index file
    index_content = [
        "---",
        "title: Jarvis StreamDeck Documentation",
        "tags:",
        "  - jarvis",
        "  - index",
        "date: 2025-09-18",
        "---",
        "",
        "# 🤖 Jarvis StreamDeck Documentation",
        "",
        "Welcome to the comprehensive documentation for the Jarvis StreamDeck automation system.",
        "",
        "## 📋 Core Modules",
        "",
        "- [[main]] - Main application entry point",
        "- [[application]] - Core application logic",
        "- [[actions]] - StreamDeck key actions and functions",
        "- [[logic]] - Event handling and core logic",
        "- [[lifecycle]] - Resource cleanup and safety",
        "",
        "## 🎨 UI Modules",
        "",
        "- [[render]] - Visual rendering system",
        "- [[layouts]] - Layout management and definitions",
        "",
        "## ⚙️ Configuration",
        "",
        "- [[setup_config]] - Interactive configuration wizard",
        "- [[initialization]] - Environment initialization",
        "",
        "## 🔧 Utility Modules",
        "",
        "- [[terminal_prints]] - Terminal output utilities",
        "- [[reset_jarvis]] - Emergency reset and recovery",
        "",
        "## 🧪 Testing",
        "",
        "- [[grid_test]] - Grid layout testing utilities",
        "",
        "## 📦 Setup",
        "",
        "- [[setup]] - Package setup and installation",
        "",
        "## 🚀 Getting Started",
        "",
        "1. Start with [[setup_config]] to configure your environment",
        "2. Review [[main]] to understand the main application flow",
        "3. Explore [[actions]] for available StreamDeck functions",
        "4. Customize layouts in [[render]] and [[layouts]]",
        "5. Keep [[reset_jarvis]] handy for troubleshooting",
    ]

    with open(output_dir / "index.md", 'w') as f:
        f.write('\n'.join(index_content))

    # Process each Python file
    for py_file in python_files:
        if py_file.exists():
            print(f"Processing {py_file}...")
            module_info = extract_module_info(py_file)

            # Create output filename
            output_name = f"{py_file.stem}.md"

            output_path = output_dir / output_name
            generate_quartz_markdown(module_info, output_path)
            print(f"  → Generated {output_path}")

    print(f"\n✅ Generated Quartz documentation in {output_dir}")
    print(f"📁 Files created:")
    for md_file in sorted(output_dir.glob("*.md")):
        print(f"   - {md_file.name}")

if __name__ == "__main__":
    main()