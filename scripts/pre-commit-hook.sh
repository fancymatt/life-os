#!/bin/bash
# Pre-commit hook to prevent print() statements in Python files
# This codebase uses structured logging - NO print() statements allowed!
#
# Installation:
#   cp scripts/pre-commit-hook.sh .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for print() statements in staged Python files
# Exclude test files, scripts, and examples where print() might be intentional
print_files=$(git diff --cached --name-only --diff-filter=ACM | \
    grep '\.py$' | \
    grep -v '^tests/' | \
    grep -v '^examples/' | \
    grep -v '^scripts/replace_print_with_logging\.py$' | \
    xargs grep -l '^[^#]*print(' 2>/dev/null || true)

if [ -n "$print_files" ]; then
    echo -e "${RED}❌ COMMIT REJECTED: print() statements found in Python files${NC}"
    echo ""
    echo -e "${YELLOW}This codebase uses structured logging. NEVER use print() statements.${NC}"
    echo ""
    echo "Files with print() statements:"
    echo "$print_files" | sed 's/^/  - /'
    echo ""
    echo "Fix this by:"
    echo "  1. Replace print() with logger.info(), logger.warning(), or logger.error()"
    echo "  2. Add logger import: from api.logging_config import get_logger"
    echo "  3. Initialize logger: logger = get_logger(__name__)"
    echo ""
    echo "Or run the automated cleanup script:"
    echo "  python3 scripts/replace_print_with_logging.py <file>"
    echo ""
    echo "See claude.md 'Logging Standards' section for details."
    exit 1
fi

# All checks passed
exit 0
