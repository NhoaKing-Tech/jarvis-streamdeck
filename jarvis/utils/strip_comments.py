#!/usr/bin/env python3
"""
Comment Stripping Tool for Clean Production Code
================================================

AUTHOR: NhoaKing
PROJECT: jarvis-streamdeck
PURPOSE: Strip tagged comments from Python files to create clean production code

DESCRIPTION:
This script removes comments with special tags (#EDU, #NOTE, #TOCLEAN, etc.)
from Python source files while preserving regular comments and code structure.

USAGE:
    python strip_comments.py <source_file> [--output output_file]
    python strip_comments.py jarvis/actions/actions.py --output jarvis_clean/actions/actions.py
    python strip_comments.py jarvis/ --output-dir jarvis_clean/ --recursive

KEY FEATURES:
- Removes only tagged comments (preserves regular comments)
- Maintains code structure and indentation
- Preserves docstrings and regular inline comments
- Can process individual files or entire directories
- Dry-run mode for testing
"""

import re
from pathlib import Path
from typing import List, Optional, Set
import shutil


# Default tags to strip from production code
DEFAULT_STRIP_TAGS = [
    'EDU',      # Educational content - too verbose for production
    'NOTE',     # Implementation notes - internal use only
    'TOCLEAN',  # Temporary notes - definitely remove
    'FIXME',    # Issues should be fixed before production
    'TODO',     # Remove TODO markers from production
    'HACK',     # Don't advertise workarounds
    'DEBUG',    # Debug comments should not be in production
    'REVIEW',   # Review comments are for development
]

# Tags to keep in production (if any)
KEEP_TAGS = [
    'IMPORTANT',  # Critical information should stay
    'OPTIMIZE',   # Performance notes are useful
]


