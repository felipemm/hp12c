# HP12C Calculator - Python Port

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

1. Install dependencies:
```bash
pip install -r requirements.txt
```

Note: Tkinter is included with Python on most systems. On Linux, you may need to install it separately:
```bash
sudo apt-get install python3-tk  # Debian/Ubuntu
```

## Usage

Run the calculator as a Python module (recommended):
```bash
# From the parent directory (hp12c_emu)
python -m hp12c_python_java_port.main
```

Or run directly from the package directory:
```bash
# From the hp12c_python_java_port directory
python main.py
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

## Project Status

This is a comprehensive port of the Java HP12C calculator. All core functionality has been implemented:
- ✅ Core math and model layer
- ✅ Controller layer with all key handlers
- ✅ Persistence layer (JSON-based)
- ✅ Tkinter GUI
- ✅ Utilities and integration

## License

See LICENSE file in the original Java project.
