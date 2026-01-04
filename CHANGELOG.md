# Changelog

All notable changes to the HP12C Calculator project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-01-04

### Added
- Comprehensive test suite with unit and integration tests
- Logging infrastructure replacing all print statements
- Pre-commit hooks for automated code quality checks
- CI/CD pipeline with GitHub Actions (CI and release workflows)
- Code quality tools: ruff (linting/formatting) and mypy (type checking)
- Configuration path flexibility with platformdirs support
- Environment variable support for data directory (`HP12C_DATA_DIR`)
- Enhanced README with development setup and contributing guidelines
- CONTRIBUTING.md with contribution guidelines
- Makefile targets for common development tasks
- Version bumping script (`scripts/bump_version.py`)
- EditorConfig for consistent coding style
- GitHub Actions workflows for continuous integration and releases

### Changed
- Relaxed Python version requirement from >=3.13 to >=3.10
- Made PyQt5 an optional dependency
- Improved error handling with better logging and error messages
- Enhanced type hints throughout the codebase
- Improved configuration and memory persistence error handling
- Reorganized project structure with proper package hierarchy (`hp12c/` package)
- Refactored UI components for better code organization and maintainability

### Fixed
- Removed duplicate `src/ui/__init__.py` file
- Fixed encoding issues in file I/O (now uses UTF-8)
- Improved font rendering in Tkinter UI using PIL (Pillow) for proper font display

### Improved
- Code organization and structure
- Documentation and developer experience
- Error messages and logging
- Type safety with comprehensive type hints
- Font rendering quality in Tkinter interface using PIL for better text display
- Project structure with proper package organization and module separation

## [0.1.0] - Initial Release

### Added
- Complete HP12C calculator emulator ported from Java
- RPN (Reverse Polish Notation) stack operations
- Financial calculations (TVM, NPV, IRR, bonds, depreciation, amortization)
- Program memory and execution
- General purpose memory registers
- Statistical functions
- Date calculations
- Dual UI framework support (Tkinter and PyQt5)
- Configuration and memory persistence (JSON-based)
- Multiple language support
- Multiple skin themes

[0.1.1]: https://github.com/your-username/hp12c/releases/tag/v0.1.1
[Unreleased]: https://github.com/your-username/hp12c/compare/v0.1.1...HEAD

[0.1.0]: https://github.com/your-username/hp12c/releases/tag/v0.1.0
