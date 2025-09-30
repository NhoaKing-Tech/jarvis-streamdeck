#!/usr/bin/env python3
"""
Comment Annotation System

This module provides tools to manage different types of comments:
- DEV: Detailed development explanations for documentation
- PROD: Essential comments that stay in production code
- ARCH: Architecture decisions and design rationale
- EDU: Educational content and computer science concepts

Usage:
    python annotation_system.py clean-prod jarvis/    # Create production version
    python annotation_system.py extract-docs jarvis/  # Extract docs comments
"""

import re
import os
from pathlib import Path
from typing import List, Dict, Tuple
import shutil

class CommentAnnotationSystem:
    def __init__(self):
        self.dev_prefixes = ['# DEV:', '# ARCH:', '# EDU:']
        self.prod_prefixes = ['# PROD:']

    def classify_comment(self, comment_line: str) -> Tuple[str, str]:
        """
        Classify a comment line and return (type, content).

        Returns:
            tuple: (comment_type, clean_content)
                comment_type: 'DEV', 'PROD', 'ARCH', 'EDU', or 'REGULAR'
                clean_content: comment text without prefix
        """
        stripped = comment_line.strip()

        if stripped.startswith('# DEV:'):
            return 'DEV', stripped[6:].strip()
        elif stripped.startswith('# ARCH:'):
            return 'ARCH', stripped[7:].strip()
        elif stripped.startswith('# EDU:'):
            return 'EDU', stripped[6:].strip()
        elif stripped.startswith('# PROD:'):
            return 'PROD', stripped[7:].strip()
        elif stripped.startswith('#'):
            return 'REGULAR', stripped[1:].strip()
        else:
            return 'CODE', stripped

    def process_file_for_production(self, file_path: Path) -> str:
        """
        Process a Python file to keep only PROD and REGULAR comments.
        Returns the cleaned content as a string.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        cleaned_lines = []
        for line in lines:
            comment_type, content = self.classify_comment(line)

            if comment_type in ['DEV', 'ARCH', 'EDU']:
                # Skip development/educational comments
                continue
            elif comment_type == 'PROD':
                # Convert PROD: prefix to regular comment
                indentation = len(line) - len(line.lstrip())
                cleaned_lines.append(' ' * indentation + f"# {content}\n")
            else:
                # Keep regular comments and code as-is
                cleaned_lines.append(line)

        return ''.join(cleaned_lines)

    def extract_dev_comments(self, file_path: Path) -> Dict[str, List[Tuple[int, str]]]:
        """
        Extract all development comments from a file.

        Returns:
            dict: {comment_type: [(line_number, content), ...]}
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        dev_comments = {
            'DEV': [],
            'ARCH': [],
            'EDU': [],
            'REGULAR': []
        }

        for i, line in enumerate(lines, 1):
            comment_type, content = self.classify_comment(line)

            if comment_type in dev_comments:
                dev_comments[comment_type].append((i, content))

        return dev_comments

    def create_production_version(self, source_dir: Path, target_dir: Path):
        """
        Create a production version of the codebase with only essential comments.
        """
        if target_dir.exists():
            shutil.rmtree(target_dir)

        target_dir.mkdir(parents=True)

        for root, dirs, files in os.walk(source_dir):
            # Skip certain directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            rel_root = Path(root).relative_to(source_dir)
            target_root = target_dir / rel_root
            target_root.mkdir(parents=True, exist_ok=True)

            for file in files:
                source_file = Path(root) / file
                target_file = target_root / file

                if file.endswith('.py'):
                    # Process Python files
                    cleaned_content = self.process_file_for_production(source_file)
                    with open(target_file, 'w', encoding='utf-8') as f:
                        f.write(cleaned_content)
                else:
                    # Copy other files as-is
                    shutil.copy2(source_file, target_file)

        print(f"✅ Production version created in {target_dir}")

def main():
    import sys

    if len(sys.argv) < 3:
        print("Usage: python annotation_system.py <command> <directory>")
        print("Commands:")
        print("  clean-prod <dir>   - Create production version in <dir>_prod")
        print("  extract-docs <dir> - Extract development comments for docs")
        return

    command = sys.argv[1]
    directory = Path(sys.argv[2])

    system = CommentAnnotationSystem()

    if command == "clean-prod":
        target_dir = directory.parent / f"{directory.name}_prod"
        system.create_production_version(directory, target_dir)

    elif command == "extract-docs":
        for py_file in directory.rglob("*.py"):
            comments = system.extract_dev_comments(py_file)
            if any(comments.values()):
                print(f"\n📁 {py_file}")
                for comment_type, comment_list in comments.items():
                    if comment_list:
                        print(f"  {comment_type}: {len(comment_list)} comments")

if __name__ == "__main__":
    main()