class CommentStripper:
    """Strip tagged comments from Python source files."""

    def __init__(
        self,
        strip_tags: Optional[List[str]] = None,
        keep_tags: Optional[List[str]] = None
    ):
        """
        Initialize the comment stripper.

        Args:
            strip_tags: List of tags to remove. If None, uses DEFAULT_STRIP_TAGS.
            keep_tags: List of tags to keep. If None, uses KEEP_TAGS.
        """
        self.strip_tags = set(strip_tags or DEFAULT_STRIP_TAGS)
        self.keep_tags = set(keep_tags or KEEP_TAGS)

        # Create regex pattern to match tagged comments
        # Matches: # TAG: content or #TAG content or # TAG content
        tag_pattern = '|'.join(self.strip_tags)
        self.tag_regex = re.compile(
            rf'^\s*#\s*({tag_pattern})[\s:]*.*$',
            re.IGNORECASE
        )

    def strip_file(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        dry_run: bool = False
    ) -> dict:
        """
        Strip tagged comments from a Python file.

        Args:
            input_path: Path to input Python file
            output_path: Path for output file (None = overwrite input)
            dry_run: If True, don't write output, just report changes

        Returns:
            Dictionary with statistics about stripping operation
        """
        input_path = Path(input_path)

        if not input_path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")

        with open(input_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        stripped_lines = []
        lines_removed = 0
        in_tagged_block = False
        blocks_removed = 0
        current_block_start = None

        for line_num, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Check if this is a tagged comment line
            if self.tag_regex.match(line):
                if not in_tagged_block:
                    in_tagged_block = True
                    current_block_start = line_num
                    blocks_removed += 1
                lines_removed += 1
                continue  # Skip this line

            # Check if we're continuing a tagged comment block
            elif in_tagged_block and stripped.startswith('#'):
                # Check if it's a continuation (no new tag)
                # If it starts with # but doesn't match any tag pattern, it's a continuation
                is_new_tag = False
                for tag in (self.strip_tags | self.keep_tags):
                    if re.match(rf'^\s*#\s*{tag}[\s:]*', line, re.IGNORECASE):
                        is_new_tag = True
                        break

                if not is_new_tag:
                    # It's a continuation of the tagged block
                    lines_removed += 1
                    continue
                else:
                    # It's a new tag, check if we should strip it
                    in_tagged_block = False
                    if self.tag_regex.match(line):
                        in_tagged_block = True
                        current_block_start = line_num
                        blocks_removed += 1
                        lines_removed += 1
                        continue

            else:
                # Not a tagged comment
                in_tagged_block = False
                stripped_lines.append(line)

        # Write output if not dry run
        if not dry_run:
            output_path = output_path or input_path
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.writelines(stripped_lines)

        return {
            'input_path': str(input_path),
            'output_path': str(output_path) if output_path else str(input_path),
            'original_lines': len(lines),
            'output_lines': len(stripped_lines),
            'lines_removed': lines_removed,
            'blocks_removed': blocks_removed,
            'reduction_percent': (lines_removed / len(lines) * 100) if lines else 0
        }

    def strip_directory(
        self,
        input_dir: Path,
        output_dir: Optional[Path] = None,
        recursive: bool = True,
        pattern: str = "*.py",
        dry_run: bool = False,
        preserve_structure: bool = True
    ) -> dict:
        """
        Strip tagged comments from all Python files in a directory.

        Args:
            input_dir: Path to input directory
            output_dir: Path to output directory (None = in-place)
            recursive: Whether to process subdirectories
            pattern: File pattern to match
            dry_run: If True, don't write files, just report
            preserve_structure: Keep directory structure in output

        Returns:
            Dictionary with overall statistics
        """
        input_dir = Path(input_dir)
        output_dir = Path(output_dir) if output_dir else input_dir

        results = []
        total_files = 0
        total_lines_removed = 0

        if recursive:
            files = input_dir.rglob(pattern)
        else:
            files = input_dir.glob(pattern)

        for file_path in files:
            if file_path.is_file():
                total_files += 1

                # Determine output path
                if preserve_structure and output_dir != input_dir:
                    # Preserve directory structure
                    relative_path = file_path.relative_to(input_dir)
                    out_path = output_dir / relative_path
                elif output_dir != input_dir:
                    # Flat structure
                    out_path = output_dir / file_path.name
                else:
                    # In-place
                    out_path = file_path

                try:
                    result = self.strip_file(file_path, out_path, dry_run)
                    results.append(result)
                    total_lines_removed += result['lines_removed']
                except Exception as e:
                    print(f"Warning: Could not process {file_path}: {e}")

        return {
            'input_directory': str(input_dir),
            'output_directory': str(output_dir),
            'files_processed': total_files,
            'total_lines_removed': total_lines_removed,
            'file_results': results
        }


def print_stripping_summary(result: dict) -> None:
    """Print a human-readable summary of stripping operation."""
    if 'file_results' in result:
        # Directory operation
        print(f"\n{'='*70}")
        print(f"Directory Stripping Summary")
        print(f"{'='*70}")
        print(f"Input: {result['input_directory']}")
        print(f"Output: {result['output_directory']}")
        print(f"Files processed: {result['files_processed']}")
        print(f"Total lines removed: {result['total_lines_removed']}")
        print()

        if result['file_results']:
            print("Per-file breakdown:")
            for file_result in result['file_results']:
                if file_result['lines_removed'] > 0:
                    print(f"  {file_result['input_path']}:")
                    print(f"    Lines: {file_result['original_lines']} → {file_result['output_lines']}")
                    print(f"    Removed: {file_result['lines_removed']} lines "
                          f"({file_result['reduction_percent']:.1f}%)")
                    print(f"    Blocks removed: {file_result['blocks_removed']}")
    else:
        # Single file operation
        print(f"\n{'='*70}")
        print(f"File Stripping Summary")
        print(f"{'='*70}")
        print(f"Input: {result['input_path']}")
        print(f"Output: {result['output_path']}")
        print(f"Original lines: {result['original_lines']}")
        print(f"Output lines: {result['output_lines']}")
        print(f"Lines removed: {result['lines_removed']}")
        print(f"Blocks removed: {result['blocks_removed']}")
        print(f"Reduction: {result['reduction_percent']:.1f}%")


def create_clean_copy(
    source_dir: Path,
    dest_dir: Path,
    stripper: CommentStripper
) -> None:
    """
    Create a complete clean copy of the codebase.

    This function:
    1. Copies entire directory structure
    2. Strips tagged comments from Python files
    3. Copies all other files as-is

    Args:
        source_dir: Source directory (e.g., jarvis/)
        dest_dir: Destination directory (e.g., jarvis_clean/)
        stripper: CommentStripper instance to use
    """
    source_dir = Path(source_dir)
    dest_dir = Path(dest_dir)

    print(f"Creating clean copy: {source_dir} → {dest_dir}")

    # Remove destination if it exists
    if dest_dir.exists():
        shutil.rmtree(dest_dir)

    # Copy entire directory structure
    shutil.copytree(source_dir, dest_dir)

    # Strip comments from Python files
    result = stripper.strip_directory(
        dest_dir,  # Process in-place
        recursive=True,
        dry_run=False
    )

    print_stripping_summary(result)


def main():
    """Command-line interface for comment stripping."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Strip tagged comments from Python files'
    )
    parser.add_argument(
        'input',
        help='Python file or directory to process'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output file or directory'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Process directories recursively'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--strip-tags',
        nargs='+',
        help='Specific tags to strip (default: EDU NOTE TOCLEAN FIXME TODO HACK DEBUG REVIEW)'
    )
    parser.add_argument(
        '--keep-tags',
        nargs='+',
        help='Tags to keep (default: IMPORTANT OPTIMIZE)'
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None

    stripper = CommentStripper(
        strip_tags=args.strip_tags,
        keep_tags=args.keep_tags
    )

    if input_path.is_file():
        result = stripper.strip_file(
            input_path,
            output_path,
            dry_run=args.dry_run
        )
        print_stripping_summary(result)

    elif input_path.is_dir():
        result = stripper.strip_directory(
            input_path,
            output_path,
            recursive=args.recursive,
            dry_run=args.dry_run
        )
        print_stripping_summary(result)

    else:
        print(f"Error: {input_path} is not a valid file or directory")
        return 1

    if args.dry_run:
        print("\n[DRY RUN] No files were modified.")

    return 0


if __name__ == '__main__':
    exit(main())
