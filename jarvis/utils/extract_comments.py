#!/usr/bin/env python3
"""
Comment Extraction Tool for Documentation Pipeline
===================================================

AUTHOR: NhoaKing
PROJECT: jarvis-streamdeck
PURPOSE: Extract tagged comments from Python files for documentation generation

DESCRIPTION:
This script parses Python source files and extracts comments with special tags
(#EDU, #NOTE, #TOCLEAN, etc.) to generate structured documentation.

USAGE:
    python extract_comments.py <source_file> [--output json|dict]
    python extract_comments.py jarvis/actions/actions.py
    python extract_comments.py jarvis/ --recursive

PRINCIPLES:
- Single-sourcing: Comments are the source of truth for documentation
- Automation: Integrated with git hooks for automatic extraction
- Structure: Maintains comment context and relationships
"""

import re
import ast
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
from dataclasses import dataclass, asdict
from collections import defaultdict


# Supported tag types for comment extraction
SUPPORTED_TAGS = [
    'EDU',      # Educational content - design patterns, CS concepts
    'NOTE',     # Implementation notes and important details
    'TOCLEAN',  # Temporary notes to clean up
    'FIXME',    # Known issues that need fixing
    'TODO',     # Future improvements
    'HACK',     # Workarounds and temporary solutions
    'DEBUG',    # Debugging aids
    'IMPORTANT',# Critical information
    'REVIEW',   # Code that needs review
    'OPTIMIZE', # Performance optimization notes
]


@dataclass
class CommentBlock:
    """Represents a block of tagged comments."""
    tag: str
    lines: List[str]
    line_number: int
    file_path: str
    context: Optional[str] = None  # Function/class context

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    def get_text(self) -> str:
        """Get comment text without tag prefixes."""
        return '\n'.join(self.lines)


@dataclass
class ExtractionResult:
    """Results from extracting comments from a file."""
    file_path: str
    total_comments: int
    comments_by_tag: Dict[str, List[CommentBlock]]
    untagged_comments: List[str]

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'file_path': self.file_path,
            'total_comments': self.total_comments,
            'comments_by_tag': {
                tag: [block.to_dict() for block in blocks]
                for tag, blocks in self.comments_by_tag.items()
            },
            'untagged_comments': self.untagged_comments
        }


