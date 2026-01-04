# Contributing to HP12C Calculator

Thank you for your interest in contributing to the HP12C Calculator project! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/hp12c.git
   cd hp12c
   ```
3. **Set up development environment**:
   ```bash
   pip install -e ".[dev]"
   pre-commit install
   ```

## Development Workflow

1. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes** following the code style guidelines

3. **Write or update tests** for your changes

4. **Run tests and checks**:
   ```bash
   make check-all  # Runs lint, type-check, and tests
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Description of your changes"
   ```
   Note: Pre-commit hooks will automatically run linting and formatting

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## Code Style

- Follow **PEP 8** style guide
- Use **type hints** for all function signatures
- Write **docstrings** for all public methods and classes (Google style)
- Maximum line length: **100 characters**
- Use `ruff` for linting and formatting (configured in `ruff.toml`)

### Running Code Quality Checks

```bash
make lint        # Check code style
make format      # Auto-format code
make type-check  # Type checking with mypy
make test        # Run tests
make check-all   # Run all checks
```

## Testing

- Write **unit tests** for all new functionality
- Test **error handling** and edge cases
- Maintain **test coverage** above 80% for core calculator logic
- Use **descriptive test names** that explain what is being tested
- Group related tests in **test classes**

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
pytest tests/unit/test_calculator.py

# Run with verbose output
pytest tests/ -v
```

## Pull Request Guidelines

- **Keep PRs focused** - one feature or bug fix per PR
- **Write clear commit messages** - explain what and why
- **Update documentation** if needed (README, docstrings)
- **Add tests** for new features
- **Ensure all checks pass** before requesting review
- **Reference issues** if your PR fixes one: "Fixes #123"

## Project Structure

- `hp12c/calculator/` - Core calculator engine
- `hp12c/model/` - Data models (stack, display, memory, etc.)
- `hp12c/ui/` - UI framework implementations
- `hp12c/persistence/` - Configuration and memory persistence
- `hp12c/utils/` - Utility functions
- `tests/` - Test suite

## Questions?

If you have questions or need help, please:
- Open an issue on GitHub
- Check existing issues and discussions
- Review the README.md for project documentation

Thank you for contributing! 🎉
