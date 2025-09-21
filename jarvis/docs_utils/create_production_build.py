#!/usr/bin/env python3
"""
Production Build Creator for Jarvis

This script creates a clean production version of the jarvis codebase by:
1. Removing DEV:, ARCH:, EDU: comments (keeping only PROD: and regular comments)
2. Converting PROD: comments to regular comments
3. Preserving all code functionality while reducing file sizes

Usage:
    python create_production_build.py [source_dir] [target_dir]

Example:
    python create_production_build.py ../jarvis ../jarvis_prod
"""

import os
import sys
import shutil
from pathlib import Path
from annotation_system import CommentAnnotationSystem

def main():
    # Default paths
    if len(sys.argv) >= 3:
        source_dir = Path(sys.argv[1])
        target_dir = Path(sys.argv[2])
    else:
        # Default to creating production version of current jarvis
        script_dir = Path(__file__).parent
        source_dir = script_dir.parent  # jarvis directory
        target_dir = source_dir.parent / "jarvis_prod"

    print(f"📦 Creating production build...")
    print(f"   Source: {source_dir}")
    print(f"   Target: {target_dir}")

    if not source_dir.exists():
        print(f"❌ Source directory {source_dir} does not exist")
        return 1

    # Initialize the annotation system
    system = CommentAnnotationSystem()

    try:
        # Create production version
        system.create_production_version(source_dir, target_dir)

        # Calculate size reduction
        def get_dir_size(path):
            total = 0
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.py'):
                        total += os.path.getsize(os.path.join(root, file))
            return total

        original_size = get_dir_size(source_dir)
        production_size = get_dir_size(target_dir)
        reduction = ((original_size - production_size) / original_size) * 100

        print(f"📊 Build Statistics:")
        print(f"   Original size: {original_size:,} bytes")
        print(f"   Production size: {production_size:,} bytes")
        print(f"   Size reduction: {reduction:.1f}%")

        # Summary of what was kept/removed
        print(f"\n📋 Production Build Summary:")
        print(f"   ✅ Kept: PROD: comments (converted to regular #)")
        print(f"   ✅ Kept: Regular comments and all code")
        print(f"   🗑️  Removed: DEV:, ARCH:, EDU: comments")
        print(f"   📁 Production code ready at: {target_dir}")

        return 0

    except Exception as e:
        print(f"❌ Error creating production build: {e}")
        return 1

if __name__ == "__main__":
    exit(main())