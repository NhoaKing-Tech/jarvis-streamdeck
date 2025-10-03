#!/usr/bin/env python3
"""
Documentation Generator from Extracted Comments
===============================================

AUTHOR: NhoaKing
PROJECT: jarvis-streamdeck
PURPOSE: Generate markdown documentation from extracted code comments

DESCRIPTION:
This script converts extracted tagged comments into well-formatted markdown
documentation files suitable for static site generation (Quartz, MkDocs, etc.)

USAGE:
    python generate_docs.py <source_dir> --output <docs_dir>
    python generate_docs.py jarvis/ --output jarvis/docs/content/

KEY FEATURES:
- Converts tagged comments to structured markdown
- Groups content by tag type
- Generates table of contents
- Creates index files
- Supports Quartz frontmatter
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict
import sys

# Import our comment extractor
from extract_comments import CommentExtractor, CommentBlock, ExtractionResult


class MarkdownGenerator:
    """Generate markdown documentation from extracted comments."""

    def __init__(
        self,
        output_dir: Path,
        site_title: str = "Jarvis Documentation",
        add_frontmatter: bool = True
    ):
        """
        Initialize the markdown generator.

        Args:
            output_dir: Directory for generated markdown files
            site_title: Title for the documentation site
            add_frontmatter: Whether to add Quartz/Obsidian frontmatter
        """
        self.output_dir = Path(output_dir)
        self.site_title = site_title
        self.add_frontmatter = add_frontmatter

        # Create output directory structure
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Category mapping for different tag types
        self.tag_categories = {
            'EDU': {
                'title': '01_Learning notes',
                'description': 'Learning notes about computer science topics in general',
                'dir': 'educational'
            },
            'REVIEW': {
                'title': '02_Code Review',
                'description': 'Code sections that need review and validation',
                'dir': 'review'
            },
            'IMPORTANT': {
                'title': '03_Important Information',
                'description': 'Important information for understanding and using the system',
                'dir': 'important'
            },
            'NOTE': {
                'title': '04_Implementation Notes',
                'description': 'Important implementation details and considerations',
                'dir': 'notes'
            },
            'TOCLEAN': {
                'title': '05_Cleanup Tasks',
                'description': 'Code sections that need cleanup and refactoring',
                'dir': 'cleanup'
            },
            'FIXME': {
                'title': '06_Known Issues',
                'description': 'Known bugs and issues that need to be fixed',
                'dir': 'fixme'
            },
            'TODO': {
                'title': '07_Future Improvements',
                'description': 'Planned features and improvements for future development',
                'dir': 'todo'
            },
            'HACK': {
                'title': '08_Workarounds',
                'description': 'Temporary solutions and workarounds that need proper implementation',
                'dir': 'hack'
            },
            'DEBUG': {
                'title': '09_Debug Information',
                'description': 'Debugging aids and diagnostic information',
                'dir': 'debug'
            },
            
            'OPTIMIZE': {
                'title': '10_Performance Notes',
                'description': 'Performance considerations and optimization opportunities',
                'dir': 'performance'
            },
        }

    def generate_frontmatter(
        self,
        title: str,
        tags: Optional[List[str]] = None,
        description: Optional[str] = None
    ) -> str:
        """
        Generate YAML frontmatter for markdown file.

        Args:
            title: Page title
            tags: List of tags
            description: Page description

        Returns:
            Formatted frontmatter string
        """
        if not self.add_frontmatter:
            return ""

        frontmatter = ["---"]
        frontmatter.append(f'title: "{title}"')

        if tags:
            frontmatter.append(f'tags: [{", ".join(tags)}]')

        if description:
            frontmatter.append(f'description: "{description}"')

        frontmatter.append(f'date: {datetime.now().strftime("%Y-%m-%d")}')
        frontmatter.append("---")
        frontmatter.append("")

        return "\n".join(frontmatter)

    def generate_doc_for_tag(
        self,
        tag: str,
        blocks: List[CommentBlock],
        source_file: str
    ) -> str:
        """
        Generate markdown content for a specific tag from one file.

        Args:
            tag: The tag type (EDU, NOTE, etc.)
            blocks: List of comment blocks for this tag
            source_file: Source file path

        Returns:
            Markdown content
        """
        category = self.tag_categories.get(tag, {
            'title': tag,
            'description': f'{tag} comments',
            'dir': tag.lower()
        })

        # Create title from source file
        file_path = Path(source_file)
        file_title = file_path.stem.replace('_', ' ').title()

        content = []

        # Add frontmatter
        content.append(self.generate_frontmatter(
            title=f"{category['title']}: {file_title}",
            tags=[tag.lower(), 'auto-generated'],
            description=f"{category['title']} from {file_path.name}"
        ))

        # Add header
        content.append(f"# {category['title']}: {file_title}")
        content.append("")
        content.append(f"**Source File**: `{source_file}`")
        content.append("")
        content.append(f"**Category**: {category['description']}")
        content.append("")
        content.append("---")
        content.append("")

        # Group blocks by context if available
        blocks_by_context = defaultdict(list)
        for block in blocks:
            context = block.context or "General"
            blocks_by_context[context].append(block)

        # Generate content for each context
        for context, context_blocks in sorted(blocks_by_context.items()):
            if context != "General":
                content.append(f"## {context}")
                content.append("")

            for i, block in enumerate(context_blocks, 1):
                # Add anchor for linking
                anchor = f"{context.lower().replace(' ', '-')}-{i}"
                content.append(f'<a id="{anchor}"></a>')
                content.append("")

                # Add block content
                text = block.get_text()

                # Check if the content looks like it has structure
                if any(line.strip().startswith(('1.', '2.', '-', '*')) for line in text.split('\n')):
                    # Already formatted as list
                    content.append(text)
                else:
                    # Regular paragraph
                    content.append(text)

                content.append("")

                # Add source reference
                content.append(f"*[Source: {file_path.name}:{block.line_number}]*")
                content.append("")
                content.append("---")
                content.append("")

        return "\n".join(content)

    def generate_docs_from_result(
        self,
        result: ExtractionResult
    ) -> Dict[str, Path]:
        """
        Generate markdown files from extraction result.

        Args:
            result: ExtractionResult from comment extraction

        Returns:
            Dictionary mapping tag to generated file path
        """
        generated_files = {}

        for tag, blocks in result.comments_by_tag.items():
            if not blocks:
                continue

            # Get category info
            category = self.tag_categories.get(tag, {
                'title': tag,
                'description': f'{tag} comments',
                'dir': tag.lower()
            })

            # Create category directory
            category_dir = self.output_dir / category['dir']
            category_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename from source file
            source_path = Path(result.file_path)
            filename = f"{source_path.stem}.md"
            output_path = category_dir / filename

            # Generate markdown content
            markdown = self.generate_doc_for_tag(tag, blocks, result.file_path)

            # Write file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown)

            generated_files[tag] = output_path

        return generated_files

    def generate_category_index(
        self,
        tag: str,
        files: List[Path]
    ) -> Path:
        """
        Generate an index file for a category.

        Args:
            tag: Tag type
            files: List of files in this category

        Returns:
            Path to generated index file
        """
        category = self.tag_categories.get(tag, {
            'title': tag,
            'description': f'{tag} comments',
            'dir': tag.lower()
        })

        category_dir = self.output_dir / category['dir']
        index_path = category_dir / "index.md"

        content = []

        # Add frontmatter
        content.append(self.generate_frontmatter(
            title=category['title'],
            tags=[tag.lower(), 'index'],
            description=category['description']
        ))

        # Add header
        content.append(f"# {category['title']}")
        content.append("")
        content.append(category['description'])
        content.append("")
        content.append("---")
        content.append("")

        # Add list of files
        content.append("## Documentation Files")
        content.append("")

        for file_path in sorted(files):
            # Get relative path from category dir for filename
            rel_path = file_path.relative_to(category_dir)
            # Create title from filename
            title = file_path.stem.replace('_', ' ').title()
            # Use full path from content root (category/filename without .md)
            # This avoids ambiguity when multiple files have the same name
            link_path = f"{category['dir']}/{file_path.stem}"
            content.append(f"- [{title}]({link_path})")

        content.append("")

        # Write index file
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))

        return index_path

    def generate_main_index(
        self,
        files_by_category: Dict[str, List[Path]]
    ) -> Path:
        """
        Generate the main index file.

        Args:
            files_by_category: Dictionary mapping tags to file lists

        Returns:
            Path to generated index file
        """
        index_path = self.output_dir / "index.md"

        content = []

        # Add frontmatter
        content.append(self.generate_frontmatter(
            title=self.site_title,
            tags=['index', 'home'],
            description="Auto-generated documentation from code comments"
        ))

        # Add header with more descriptive title
        content.append(f"# {self.site_title} - Code Documentation")
        content.append("")
        content.append("This documentation is automatically generated from code comments.")
        content.append("")
        content.append(f"**Last Updated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        content.append("")
        content.append("---")
        content.append("")

        # Add navigation
        content.append("## Documentation Categories")
        content.append("")

        # Sort by the numbered titles in the category mapping instead of tag names
        sorted_categories = sorted(
            files_by_category.items(),
            key=lambda x: self.tag_categories.get(x[0], {'title': x[0]})['title']
        )

        for tag, files in sorted_categories:
            if not files:
                continue

            category = self.tag_categories.get(tag, {
                'title': tag,
                'description': f'{tag} comments',
                'dir': tag.lower()
            })

            content.append(f"### [{category['title']}](./{category['dir']}/)")
            content.append("")
            content.append(category['description'])
            content.append("")
            content.append(f"**{len(files)} document(s)**")
            content.append("")

        # Write index
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))

        return index_path


def generate_docs_from_directory(
    source_dir: Path,
    output_dir: Path,
    site_title: str = "Jarvis Documentation"
) -> dict:
    """
    Extract comments and generate documentation from a directory.

    Args:
        source_dir: Source code directory
        output_dir: Output directory for markdown files
        site_title: Title for documentation site

    Returns:
        Dictionary with generation statistics
    """
    # Extract comments
    print(f"Extracting comments from {source_dir}...")
    extractor = CommentExtractor()
    extraction_results = extractor.extract_from_directory(
        source_dir,
        recursive=True
    )

    if not extraction_results:
        print("No tagged comments found.")
        return {
            'files_processed': 0,
            'docs_generated': 0
        }

    print(f"Found tagged comments in {len(extraction_results)} file(s)")

    # Generate documentation
    print(f"Generating documentation in {output_dir}...")
    generator = MarkdownGenerator(output_dir, site_title)

    files_by_category = defaultdict(list)
    total_docs = 0

    for source_file, result in extraction_results.items():
        generated = generator.generate_docs_from_result(result)
        for tag, file_path in generated.items():
            files_by_category[tag].append(file_path)
            total_docs += 1

    # Generate category indices
    print("Generating category indices...")
    for tag, files in files_by_category.items():
        generator.generate_category_index(tag, files)

    # Generate main index
    print("Generating main index...")
    generator.generate_main_index(files_by_category)

    print(f"✓ Generated {total_docs} documentation file(s)")

    return {
        'files_processed': len(extraction_results),
        'docs_generated': total_docs,
        'categories': list(files_by_category.keys()),
        'output_directory': str(output_dir)
    }


def main():
    """Command-line interface for documentation generation."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate markdown documentation from code comments'
    )
    parser.add_argument(
        'source',
        help='Source directory to process'
    )
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output directory for markdown files'
    )
    parser.add_argument(
        '--title',
        default='Jarvis Documentation',
        help='Site title (default: Jarvis Documentation)'
    )
    parser.add_argument(
        '--no-frontmatter',
        action='store_true',
        help='Do not add YAML frontmatter to files'
    )

    args = parser.parse_args()

    source_dir = Path(args.source)
    output_dir = Path(args.output)

    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        return 1

    # Generate documentation
    result = generate_docs_from_directory(
        source_dir,
        output_dir,
        site_title=args.title
    )

    print("\n" + "="*70)
    print("Documentation Generation Complete")
    print("="*70)
    print(f"Files processed: {result['files_processed']}")
    print(f"Docs generated: {result['docs_generated']}")
    print(f"Categories: {', '.join(result['categories'])}")
    print(f"Output directory: {result['output_directory']}")
    print()

    return 0


if __name__ == '__main__':
    exit(main())
