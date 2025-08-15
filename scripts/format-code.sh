#!/bin/bash
# Code formatting script for MiniCRM

set -e

echo "🎨 Formatting MiniCRM code..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# 1. Format code with Ruff
print_status "Formatting Python code with Ruff..."
uv run ruff format src/ tests/
print_success "Code formatting complete"

# 2. Fix import sorting
print_status "Sorting imports..."
uv run ruff check --select I --fix src/ tests/
print_success "Import sorting complete"

# 3. Auto-fix other Ruff issues
print_status "Auto-fixing Ruff issues..."
uv run ruff check --fix src/ tests/
print_success "Auto-fix complete"

# 4. Format docstrings
print_status "Formatting docstrings..."
uv run docformatter --in-place --recursive src/
print_success "Docstring formatting complete"

# 5. Format configuration files
print_status "Formatting configuration files..."

# Format YAML files
if command -v prettier &> /dev/null; then
    prettier --write "*.yaml" "*.yml" ".github/**/*.yaml" ".github/**/*.yml" 2>/dev/null || true
fi

# Format JSON files
if command -v prettier &> /dev/null; then
    prettier --write "*.json" ".vscode/*.json" 2>/dev/null || true
fi

print_success "Configuration file formatting complete"

echo ""
print_success "All formatting complete! ✨"
echo ""
echo "Next steps:"
echo "1. Review the changes: git diff"
echo "2. Run quality checks: ./scripts/check-code.sh"
echo "3. Commit your changes: git add . && git commit"
