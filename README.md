# MiniCRM

A modern, modular CRM system built with Python and Qt, featuring automated code quality checks and a reusable function library.

## ✨ Features

- **Modern Qt Interface**: Built with PySide6 for native cross-platform experience
- **Modular Architecture**: Clean separation of concerns with transfunctions library
- **Automated Quality Checks**: Comprehensive linting, formatting, and testing
- **Type Safety**: Full type annotations with mypy checking
- **Comprehensive Testing**: Unit tests with coverage reporting
- **Developer Friendly**: Pre-commit hooks and automated formatting

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd minicrm

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Setup development environment
./scripts/setup-dev.sh

# Activate virtual environment
source .venv/bin/activate

# Run the application
uv run python -m minicrm
```

## 🛠️ Development

### Code Quality Tools

This project uses a comprehensive set of modern Python tools:

- **[Ruff](https://github.com/astral-sh/ruff)**: Fast linting and formatting
- **[MyPy](https://mypy.readthedocs.io/)**: Static type checking
- **[Pytest](https://pytest.org/)**: Testing framework with coverage
- **[Pre-commit](https://pre-commit.com/)**: Git hooks for quality assurance

### Development Commands

```bash
# Format code
./scripts/format-code.sh

# Run quality checks (开发阶段推荐宽松模式)
RELAXED_MODE=true ./scripts/check-code.sh

# Run quality checks (标准模式)
./scripts/check-code.sh

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src --cov-report=html

# Type checking (可选，开发阶段)
uv run mypy src/

# Linting (宽松模式，开发阶段推荐)
uv run ruff check src/ --config ruff.toml

# Linting (标准模式)
uv run ruff check src/

# Auto-fix linting issues
uv run ruff check src/ --fix
```

### Using Make (Optional)

```bash
# See all available commands
make help

# Install development dependencies
make dev-install

# Run quality checks (宽松模式 - 开发阶段推荐)
make check-relaxed

# Run quality checks (标准模式 - 提交前使用)
make check

# Format code
make format

# Run tests
make test

# Linting (宽松模式)
make lint-relaxed

# Linting (标准模式)
make lint
```

## 📁 Project Structure

```
minicrm/
├── src/
│   ├── minicrm/          # Main application code
│   │   ├── ui/           # Qt user interface components
│   │   ├── services/     # Business logic layer
│   │   ├── data/         # Data access layer
│   │   └── models/       # Data models
│   └── transfunctions/   # Reusable function library
│       ├── business_validation.py
│       ├── data_formatting.py
│       ├── business_calculations.py
│       └── crud_templates.py
├── tests/                # Test suite
├── docs/                 # Documentation
├── scripts/              # Development scripts
├── .vscode/              # VS Code configuration
└── .github/              # GitHub Actions workflows
```

## 🧪 Testing

The project includes comprehensive testing with pytest:

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src

# Run specific test categories
uv run pytest -m unit          # Unit tests only
uv run pytest -m integration   # Integration tests only
uv run pytest -m "not slow"    # Skip slow tests
```

## 📊 Code Quality

### Quality Metrics

- **Test Coverage**: Minimum 80%
- **Type Coverage**: 100% with mypy
- **Documentation Coverage**: Minimum 80%
- **Code Complexity**: Monitored with ruff

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality:

- Code formatting with Ruff
- Import sorting
- Type checking with MyPy
- Security scanning with Bandit
- Documentation formatting

## 🏗️ Architecture

### 🔧 Modular Development Standards

This project enforces strict modularity standards from day one to prevent technical debt:

#### File Size Control
- **Hard Limit**: 200 lines per Python file
- **Warning Threshold**: 150 lines (consider refactoring)
- **Function Limit**: 50 lines maximum
- **Class Limit**: 100 lines maximum

#### Transfunctions Mandatory Usage
- **Check First**: Always check transfunctions before implementing new functionality
- **No Duplication**: Forbidden to reimplement existing transfunctions
- **Extend Library**: Add new common functions to transfunctions for reuse

#### Layered Architecture Constraints
```
UI Layer (ui/)
├── Can import: services, models, core, transfunctions
└── Cannot import: data

Business Logic Layer (services/)
├── Can import: data, models, core, transfunctions
└── Cannot import: ui

Data Access Layer (data/)
├── Can import: models, core, transfunctions
└── Cannot import: ui, services

Data Model Layer (models/)
├── Can import: core, transfunctions
└── Cannot import: ui, services, data

Core Utilities (core/)
├── Can import: none
└── Cannot import: all business layers

Reusable Functions (transfunctions/)
├── Can import: none
└── Cannot import: minicrm modules
```

#### Quality Enforcement Tools

```bash
# Check modularity compliance
python scripts/modularity_check.py --all

# Check specific file
python scripts/modularity_check.py src/minicrm/services/customer_service.py

# Git pre-commit hook automatically runs checks
git commit -m "your changes"  # Will run modularity checks
```

### Transfunctions Library

The `transfunctions` library provides reusable functions across the application:

- **Business Validation**: Data validation functions
- **Data Formatting**: Consistent data display formatting
- **Business Calculations**: Common business logic calculations
- **CRUD Templates**: Standardized database operations
- **Search Templates**: Reusable search functionality

### Modular Design

- **File Size Limit**: Maximum 200 lines per file (warning at 150)
- **Single Responsibility**: Each module has a clear, focused purpose
- **Dependency Injection**: Loose coupling between components
- **Type Safety**: Full type annotations throughout

## 🔧 Configuration

### VS Code Setup

The project includes VS Code configuration for optimal development experience:

- Automatic code formatting on save
- Integrated linting and type checking
- Test discovery and running
- Recommended extensions

### Environment Variables

```bash
# Development
PYTHONPATH=./src
MINICRM_ENV=development

# Testing
MINICRM_TEST_DB=:memory:
```

## 📈 Continuous Integration

GitHub Actions workflow includes:

- Multi-platform testing (Ubuntu, Windows, macOS)
- Multiple Python versions (3.11, 3.12)
- Code quality checks
- Security scanning
- Coverage reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run quality checks: `./scripts/check-code.sh`
5. Commit your changes (pre-commit hooks will run)
6. Push to your fork
7. Create a pull request

### Code Style

- Follow PEP 8 (enforced by Ruff)
- Use type annotations
- Write docstrings for all public functions
- Keep functions under 50 lines
- Keep files under 200 lines

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython/) for the Qt interface
- Code quality powered by [Ruff](https://github.com/astral-sh/ruff)
- Package management with [uv](https://github.com/astral-sh/uv)
- Testing with [Pytest](https://pytest.org/)

---

**Happy coding!** 🎉
