"""
High-precision Number class for HP12C calculator.
Ported from Java Number.java using Python's Decimal instead of BigDecimal.
"""

import math
from decimal import ROUND_HALF_UP, Decimal, getcontext
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


class Number:
    """High-precision number class using Decimal for calculations."""

    # Set default context precision
    _context = getcontext()
    _context.prec = 34  # DECIMAL128 equivalent

    SCALE = 10

    # Constants - will be initialized after class definition
    ZERO: "Number"
    ONE: "Number"
    TWO: "Number"
    THREE: "Number"
    FOUR: "Number"
    FIVE: "Number"
    SIX: "Number"
    SEVEN: "Number"
    EIGHT: "Number"
    NINE: "Number"
    TEN: "Number"
    TWELVE: "Number"
    HUNDRED: "Number"
    THOUSAND: "Number"
    HALF: "Number"
    THIRD: "Number"
    FORTH: "Number"
    FITH: "Number"
    TENTH: "Number"
    CENT: "Number"
    THOUSANDTH: "Number"
    PI: "Number"
    E: "Number"

    def __init__(self, value: Decimal | str | float | int = 0):
        """
        Initialize Number. Private constructor - use getInstance() instead.

        Args:
            value: Decimal, string, float, or int value
        """
        if isinstance(value, Decimal):
            self._value = value
        elif isinstance(value, str):
            try:
                self._value = Decimal(value)
            except Exception as err:
                raise ValueError("Invalid number format") from err
        elif isinstance(value, int | float):
            if math.isnan(value):
                raise ValueError("Value is not a number")
            if math.isinf(value):
                raise ValueError("Value is infinity")
            # Convert through string to avoid precision issues
            self._value = Decimal(str(value))
        else:
            raise TypeError(f"Unsupported type: {type(value)}")
            raise TypeError(f"Unsupported type: {type(value)}")

    def copy_value(self) -> Decimal:
        """Return a copy of the internal Decimal value."""
        return Decimal(self._value)

    def get_value(self) -> Decimal:
        """Get the internal Decimal value (alias for copy_value for test compatibility)."""
        return self.copy_value()

    def copy(self) -> "Number":
        """Return a copy of this Number."""
        return Number(self.copy_value())

    @staticmethod
    def get_instance(value: float | str | Decimal) -> "Number":
        """Factory method to create Number instances."""
        if isinstance(value, Decimal | str | int | float):
            return Number(value)
        else:
            raise TypeError(f"Unsupported type: {type(value)}")

    @staticmethod
    def random() -> "Number":
        """Generate a random Number between 0 and 1."""
        import random

        return Number.get_instance(random.random())

    def is_zero(self) -> bool:
        """Check if number is zero."""
        return self._value == 0

    def is_positive(self) -> bool:
        """Check if number is positive."""
        return self._value > 0

    def is_negative(self) -> bool:
        """Check if number is negative."""
        return self._value < 0

    def is_decimal(self) -> bool:
        """Check if number has a fractional part."""
        return not self.fractional_part().equal_to(Number.ZERO)

    def is_integer(self) -> bool:
        """Check if number is an integer."""
        return self.fractional_part().equal_to(Number.ZERO)

    def is_natural(self) -> bool:
        """Check if number is a natural number (non-negative integer)."""
        return self.is_integer() and (self.is_positive() or self.is_zero())

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if other is None:
            return False
        if other is self:
            return True
        if not isinstance(other, Number):
            return False
        return self._value == other._value

    def __str__(self) -> str:
        """String representation."""
        return str(self._value)

    def __repr__(self) -> str:
        """Representation."""
        return f"Number({self._value})"

    def equal_to(self, number: "Number") -> bool:
        """Check if equal to another Number."""
        return self == number

    def equals(self, number: "Number") -> bool:
        """Check if equal to another Number (alias for equal_to for test compatibility)."""
        return self.equal_to(number)

    def not_equal_to(self, number: "Number") -> bool:
        """Check if not equal to another Number."""
        return self != number

    def greater_than(self, number: "Number") -> bool:
        """Check if greater than another Number."""
        return self._value > number._value

    def less_than(self, number: "Number") -> bool:
        """Check if less than another Number."""
        return self._value < number._value

    def greater_than_or_equal_to(self, number: "Number") -> bool:
        """Check if greater than or equal to another Number."""
        return self._value >= number._value

    def less_than_or_equal_to(self, number: "Number") -> bool:
        """Check if less than or equal to another Number."""
        return self._value <= number._value

    def eq(self, number: "Number") -> bool:
        """Short form of equal_to."""
        return self.equal_to(number)

    def ne(self, number: "Number") -> bool:
        """Short form of not_equal_to."""
        return self.not_equal_to(number)

    def gt(self, number: "Number") -> bool:
        """Short form of greater_than."""
        return self.greater_than(number)

    def lt(self, number: "Number") -> bool:
        """Short form of less_than."""
        return self.less_than(number)

    def gte(self, number: "Number") -> bool:
        """Short form of greater_than_or_equal_to."""
        return self.greater_than_or_equal_to(number)

    def lte(self, number: "Number") -> bool:
        """Short form of less_than_or_equal_to."""
        return self.less_than_or_equal_to(number)

    def int_value(self) -> int:
        """Convert to int, raising error if not exact."""
        return int(self._value)

    def long_value(self) -> int:
        """Convert to long (int in Python 3)."""
        return int(self._value)

    def float_value(self) -> float:
        """Convert to float."""
        return float(self._value)

    def double_value(self) -> float:
        """Convert to double (float in Python)."""
        return float(self._value)

    @staticmethod
    def n(value: float | str | Decimal) -> "Number":
        """Short form of get_instance."""
        return Number.get_instance(value)

    # Instance methods (aliases for convenience)
    def i(self) -> int:
        """Instance method to get int value."""
        return self.int_value()

    def l(self) -> int:  # noqa: E743
        """Instance method to get long value."""
        return self.long_value()

    def f(self) -> float:
        """Instance method to get float value."""
        return self.float_value()

    def d(self) -> float:
        """Instance method to get double value."""
        return self.double_value()

    def abs(self) -> "Number":
        """Absolute value."""
        return Number(abs(self._value))

    def negate(self) -> "Number":
        """Negate the number."""
        if self.is_zero():
            return self.abs()
        return Number(-self._value)

    def max(self, number: "Number") -> "Number":
        """Maximum of this and another number."""
        return Number(max(self._value, number._value))

    def min(self, number: "Number") -> "Number":
        """Minimum of this and another number."""
        return Number(min(self._value, number._value))

    def add(self, number: "Number") -> "Number":
        """Add another number."""
        return Number(self._value + number._value)

    def subtract(self, number: "Number") -> "Number":
        """Subtract another number."""
        return Number(self._value - number._value)

    def multiply(self, number: "Number") -> "Number":
        """Multiply by another number."""
        return Number(self._value * number._value)

    def divide(self, number: "Number") -> "Number":
        """Divide by another number."""
        if number.is_zero():
            raise ZeroDivisionError("Division by zero")
        return Number(self._value / number._value)

    def remainder(self, number: "Number") -> "Number":
        """Remainder after division."""
        return Number(self._value % number._value)

    def reciprocal(self) -> "Number":
        """Reciprocal (1/x)."""
        return Number.ONE.divide(self)

    def signum(self) -> "Number":
        """Sign of the number (-1, 0, or 1)."""
        if self.is_zero():
            return Number.ZERO
        elif self.is_positive():
            return Number.ONE
        else:
            return Number(Decimal("-1"))

    def pow(self, exponent: "Number") -> "Number":
        """Raise to power."""
        # Use float for pow, then convert back
        result = math.pow(float(self._value), float(exponent._value))
        return Number(Decimal(str(result)))

    def nrt(self, number: "Number") -> "Number":
        """Nth root."""
        return self.pow(number.reciprocal())

    def sqrt(self) -> "Number":
        """Square root."""
        return self.nrt(Number.TWO)

    def cbrt(self) -> "Number":
        """Cube root."""
        return self.nrt(Number.THREE)

    def exp(self) -> "Number":
        """Exponential (e^x)."""
        return Number.E.pow(self)

    def log(self) -> "Number":
        """Natural logarithm."""
        result = math.log(float(self._value))
        return Number(Decimal(str(result)))

    def log10(self) -> "Number":
        """Base 10 logarithm."""
        return self.log().divide(Number.TEN.log())

    def fractional_part(self) -> "Number":
        """Fractional part of the number."""
        return self.remainder(Number.ONE)

    def integral_part(self) -> "Number":
        """Integral part of the number."""
        return self.subtract(self.fractional_part())

    def floor(self) -> "Number":
        """Floor (round down)."""
        integral = self.integral_part()
        if self.is_negative():
            return integral.subtract(Number.ONE)
        return integral

    def ceil(self) -> "Number":
        """Ceiling (round up)."""
        integral = self.integral_part()
        if self.is_negative():
            return integral
        return integral.add(Number.ONE)

    def round(self, scale: int | None = None) -> "Number":
        """Round to specified scale (default SCALE)."""
        if scale is None:
            scale = Number.SCALE
        rounded = self._value.quantize(Decimal(10) ** -scale, rounding=ROUND_HALF_UP)
        return Number(rounded)

    def factorial(self) -> "Number":
        """Factorial."""
        if not self.is_natural():
            raise ValueError("Factorial only defined for natural numbers")
        result = Number.ONE
        n = self.copy()
        while n.greater_than(Number.ZERO):
            result = result.multiply(n)
            n = n.subtract(Number.ONE)
        return result

    def to_degrees(self) -> "Number":
        """Convert radians to degrees."""
        k = Number.PI.divide(Number(180.0))
        return self.divide(k)

    def to_radians(self) -> "Number":
        """Convert degrees to radians."""
        k = Number.PI.divide(Number(180.0))
        return self.multiply(k)

    def sin(self) -> "Number":
        """Sine."""
        result = math.sin(float(self._value))
        return Number(Decimal(str(result)))

    def cos(self) -> "Number":
        """Cosine."""
        # cos(x) = sin(π/2 - x)
        half_pi = Number.PI.multiply(Number.HALF)
        return half_pi.subtract(self).sin()

    def tan(self) -> "Number":
        """Tangent."""
        return self.sin().divide(self.cos())


# Initialize constants after class definition
Number.ZERO = Number.get_instance(0.0)
Number.ONE = Number.get_instance(1.0)
Number.TWO = Number.get_instance(2.0)
Number.THREE = Number.get_instance(3.0)
Number.FOUR = Number.get_instance(4.0)
Number.FIVE = Number.get_instance(5.0)
Number.SIX = Number.get_instance(6.0)
Number.SEVEN = Number.get_instance(7.0)
Number.EIGHT = Number.get_instance(8.0)
Number.NINE = Number.get_instance(9.0)
Number.TEN = Number.get_instance(10.0)
Number.TWELVE = Number.get_instance(12.0)
Number.HUNDRED = Number.get_instance(100.0)
Number.THOUSAND = Number.get_instance(1000.0)
Number.HALF = Number.TWO.reciprocal()
Number.THIRD = Number.THREE.reciprocal()
Number.FORTH = Number.FOUR.reciprocal()
Number.FITH = Number.FIVE.reciprocal()
Number.TENTH = Number.TEN.reciprocal()
Number.CENT = Number.HUNDRED.reciprocal()
Number.THOUSANDTH = Number.THOUSAND.reciprocal()
Number.PI = Number.get_instance(math.pi)
Number.E = Number.get_instance(math.e)
