"""Unit tests for Exceptions and Key classes."""

from hp12c.calculator.exceptions import CalculatorException, Error
from hp12c.calculator.key import Key


class TestError:
    """Test cases for Error enum."""

    def test_error_enum_values(self):
        """Test that all error types exist."""
        assert Error.ERROR_MATH is not None
        assert Error.ERROR_SRO is not None
        assert Error.ERROR_STAT is not None
        assert Error.ERROR_IRR1 is not None
        assert Error.ERROR_MEM is not None
        assert Error.ERROR_CI is not None
        assert Error.ERROR_SR is not None
        assert Error.ERROR_IRR2 is not None
        assert Error.ERROR_CAL is not None
        assert Error.ERROR_SERV is not None
        assert Error.ERROR_PR is not None
        assert Error.ERROR_MAG is not None

    def test_get_code(self):
        """Test getting error code."""
        assert Error.ERROR_MATH.get_code() == 0
        assert Error.ERROR_SRO.get_code() == 1
        assert Error.ERROR_MAG.get_code() == 99

    def test_get_message(self):
        """Test getting error message."""
        assert Error.ERROR_MATH.get_message() == "Math Error"
        assert Error.ERROR_SRO.get_message() == "Storage Register Overflow Error"

    def test_get_name(self):
        """Test getting error name."""
        assert Error.ERROR_MATH.get_name() == "ERROR_MATH"

    def test_string_representation(self):
        """Test string representation."""
        error_str = str(Error.ERROR_MATH)
        assert "ERROR" in error_str
        assert "Math Error" in error_str


class TestCalculatorException:
    """Test cases for CalculatorException class."""

    def test_initialization(self):
        """Test exception initialization."""
        exc = CalculatorException(Error.ERROR_MATH)
        assert exc is not None
        assert exc.get_error() == Error.ERROR_MATH

    def test_initialization_with_detail(self):
        """Test exception initialization with detail."""
        exc = CalculatorException(Error.ERROR_MATH, "Division by zero")
        assert exc.get_detail() == "Division by zero"

    def test_get_error(self):
        """Test getting error."""
        exc = CalculatorException(Error.ERROR_STAT)
        assert exc.get_error() == Error.ERROR_STAT

    def test_get_detail(self):
        """Test getting detail."""
        exc = CalculatorException(Error.ERROR_MATH, "Test detail")
        assert exc.get_detail() == "Test detail"

    def test_get_code(self):
        """Test getting error code."""
        exc = CalculatorException(Error.ERROR_MATH)
        assert exc.get_code() == 0

    def test_get_name(self):
        """Test getting error name."""
        exc = CalculatorException(Error.ERROR_MATH)
        assert exc.get_name() == "ERROR_MATH"

    def test_get_message(self):
        """Test getting error message."""
        exc = CalculatorException(Error.ERROR_MATH)
        assert exc.get_message() == "Math Error"

    def test_string_representation(self):
        """Test string representation."""
        exc = CalculatorException(Error.ERROR_MATH)
        error_str = str(exc)
        assert "ERROR" in error_str or "Math Error" in error_str

    def test_string_representation_with_detail(self):
        """Test string representation with detail."""
        exc = CalculatorException(Error.ERROR_MATH, "Division by zero")
        error_str = str(exc)
        assert "Division by zero" in error_str


class TestKey:
    """Test cases for Key enum."""

    def test_key_enum_values(self):
        """Test that key enum values exist."""
        assert Key.KEY_0 is not None
        assert Key.KEY_1 is not None
        assert Key.KEY_9 is not None
        assert Key.KEY_ENTER is not None
        assert Key.KEY_SUM is not None
        assert Key.KEY_SUB is not None
        assert Key.KEY_MUL is not None
        assert Key.KEY_DIV is not None

    def test_get_code(self):
        """Test getting key code."""
        assert Key.KEY_0.get_code() == 0
        assert Key.KEY_1.get_code() == 1
        assert Key.KEY_ENTER.get_code() == 36

    def test_get_name(self):
        """Test getting key name."""
        assert Key.KEY_0.get_name() == "KEY_0"
        assert Key.KEY_ENTER.get_name() == "KEY_ENTER"

    def test_get_key_by_code(self):
        """Test getting key by code."""
        key = Key.get_key(0)
        assert key == Key.KEY_0
        key = Key.get_key(36)
        assert key == Key.KEY_ENTER

    def test_get_key_by_code_invalid(self):
        """Test getting key by invalid code."""
        key = Key.get_key(9999)
        assert key == Key.KEY_NULL

    def test_get_key_by_name(self):
        """Test getting key by name."""
        key = Key.get_key_by_name("KEY_0")
        assert key == Key.KEY_0
        key = Key.get_key_by_name("KEY_ENTER")
        assert key == Key.KEY_ENTER

    def test_get_key_by_name_invalid(self):
        """Test getting key by invalid name."""
        key = Key.get_key_by_name("INVALID_KEY")
        assert key == Key.KEY_NULL

    def test_get_name_by_code(self):
        """Test getting name by code."""
        name = Key.get_name_by_code(0)
        assert name == "KEY_0"
        name = Key.get_name_by_code(36)
        assert name == "KEY_ENTER"

    def test_get_name_by_code_invalid(self):
        """Test getting name by invalid code."""
        name = Key.get_name_by_code(-1)
        assert name == ""
        name = Key.get_name_by_code(9999)
        assert name == ""

    def test_string_representation(self):
        """Test string representation."""
        key_str = str(Key.KEY_0)
        assert "KEY" in key_str
        assert "0" in key_str
