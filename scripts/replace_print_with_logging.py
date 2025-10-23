#!/usr/bin/env python3
"""
Replace print() statements with proper logging in production code.

This script:
1. Scans Python files for print() statements
2. Adds logger import if not present
3. Replaces print() with appropriate logger calls
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple


def has_logger_import(content: str) -> bool:
    """Check if file already has logger import"""
    return bool(re.search(r'from api\.logging_config import get_logger', content))


def add_logger_import(content: str) -> str:
    """Add logger import after other imports"""
    # Find the last import statement
    import_pattern = r'^(from .* import .*|import .*)'
    matches = list(re.finditer(import_pattern, content, re.MULTILINE))

    if not matches:
        # No imports found, add at top after docstring
        if content.startswith('"""') or content.startswith("'''"):
            # Find end of docstring
            quote = '"""' if content.startswith('"""') else "'''"
            end = content.find(quote, len(quote))
            if end != -1:
                insertion_point = end + len(quote)
                return content[:insertion_point] + '\n\nfrom api.logging_config import get_logger\n\nlogger = get_logger(__name__)\n' + content[insertion_point:]
        # Fallback: add at very top
        return 'from api.logging_config import get_logger\n\nlogger = get_logger(__name__)\n\n' + content

    # Add after last import
    last_import = matches[-1]
    insertion_point = last_import.end()

    # Add logger import and instance
    logger_code = '\nfrom api.logging_config import get_logger\n\nlogger = get_logger(__name__)'

    return content[:insertion_point] + logger_code + content[insertion_point:]


def replace_print_statements(content: str) -> Tuple[str, int]:
    """Replace print() statements with logger calls"""
    replacements = 0

    # Pattern: print(f"✅ ...") or print("✅ ...") → logger.info()
    # Pattern: print(f"⚠️  ...") or print("⚠️  ...") → logger.warning()
    # Pattern: print(f"❌ ...") or print("❌ ...") → logger.error()
    # Pattern: print(f"🎨 ...") or print(f"ℹ️  ...") → logger.info()
    # Pattern: print(f"[BGG] ...") → logger.info()
    # Pattern: print(f"Error ...") or print("Error ...") → logger.error()

    lines = content.split('\n')
    new_lines = []

    for line in lines:
        # Skip commented lines
        if line.strip().startswith('#'):
            new_lines.append(line)
            continue

        # Match print statements
        print_match = re.match(r'^(\s*)print\((.*)\)\s*$', line)
        if print_match:
            indent = print_match.group(1)
            args = print_match.group(2)

            # Determine log level based on emoji/content
            if any(emoji in args for emoji in ['✅', '🎨', 'ℹ️', '[BGG]', 'Found', 'Created', 'Updated', 'Deleted', 'Generated', 'Queued']):
                log_method = 'info'
            elif any(emoji in args for emoji in ['⚠️', 'Failed', 'Warning']):
                log_method = 'warning'
            elif any(word in args for word in ['Error', '❌', 'failed']):
                log_method = 'error'
            else:
                # Default to info for neutral messages
                log_method = 'info'

            # Remove emoji prefixes for cleaner logs (logging will add structure)
            args = re.sub(r'[✅⚠️❌🎨ℹ️⭐]\s*', '', args)

            new_line = f'{indent}logger.{log_method}({args})'
            new_lines.append(new_line)
            replacements += 1
        else:
            new_lines.append(line)

    return '\n'.join(new_lines), replacements


def process_file(file_path: Path, dry_run: bool = False) -> Tuple[bool, int]:
    """Process a single file"""
    try:
        content = file_path.read_text()

        # Skip files that don't have print statements
        if not re.search(r'^[^#]*print\(', content, re.MULTILINE):
            return False, 0

        # Add logger import if needed
        if not has_logger_import(content):
            content = add_logger_import(content)

        # Replace print statements
        new_content, replacements = replace_print_statements(content)

        if replacements > 0:
            if not dry_run:
                file_path.write_text(new_content)
            print(f"{'[DRY RUN] ' if dry_run else ''}✅ {file_path}: {replacements} print statements replaced")
            return True, replacements

        return False, 0

    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}")
        return False, 0


def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description='Replace print statements with logging')
    parser.add_argument('paths', nargs='+', help='Directories or files to process')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without modifying files')
    parser.add_argument('--exclude', nargs='*', default=['tests/', 'examples/', 'scripts/'],
                       help='Directories to exclude')
    args = parser.parse_args()

    total_files = 0
    total_replacements = 0

    for path_str in args.paths:
        path = Path(path_str)

        if path.is_file():
            if path.suffix == '.py':
                modified, count = process_file(path, args.dry_run)
                if modified:
                    total_files += 1
                    total_replacements += count
        elif path.is_dir():
            for py_file in path.rglob('*.py'):
                # Skip excluded directories
                if any(excluded in str(py_file) for excluded in args.exclude):
                    continue

                modified, count = process_file(py_file, args.dry_run)
                if modified:
                    total_files += 1
                    total_replacements += count

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Summary:")
    print(f"  Files modified: {total_files}")
    print(f"  Print statements replaced: {total_replacements}")

    if args.dry_run:
        print("\nRun without --dry-run to apply changes")


if __name__ == '__main__':
    main()
