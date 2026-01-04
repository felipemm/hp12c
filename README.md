# HP12C Calculator - Python Port

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-green)](LICENSE)
[![Version](https://img.shields.io/github/v/release/felipemm/hp12c)](https://github.com/felipemm/hp12c/releases)
[![codecov](https://codecov.io/gh/felipemm/hp12c/branch/main/graph/badge.svg)](https://codecov.io/gh/felipemm/hp12c)

This is a Python port of the Java HP12C calculator emulator, originally decompiled from `hp12c.jar`.

## Overview

A complete HP12C financial calculator emulator with:

- RPN (Reverse Polish Notation) stack operations
- Financial calculations (TVM, NPV, IRR, bonds, depreciation, amortization)
- Program memory and execution
- General purpose memory registers
- Statistical functions
- Date calculations
- Dual UI framework support (Tkinter and PyQt5)
- Multiple skins/themes
- Multi-language support (English, Spanish, French, Portuguese)

## Architecture

The port maintains the Java architecture structure with a clean separation of concerns:

```
hp12c/
├── calculator/          # Core calculator engine
│   ├── calculator.py    # Main Calculator class
│   ├── key.py          # Key enumeration
│   ├── config.py       # Configuration management
│   ├── exceptions.py   # CalculatorException
│   └── controller.py   # Controller (MVC pattern)
├── model/              # Data models
│   ├── stack.py        # RPN stack implementation
│   ├── display.py      # Display formatting
│   ├── flags.py        # Calculator flags
│   ├── finance_memory.py  # Financial memory (TVM variables)
│   ├── general_memory.py # General purpose registers
│   ├── program_memory.py  # Program memory (1000 steps)
│   ├── history.py      # Operation history
│   ├── step.py         # Program step representation
│   └── instruction.py  # Instruction representation
├── hp12c_math/         # Math utilities
│   └── number.py       # High-precision Number class (using Decimal)
├── utils/              # Utilities
│   ├── date.py         # Date class for date operations
│   ├── date_utils.py   # Date utility functions
│   ├── language_loader.py  # Multi-language support
│   ├── skin_loader.py   # Skin/theme loader
│   ├── logger.py       # Logging configuration
│   └── timer.py        # Timer utilities
├── persistence/        # Persistence layer
│   ├── config_dao.py   # Configuration persistence (JSON-based)
│   └── memory_dao.py    # Memory persistence (JSON-based)
├── ui/                 # UI frameworks
│   ├── base_main_window.py      # Abstract base class
│   ├── tkinter_main_window.py   # Tkinter implementation
│   ├── pyqt5_main_window.py     # PyQt5 implementation
│   ├── main_window.py            # Legacy main window (Tkinter)
│   ├── image_button.py           # Custom image button (Tkinter)
│   ├── pyqt5_image_button.py     # Custom image button (PyQt5)
│   ├── image_panel.py            # Image panel (Tkinter)
│   ├── pyqt5_image_panel.py      # Image panel (PyQt5)
│   ├── text_field.py             # Display text field
│   ├── register_view_tkinter.py  # Register view (Tkinter)
│   ├── register_view_pyqt5.py    # Register view (PyQt5)
│   └── history_view_tkinter.py   # History view (Tkinter)
├── resources/          # Resources
│   ├── data/           # Default configuration and memory
│   ├── langs/          # Language files (en, es, fr, pt)
│   └── skins/          # Skin themes (argentum, aurum, nigrum)
├── tests/              # Test suite
│   ├── unit/           # Unit tests
│   └── integration/   # Integration tests
├── main.py             # Application entry point
├── pyproject.toml       # Project configuration
└── README.md
```

## Installation

### Requirements

- Python 3.10 or higher
- Pillow >= 10.0.0 (for image handling)
- PyQt5 >= 5.15.0 (optional, for PyQt5 UI framework)
- Tkinter (usually included with Python)

### Basic Installation

1. Install dependencies:

```bash
pip install -r requirements.txt
```

Or install with optional PyQt5 support:

```bash
pip install -r requirements.txt
pip install pyqt5  # Optional: for PyQt5 UI framework
```

Note: Tkinter is included with Python on most systems. On Linux, you may need to install it separately:

```bash
sudo apt-get install python3-tk  # Debian/Ubuntu
```

### Development Installation

For development, install with dev dependencies:

```bash
pip install -e ".[dev]"
```

Or using uv:

```bash
uv pip install -e ".[dev]"
```

## Usage

### Running the Application

Run the calculator as a Python module (recommended):

```bash
python main.py
```

Or using the Makefile:

```bash
make run
```

The calculator will automatically select the best available UI framework (Tkinter or PyQt5) based on what's installed and your configuration.

### Building Distributables

Build for your current platform:

```bash
make build
```

Build for specific platforms:

```bash
make build-macos    # macOS .app bundle
make build-windows  # Windows .exe
make build-linux    # Linux executable
```

## Key Features

### Core Math

- High-precision arithmetic using Python's `decimal.Decimal`
- All standard mathematical functions (sin, cos, tan, log, exp, sqrt, etc.)
- Factorial, power, reciprocal operations

### RPN Stack

- 4-level stack (X, Y, Z, T registers)
- Stack operations: shift, roll, swap
- LAST X register support

### Financial Calculations

- Time Value of Money (TVM): N, I, PV, PMT, FV
- Net Present Value (NPV)
- Internal Rate of Return (IRR)
- Bond calculations
- Depreciation methods (SL, SOYD, DB)
- Amortization

### Memory

- General purpose registers (R0-R9, etc.)
- Financial memory (TVM variables)
- Program memory (1000 steps)
- Operation history

### Statistics

- Mean, weighted mean
- Standard deviation
- Linear regression (x and y estimation)
- Correlation coefficient

### Date Operations

- Date arithmetic
- Day of week calculation
- 360-day and 365-day year calculations

### UI Features

- Dual framework support: Tkinter (default) and PyQt5
- Multiple skins/themes: Argentum, Aurum, and Nigrum
- Multi-language support: English, Spanish, French, Portuguese
- Register view window for inspecting memory registers
- History view for operation history
- Customizable display and button layouts

## Differences from Java Version

1. **Persistence**: Uses JSON instead of XML for runtime data (XML still used for resources)
2. **GUI**: Supports both Tkinter and PyQt5 (with automatic framework selection)
3. **Decimal**: Uses Python's `decimal.Decimal` instead of Java's `BigDecimal`
4. **Enum**: Uses Python's `enum.Enum` instead of Java enums
5. **Architecture**: Maintains MVC pattern with abstract base classes for UI frameworks

## Development

### Setting Up Development Environment

1. Clone the repository
2. Install development dependencies:

   ```bash
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks (recommended):

   ```bash
   pre-commit install
   ```

   This will automatically run linting and formatting checks before each commit.

### Running Tests

Run all tests:

```bash
make test
# or
pytest tests/
```

Run tests with coverage:

```bash
make test-cov
# or
pytest --cov=hp12c --cov-report=html tests/
```

Coverage report will be generated in `htmlcov/index.html`.

### Code Quality

Lint code:

```bash
make lint
# or
ruff check hp12c/ tests/ main.py
```

Format code:

```bash
make format
# or
ruff format hp12c/ tests/ main.py
```

Type checking:

```bash
make type-check
# or
mypy hp12c/ main.py
```

Run all checks:

```bash
make check-all
```

### Project Structure

```
hp12c/
├── calculator/          # Core calculator engine
│   ├── calculator.py    # Main Calculator class
│   ├── key.py          # Key enumeration
│   ├── config.py       # Configuration management
│   ├── exceptions.py   # CalculatorException
│   └── controller.py   # Controller (MVC pattern)
├── model/              # Data models
│   ├── stack.py        # RPN stack implementation
│   ├── display.py      # Display formatting
│   ├── flags.py        # Calculator flags
│   ├── finance_memory.py  # Financial memory (TVM variables)
│   ├── general_memory.py # General purpose registers
│   ├── program_memory.py  # Program memory (1000 steps)
│   ├── history.py      # Operation history
│   ├── step.py         # Program step representation
│   └── instruction.py  # Instruction representation
├── hp12c_math/         # Math utilities
│   └── number.py       # High-precision Number class (using Decimal)
├── utils/              # Utilities
│   ├── date.py         # Date class for date operations
│   ├── date_utils.py   # Date utility functions
│   ├── language_loader.py  # Multi-language support
│   ├── skin_loader.py   # Skin/theme loader
│   ├── logger.py       # Logging configuration
│   └── timer.py        # Timer utilities
├── persistence/        # Persistence layer
│   ├── config_dao.py   # Configuration persistence (JSON-based)
│   └── memory_dao.py    # Memory persistence (JSON-based)
├── ui/                 # UI frameworks
│   ├── base_main_window.py      # Abstract base class
│   ├── tkinter_main_window.py   # Tkinter implementation
│   ├── pyqt5_main_window.py     # PyQt5 implementation
│   ├── main_window.py            # Legacy main window (Tkinter)
│   ├── image_button.py           # Custom image button (Tkinter)
│   ├── pyqt5_image_button.py     # Custom image button (PyQt5)
│   ├── image_panel.py            # Image panel (Tkinter)
│   ├── pyqt5_image_panel.py      # Image panel (PyQt5)
│   ├── text_field.py             # Display text field
│   ├── register_view_tkinter.py   # Register view (Tkinter)
│   ├── register_view_pyqt5.py     # Register view (PyQt5)
│   └── history_view_tkinter.py    # History view (Tkinter)
├── resources/          # Resources
│   ├── data/           # Default configuration and memory (XML)
│   ├── langs/          # Language files (en.xml, es.xml, fr.xml, pt.xml)
│   └── skins/          # Skin themes (argentum, aurum, nigrum)
├── tests/              # Test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── conftest.py     # Pytest fixtures
├── scripts/            # Utility scripts
│   └── bump_version.py  # Version bumping script
├── main.py             # Application entry point
├── pyproject.toml      # Project configuration
├── ruff.toml           # Ruff linting configuration
├── mypy.ini            # MyPy type checking configuration
└── Makefile            # Build and development commands
```

### Testing Guidelines

- Write unit tests for all calculator operations
- Test error handling and edge cases
- Maintain test coverage above 80% for core calculator logic
- Use descriptive test names that explain what is being tested
- Group related tests in test classes

### Code Style

- Follow PEP 8 style guide
- Use type hints for all function signatures
- Write docstrings for all public methods and classes
- Use Google-style docstrings
- Maximum line length: 100 characters
- Use `ruff` for linting and formatting

### Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

Quick start:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests
5. Ensure all tests pass (`make test`)
6. Run linting and type checking (`make check-all`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Releasing

This project uses automated semantic versioning with GitHub Actions. The release process is fully automated:

### Creating a Release

1. **Update CHANGELOG.md**: Make sure all changes are documented in the `[Unreleased]` section.

2. **Bump the version**:

   ```bash
   # For a patch release (0.1.0 -> 0.1.1)
   python scripts/bump_version.py patch

   # For a minor release (0.1.0 -> 0.2.0)
   python scripts/bump_version.py minor

   # For a major release (0.1.0 -> 1.0.0)
   python scripts/bump_version.py major
   ```

   Or using the Makefile:

   ```bash
   make bump-version TYPE=patch
   ```

3. **The script will automatically**:
   - Update version in `pyproject.toml` and `hp12c/__init__.py`
   - Move `[Unreleased]` section to a versioned section in `CHANGELOG.md`
   - Create a git commit
   - Create a git tag (e.g., `v0.1.1`)
   - Push to remote (which triggers the GitHub Actions release workflow)

4. **GitHub Actions will automatically**:
   - Build the application for macOS, Windows, and Linux
   - Create a GitHub release with the changelog
   - Upload build artifacts for all platforms

### Release Artifacts

Each release includes:

- **macOS**: `hp12c.app` bundle (zip file)
- **Windows**: `hp12c.exe` executable (zip file)
- **Linux**: `hp12c` executable (zip file)

See [scripts/README.md](scripts/README.md) for more details on the version bumping script.

### Configuration

The calculator stores configuration and memory data in a data directory. The location is determined in this order:

1. Custom path provided to DAO constructors
2. `HP12C_DATA_DIR` environment variable
3. Platform-specific user data directory (if `platformdirs` is installed):
   - macOS: `~/Library/Application Support/hp12c`
   - Linux: `~/.local/share/hp12c`
   - Windows: `%APPDATA%\hp12c`
4. `data/` directory in the current working directory (fallback)

To use a custom data directory:

```bash
export HP12C_DATA_DIR=/path/to/your/data
python main.py
```

### UI Framework Selection

The calculator automatically selects the UI framework based on:

1. Configuration setting (stored in `cfg.json`)
2. Available frameworks (Tkinter is always available, PyQt5 is optional)
3. Fallback to Tkinter if PyQt5 is not available or incompatible

You can configure the preferred framework in the application settings or by editing the configuration file.

### Skins and Themes

The calculator includes three built-in skins:
- **Argentum**: Silver theme
- **Aurum**: Gold theme
- **Nigrum**: Black theme

Skins include custom button images, backgrounds, and fonts. You can switch skins through the application menu.

### Language Support

The calculator supports multiple languages:
- English (en)
- Spanish (es)
- French (fr)
- Portuguese (pt)

Language files are stored in `hp12c/resources/langs/` and can be selected through the application menu.

### Troubleshooting

**Issue: PyQt5 not available on macOS**

- Solution: The calculator will automatically fall back to Tkinter. If you want PyQt5, install it separately or use the optional dependency group.

**Issue: Tests fail with import errors**

- Solution: Make sure you've installed the package in development mode: `pip install -e .`

**Issue: Build fails with symlink errors (macOS)**

- Solution: Run `make distclean && make build` to clean previous build artifacts.

**Issue: Pre-commit hooks fail**

- Solution: Run `pre-commit run --all-files` to see what needs to be fixed, or temporarily skip hooks with `git commit --no-verify`

## Project Status

This is a comprehensive port of the Java HP12C calculator. All core functionality has been implemented:

- ✅ Core math and model layer
- ✅ Controller layer with all key handlers
- ✅ Persistence layer (JSON-based)
- ✅ Dual UI framework support (Tkinter and PyQt5)
- ✅ Utilities and integration
- ✅ Comprehensive test suite
- ✅ Logging infrastructure
- ✅ Code quality tools (linting, type checking)
- ✅ CI/CD pipeline
- ✅ Pre-commit hooks
- ✅ Developer documentation

## Additional Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) - Guidelines for contributing
- [CHANGELOG.md](CHANGELOG.md) - Project changelog

## License

This project is licensed under the GNU General Public License v3.0 or later (GPL-3.0-or-later).

See LICENSE file in the original Java project for the original license.
