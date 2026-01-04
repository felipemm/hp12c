# HP12C Calculator - Python Port

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-GPL--3.0--or--later-green)](LICENSE)

This is a Python port of the Java HP12C calculator emulator, originally decompiled from `hp12c.jar`.

## Overview

A complete HP12C financial calculator emulator with:

- RPN (Reverse Polish Notation) stack operations
- Financial calculations (TVM, NPV, IRR, bonds, depreciation, amortization)
- Program memory and execution
- General purpose memory registers
- Statistical functions
- Date calculations
- Tkinter-based GUI

## Architecture

The port maintains the Java architecture structure:

```
hp12c_python_java_port/
├── calculator/          # Core calculator engine
│   ├── calculator.py    # Main Calculator class
│   ├── key.py          # Key enumeration
│   ├── config.py       # Configuration
│   ├── exceptions.py   # CalculatorException
│   └── controller.py  # Controller (MVC)
├── model/              # Data models
│   ├── stack.py        # RPN stack
│   ├── display.py      # Display formatting
│   ├── flags.py        # Calculator flags
│   ├── finance_memory.py
│   ├── general_memory.py
│   ├── program_memory.py
│   ├── history.py
│   ├── step.py
│   └── instruction.py
├── hp12c_math/         # Math utilities
│   └── number.py       # High-precision Number class (using Decimal)
├── utils/              # Utilities
│   ├── date_utils.py
│   └── timer.py
├── persistence/        # Persistence layer
│   ├── config_dao.py   # Configuration persistence (JSON-based)
│   └── memory_dao.py   # Memory persistence (JSON-based)
├── ui/                 # Tkinter GUI
│   ├── main_window.py  # Main window
│   ├── image_button.py # Custom button
│   ├── image_panel.py  # Custom panel
│   └── text_field.py   # Display field
├── main.py             # Application entry point
├── requirements.txt
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

## Differences from Java Version

1. **Persistence**: Uses JSON instead of XML for simpler Python integration
2. **GUI**: Uses Tkinter instead of Swing
3. **Decimal**: Uses Python's `decimal.Decimal` instead of Java's `BigDecimal`
4. **Enum**: Uses Python's `enum.Enum` instead of Java enums

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
│   ├── config.py       # Configuration
│   ├── exceptions.py   # CalculatorException
│   └── controller.py  # Controller (MVC)
├── model/              # Data models
│   ├── stack.py        # RPN stack
│   ├── display.py      # Display formatting
│   ├── flags.py        # Calculator flags
│   ├── finance_memory.py
│   ├── general_memory.py
│   ├── program_memory.py
│   ├── history.py
│   ├── step.py
│   └── instruction.py
├── hp12c_math/         # Math utilities
│   └── number.py       # High-precision Number class (using Decimal)
├── utils/              # Utilities
│   ├── date_utils.py
│   ├── timer.py
│   └── logger.py       # Logging configuration
├── persistence/        # Persistence layer
│   ├── config_dao.py   # Configuration persistence (JSON-based)
│   └── memory_dao.py   # Memory persistence (JSON-based)
├── ui/                 # UI frameworks
│   ├── base_main_window.py  # Base window interface
│   ├── tkinter_main_window.py  # Tkinter implementation
│   ├── pyqt5_main_window.py    # PyQt5 implementation
│   └── ...
├── tests/              # Test suite
│   ├── unit/           # Unit tests
│   ├── integration/    # Integration tests
│   └── conftest.py     # Pytest fixtures
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
