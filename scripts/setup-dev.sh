#!/bin/bash
# Development environment setup script for MiniCRM

set -e  # Exit on any error

echo "🚀 Setting up MiniCRM development environment..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv is installed"

# Create virtual environment and install dependencies
echo "📦 Installing dependencies..."
uv sync --dev

# Activate virtual environment for the rest of the script
source .venv/bin/activate

# Install pre-commit hooks
echo "🔧 Setting up pre-commit hooks..."
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg

# Create initial secrets baseline (if detect-secrets is configured)
if [ ! -f .secrets.baseline ]; then
    echo "🔐 Creating secrets baseline..."
    uv run detect-secrets scan --baseline .secrets.baseline
fi

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p src/minicrm
mkdir -p src/transfunctions
mkdir -p tests
mkdir -p docs
mkdir -p scripts
mkdir -p data

# Create __init__.py files
touch src/minicrm/__init__.py
touch src/transfunctions/__init__.py
touch tests/__init__.py

# Create basic README if it doesn't exist
if [ ! -f README.md ]; then
    echo "📝 Creating README.md..."
    cat > README.md << 'EOF'
# MiniCRM

A modern, modular CRM system built with Python and Qt.

## Features

- Modern Qt-based user interface
- Modular architecture with transfunctions
- Automated code quality checks
- Comprehensive testing suite

## Development Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup development environment
./scripts/setup-dev.sh

# Run the application
uv run python -m minicrm

# Run tests
uv run pytest

# Run code quality checks
./scripts/check-code.sh
```

## Project Structure

```
minicrm/
├── src/
│   ├── minicrm/          # Main application code
│   └── transfunctions/   # Reusable function library
├── tests/                # Test suite
├── docs/                 # Documentation
└── scripts/              # Development scripts
```
EOF
fi

# Run initial code quality check
echo "🔍 Running initial code quality check..."
if [ -f scripts/check-code.sh ]; then
    chmod +x scripts/check-code.sh
    ./scripts/check-code.sh || echo "⚠️  Some code quality issues found (expected for new project)"
fi

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment: source .venv/bin/activate"
echo "2. Start coding in src/minicrm/"
echo "3. Run tests with: uv run pytest"
echo "4. Check code quality with: ./scripts/check-code.sh"
echo ""
echo "Happy coding! 🎉"
