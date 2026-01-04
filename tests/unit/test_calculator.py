"""Unit tests for Calculator class."""

import pytest

from hp12c.calculator.exceptions import CalculatorException, Error
from hp12c.calculator.key import Key
from hp12c.hp12c_math.number import Number


class TestCalculator:
    """Test cases for Calculator class."""

    def test_initialization(self, calculator):
        """Test calculator initialization."""
        assert calculator is not None
        assert calculator.get_stack() is not None
        assert calculator.get_display() is not None
        assert calculator.get_flags() is not None

    def test_basic_arithmetic_addition(self, calculator):
        """Test basic addition operation."""
        # Enter 5
        calculator.process_key(Key.KEY_5)
        calculator.process_key(Key.KEY_ENTER)
        # Enter 3
        calculator.process_key(Key.KEY_3)
        # Add
        calculator.process_key(Key.KEY_SUM)

        result = calculator.get_stack().get(0)
        assert result.equals(Number("8"))

    def test_basic_arithmetic_subtraction(self, calculator):
        """Test basic subtraction operation."""
        # Enter 10
        calculator.process_key(Key.KEY_1)
        calculator.process_key(Key.KEY_0)
        calculator.process_key(Key.KEY_ENTER)
        # Enter 3
        calculator.process_key(Key.KEY_3)
        # Subtract
        calculator.process_key(Key.KEY_SUB)

        result = calculator.get_stack().get(0)
        assert result.equals(Number("7"))

    def test_basic_arithmetic_multiplication(self, calculator):
        """Test basic multiplication operation."""
        # Enter 4
        calculator.process_key(Key.KEY_4)
        calculator.process_key(Key.KEY_ENTER)
        # Enter 5
        calculator.process_key(Key.KEY_5)
        # Multiply
        calculator.process_key(Key.KEY_MUL)

        result = calculator.get_stack().get(0)
        assert result.equals(Number("20"))

    def test_basic_arithmetic_division(self, calculator):
        """Test basic division operation."""
        # Enter 20
        calculator.process_key(Key.KEY_2)
        calculator.process_key(Key.KEY_0)
        calculator.process_key(Key.KEY_ENTER)
        # Enter 4
        calculator.process_key(Key.KEY_4)
        # Divide
        calculator.process_key(Key.KEY_DIV)

        result = calculator.get_stack().get(0)
        assert result.equals(Number("5"))

    def test_division_by_zero(self, calculator):
        """Test division by zero raises error."""
        # Enter 10
        calculator.process_key(Key.KEY_1)
        calculator.process_key(Key.KEY_0)
        calculator.process_key(Key.KEY_ENTER)
        # Enter 0
        calculator.process_key(Key.KEY_0)
        # Divide
        with pytest.raises(CalculatorException) as exc_info:
            calculator.process_key(Key.KEY_DIV)
        assert exc_info.value.get_error() == Error.ERROR_MATH

    def test_stack_operations_enter(self, calculator):
        """Test ENTER key pushes stack."""
        # Enter 5
        calculator.process_key(Key.KEY_5)
        calculator.process_key(Key.KEY_ENTER)

        # Stack should have 5 in both X and Y
        x = calculator.get_stack().get(0)
        y = calculator.get_stack().get(1)
        assert x.equals(Number("5"))
        assert y.equals(Number("5"))

    def test_stack_operations_swap(self, calculator):
        """Test XY swap operation."""
        # Enter 5
        calculator.process_key(Key.KEY_5)
        calculator.process_key(Key.KEY_ENTER)
        # Enter 3
        calculator.process_key(Key.KEY_3)
        # Swap
        calculator.process_key(Key.KEY_XY)

        x = calculator.get_stack().get(0)
        y = calculator.get_stack().get(1)
        assert x.equals(Number("5"))
        assert y.equals(Number("3"))

    def test_stack_operations_roll(self, calculator):
        """Test ROLL operation."""
        # Enter values 1, 2, 3, 4
        calculator.process_key(Key.KEY_1)
        calculator.process_key(Key.KEY_ENTER)
        calculator.process_key(Key.KEY_2)
        calculator.process_key(Key.KEY_ENTER)
        calculator.process_key(Key.KEY_3)
        calculator.process_key(Key.KEY_ENTER)
        calculator.process_key(Key.KEY_4)

        # Roll down
        calculator.process_key(Key.KEY_ROLL)

        # After roll, stack should be rotated
        x = calculator.get_stack().get(0)
        assert x.equals(Number("1"))  # 4 should roll to T, 1 comes to X

    def test_clear_x(self, calculator):
        """Test CLX (clear X) operation."""
        # Enter 5
        calculator.process_key(Key.KEY_5)
        # Clear X
        calculator.process_key(Key.KEY_CLX)

        x = calculator.get_stack().get(0)
        assert x.equals(Number.ZERO)

    def test_chs_operation(self, calculator):
        """Test CHS (change sign) operation."""
        # Enter 5
        calculator.process_key(Key.KEY_5)
        # Change sign
        calculator.process_key(Key.KEY_CHS)

        x = calculator.get_stack().get(0)
        assert x.equals(Number("-5"))

    def test_reciprocal(self, calculator):
        """Test reciprocal operation."""
        # Enter 4
        calculator.process_key(Key.KEY_4)
        calculator.process_key(Key.KEY_ENTER)
        # Reciprocal
        calculator.process_key(Key.KEY_RECIPROCAL)

        result = calculator.get_stack().get(0)
        assert result.equals(Number("0.25"))

    def test_square_root(self, calculator):
        """Test square root operation."""
        # Enter 16
        calculator.process_key(Key.KEY_1)
        calculator.process_key(Key.KEY_6)
        calculator.process_key(Key.KEY_ENTER)
        # Square root
        calculator.process_key(Key.KEY_G)
        calculator.process_key(Key.KEY_XY)  # G + XY = sqrt

        result = calculator.get_stack().get(0)
        # Should be approximately 4
        assert abs(float(result.get_value()) - 4.0) < 0.0001

    def test_power_operation(self, calculator):
        """Test power operation."""
        # Enter 2
        calculator.process_key(Key.KEY_2)
        calculator.process_key(Key.KEY_ENTER)
        # Enter 3
        calculator.process_key(Key.KEY_3)
        # Power (2^3)
        calculator.process_key(Key.KEY_POW)

        result = calculator.get_stack().get(0)
        assert result.equals(Number("8"))

    def test_percentage(self, calculator):
        """Test percentage operation."""
        # Enter 100
        calculator.process_key(Key.KEY_1)
        calculator.process_key(Key.KEY_0)
        calculator.process_key(Key.KEY_0)
        calculator.process_key(Key.KEY_ENTER)
        # Enter 20
        calculator.process_key(Key.KEY_2)
        calculator.process_key(Key.KEY_0)
        # Percentage
        calculator.process_key(Key.KEY_PERC)

        result = calculator.get_stack().get(0)
        assert result.equals(Number("20"))

    def test_memory_store_and_recall(self, calculator):
        """Test memory store and recall operations."""
        # Enter 42
        calculator.process_key(Key.KEY_4)
        calculator.process_key(Key.KEY_2)
        # Store in R0
        calculator.process_key(Key.KEY_STO)
        calculator.process_key(Key.KEY_0)

        # Clear display
        calculator.process_key(Key.KEY_CLX)

        # Recall from R0
        calculator.process_key(Key.KEY_RCL)
        calculator.process_key(Key.KEY_0)

        result = calculator.get_stack().get(0)
        assert result.equals(Number("42"))

    def test_display_formatting(self, calculator):
        """Test display formatting."""
        # Enter 1234.56
        calculator.process_key(Key.KEY_1)
        calculator.process_key(Key.KEY_2)
        calculator.process_key(Key.KEY_3)
        calculator.process_key(Key.KEY_4)
        calculator.process_key(Key.KEY_DOT)
        calculator.process_key(Key.KEY_5)
        calculator.process_key(Key.KEY_6)

        display = calculator.get_display()
        display_text = display.get_text()
        # Display may include thousands separators and leading spaces
        # Check for the numeric value (with or without formatting)
        assert (
            "1234.56" in display_text
            or "1234,56" in display_text
            or "1,234.56" in display_text
            or "1.234,56" in display_text
        )

    def test_error_handling(self, calculator):
        """Test error handling."""
        # Try to divide by zero
        calculator.process_key(Key.KEY_1)
        calculator.process_key(Key.KEY_ENTER)
        calculator.process_key(Key.KEY_0)

        with pytest.raises(CalculatorException):
            calculator.process_key(Key.KEY_DIV)