class CommentExtractor:
    """Extract and categorize tagged comments from Python source files."""

    def __init__(self, tag_list: Optional[List[str]] = None):
        """
        Initialize the comment extractor.

        Args:
            tag_list: List of tags to extract. If None, uses SUPPORTED_TAGS.
        """
        self.tags = tag_list or SUPPORTED_TAGS
        # Create regex pattern to match any of the tags
        # Matches: # TAG: content or #TAG content or # TAG content
        tag_pattern = '|'.join(self.tags)
        self.tag_regex = re.compile(
            rf'^\s*#\s*({tag_pattern})[\s:]*(.*)$',
            re.IGNORECASE
        )

    def extract_from_file(self, file_path: Path) -> ExtractionResult:
        """
        Extract tagged comments from a Python file.

        Args:
            file_path: Path to Python source file

        Returns:
            ExtractionResult containing categorized comments
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        comments_by_tag = defaultdict(list)
        untagged_comments = []
        current_block = None
        current_tag = None
        total_count = 0

        # Try to parse AST for context (function/class names)
        context_map = self._build_context_map(file_path)

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Check if line is a comment
            if not stripped.startswith('#'):
                # If we were building a block, save it
                if current_block:
                    comments_by_tag[current_tag].append(current_block)
                    current_block = None
                    current_tag = None
                continue

            # Check if comment has a tag
            match = self.tag_regex.match(line)

            if match:
                tag = match.group(1).upper()
                content = match.group(2).strip()

                # If starting a new tag block
                if current_tag != tag:
                    # Save previous block if exists
                    if current_block:
                        comments_by_tag[current_tag].append(current_block)

                    # Start new block
                    context = context_map.get(line_num, None)
                    current_block = CommentBlock(
                        tag=tag,
                        lines=[content] if content else [],
                        line_number=line_num,
                        file_path=str(file_path),
                        context=context
                    )
                    current_tag = tag
                    total_count += 1
                else:
                    # Continue current block
                    if content:
                        current_block.lines.append(content)

            elif current_block:
                # Comment line without tag, but we're in a tagged block
                # Check if it's a continuation (starts with #)
                if stripped.startswith('#'):
                    # Remove # and any leading/trailing whitespace
                    content = stripped[1:].strip()
                    if content or not current_block.lines:  # Allow empty lines in blocks
                        current_block.lines.append(content)
                else:
                    # Non-comment line, end the block
                    comments_by_tag[current_tag].append(current_block)
                    current_block = None
                    current_tag = None
            else:
                # Untagged comment
                if stripped.startswith('#'):
                    comment_text = stripped[1:].strip()
                    if comment_text:
                        untagged_comments.append(comment_text)

        # Save any remaining block
        if current_block:
            comments_by_tag[current_tag].append(current_block)

        return ExtractionResult(
            file_path=str(file_path),
            total_comments=total_count,
            comments_by_tag=dict(comments_by_tag),
            untagged_comments=untagged_comments
        )

    def _build_context_map(self, file_path: Path) -> Dict[int, str]:
        """
        Build a map of line numbers to function/class context.

        Args:
            file_path: Path to Python file

        Returns:
            Dictionary mapping line numbers to context strings
        """
        context_map = {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    context = f"function: {node.name}"
                    # Map all lines in function to this context
                    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                        for line in range(node.lineno, (node.end_lineno or node.lineno) + 1):
                            context_map[line] = context

                elif isinstance(node, ast.ClassDef):
                    context = f"class: {node.name}"
                    if hasattr(node, 'lineno') and hasattr(node, 'end_lineno'):
                        for line in range(node.lineno, (node.end_lineno or node.lineno) + 1):
                            context_map[line] = context

        except SyntaxError:
            # If file has syntax errors, skip context mapping
            pass

        return context_map

    def extract_from_directory(
        self,
        directory: Path,
        recursive: bool = True,
        pattern: str = "*.py"
    ) -> Dict[str, ExtractionResult]:
        """
        Extract comments from all Python files in a directory.

        Args:
            directory: Path to directory
            recursive: Whether to search subdirectories
            pattern: File pattern to match

        Returns:
            Dictionary mapping file paths to ExtractionResults
        """
        directory = Path(directory)
        results = {}

        if recursive:
            files = directory.rglob(pattern)
        else:
            files = directory.glob(pattern)

        for file_path in files:
            if file_path.is_file():
                try:
                    result = self.extract_from_file(file_path)
                    if result.total_comments > 0:
                        results[str(file_path)] = result
                except Exception as e:
                    print(f"Warning: Could not process {file_path}: {e}")

        return results


def print_extraction_summary(result: ExtractionResult) -> None:
    """Print a human-readable summary of extraction results."""
    print(f"\n{'='*70}")
    print(f"File: {result.file_path}")
    print(f"{'='*70}")
    print(f"Total tagged comment blocks: {result.total_comments}")
    print()

    if result.comments_by_tag:
        print("Comments by tag:")
        for tag, blocks in sorted(result.comments_by_tag.items()):
            print(f"  {tag}: {len(blocks)} block(s)")
            for i, block in enumerate(blocks, 1):
                print(f"    Block {i} (line {block.line_number}):")
                if block.context:
                    print(f"      Context: {block.context}")
                preview = block.get_text()
                if len(preview) > 100:
                    preview = preview[:100] + "..."
                print(f"      Preview: {preview}")
                print()

    if result.untagged_comments:
        print(f"\nUntagged comments: {len(result.untagged_comments)}")


def main():
    """Command-line interface for comment extraction."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract tagged comments from Python files'
    )
    parser.add_argument(
        'path',
        help='Python file or directory to process'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Process directories recursively'
    )
    parser.add_argument(
        '--output', '-o',
        choices=['summary', 'json', 'dict'],
        default='summary',
        help='Output format'
    )
    parser.add_argument(
        '--tags',
        nargs='+',
        help='Specific tags to extract (default: all supported)'
    )

    args = parser.parse_args()

    path = Path(args.path)
    extractor = CommentExtractor(tag_list=args.tags)

    if path.is_file():
        result = extractor.extract_from_file(path)

        if args.output == 'json':
            print(json.dumps(result.to_dict(), indent=2))
        elif args.output == 'dict':
            print(result.to_dict())
        else:
            print_extraction_summary(result)

    elif path.is_dir():
        results = extractor.extract_from_directory(
            path,
            recursive=args.recursive
        )

        if args.output == 'json':
            output = {
                path: result.to_dict()
                for path, result in results.items()
            }
            print(json.dumps(output, indent=2))
        elif args.output == 'dict':
            output = {
                path: result.to_dict()
                for path, result in results.items()
            }
            print(output)
        else:
            print(f"\nProcessed {len(results)} file(s)\n")
            for file_path, result in results.items():
                print_extraction_summary(result)

    else:
        print(f"Error: {path} is not a valid file or directory")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
