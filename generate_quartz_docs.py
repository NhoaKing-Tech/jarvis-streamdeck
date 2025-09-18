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

def extract_module_info(file_path):
    """Extract module docstring and function information from Python file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse the AST to extract docstrings
    tree = ast.parse(content)

    module_doc = ast.get_docstring(tree) or ""
    functions = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_doc = ast.get_docstring(node) or ""
            functions.append({
                'name': node.name,
                'docstring': func_doc,
                'line': node.lineno
            })

    return {
        'module_docstring': module_doc,
        'functions': functions,
        'file_name': file_path.stem
    }

def generate_quartz_markdown(module_info, output_path):
    """Generate Quartz-optimized Markdown file."""
    content = []

    # Add Quartz frontmatter
    content.append("---")
    content.append(f"title: {module_info['file_name']}")
    content.append("tags:")
    content.append("  - jarvis")
    content.append("  - python")
    content.append("  - documentation")
    content.append("date: 2025-09-18")
    content.append("---")
    content.append("")

    # Module title and description
    content.append(f"# {module_info['file_name']}")
    content.append("")

    if module_info['module_docstring']:
        content.append(module_info['module_docstring'])
        content.append("")

    # Table of contents
    if module_info['functions']:
        content.append("## Functions")
        content.append("")
        for func in module_info['functions']:
            if not func['name'].startswith('_'):  # Skip private functions
                content.append(f"- [[#{func['name']}|{func['name']}()]]")
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

    # Write the file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(content))

def main():
    """Generate Quartz documentation for all jarvis modules."""

    # Create output directory
    output_dir = Path("../content/jarvis-docs")
    output_dir.mkdir(exist_ok=True)

    # Python files to process
    python_files = [
        Path("run_jarvis.py"),
        Path("setup_config.py"),
        Path("reset_jarvis.py"),
        Path("actions/actions.py"),
        Path("ui/render.py"),
        Path("ui/logic.py"),
        Path("ui/lifecycle.py"),
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
        "- [[run_jarvis]] - Main application entry point",
        "- [[actions]] - StreamDeck key actions and functions",
        "",
        "## 🎨 UI Modules",
        "",
        "- [[render]] - Visual rendering system",
        "- [[logic]] - Event handling and layout management",
        "- [[lifecycle]] - Resource cleanup and safety",
        "",
        "## 🔧 Utility Modules",
        "",
        "- [[setup_config]] - Interactive configuration wizard",
        "- [[reset_jarvis]] - Emergency reset and recovery",
        "",
        "## 🚀 Getting Started",
        "",
        "1. Start with [[setup_config]] to configure your environment",
        "2. Review [[run_jarvis]] to understand the main application flow",
        "3. Explore [[actions]] for available StreamDeck functions",
        "4. Customize layouts in [[render]]",
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
            if py_file.parent.name in ['actions', 'ui']:
                output_name = f"{py_file.stem}.md"
            else:
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