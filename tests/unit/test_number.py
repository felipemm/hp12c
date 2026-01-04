"""Unit tests for Number class."""

from decimal import Decimal

import pytest

from hp12c.hp12c_math.number import Number


class TestNumber:
    """Test cases for Number class."""

    def test_initialization_from_string(self):
        """Test Number initialization from string."""
        num = Number("123.45")
        assert num.get_value() == Decimal("123.45")

    def test_initialization_from_decimal(self):
        """Test Number initialization from Decimal."""
        num = Number(Decimal("42.5"))
        assert num.get_value() == Decimal("42.5")

    def test_initialization_from_int(self):
        """Test Number initialization from int."""
        num = Number(42)
        assert num.get_value() == Decimal("42")

    def test_initialization_from_float(self):
        """Test Number initialization from float."""
        num = Number(3.14)
        # Float precision may vary, so check approximate equality
        assert abs(float(num.get_value()) - 3.14) < 0.01

    def test_constants(self):
        """Test Number constants."""
        assert Number.ZERO.equals(Number("0"))
        assert Number.ONE.equals(Number("1"))
        assert Number.TWO.equals(Number("2"))
        assert Number.TEN.equals(Number("10"))

    def test_addition(self, number_one, number_ten):
        """Test addition operation."""
        result = number_one.add(number_ten)
        assert result.equals(Number("11"))

    def test_subtraction(self, number_ten, number_one):
        """Test subtraction operation."""
        result = number_ten.subtract(number_one)
        assert result.equals(Number("9"))

    def test_multiplication(self, number_one, number_ten):
        """Test multiplication operation."""
        result = number_one.multiply(number_ten)
        assert result.equals(Number("10"))

    def test_division(self, number_ten, number_one):
        """Test division operation."""
        result = number_ten.divide(number_one)
        assert result.equals(Number("10"))

    def test_division_by_zero(self, number_one, number_zero):
        """Test division by zero raises error."""
        with pytest.raises(ZeroDivisionError):
            number_one.divide(number_zero)

    def test_reciprocal(self, number_ten):
        """Test reciprocal operation."""
        result = number_ten.reciprocal()
        assert result.equals(Number("0.1"))

    def test_square_root(self):
        """Test square root operation."""
        num = Number("16")
        result = num.sqrt()
        assert result.equals(Number("4"))

    def test_power(self):
        """Test power operation."""
        base = Number("2")
        exponent = Number("3")
        result = base.pow(exponent)
        assert result.equals(Number("8"))

    def test_logarithm(self):
        """Test natural logarithm."""
        num = Number("2.71828")  # Approximate e
        result = num.log()
        # log(e) should be approximately 1
        assert abs(float(result.get_value()) - 1.0) < 0.1

    def test_log10(self):
        """Test base 10 logarithm."""
        num = Number("100")
        result = num.log10()
        assert abs(float(result.get_value()) - 2.0) < 0.0001

    def test_exponential(self):
        """Test exponential function."""
        num = Number("1")
        result = num.exp()
        # e^1 should be approximately e
        assert abs(float(result.get_value()) - 2.71828) < 0.1

    def test_equals(self):
        """Test equality comparison."""
        num1 = Number("42")
        num2 = Number("42")
        num3 = Number("43")

        assert num1.equals(num2)
        assert not num1.equals(num3)

    def test_less_than(self):
        """Test less than comparison."""
        num1 = Number("5")
        num2 = Number("10")

        assert num1.less_than(num2)
        assert not num2.less_than(num1)

    def test_greater_than(self):
        """Test greater than comparison."""
        num1 = Number("10")
        num2 = Number("5")

        assert num1.greater_than(num2)
        assert not num2.greater_than(num1)

    def test_is_zero(self, number_zero, number_one):
        """Test is_zero check."""
        assert number_zero.is_zero()
        assert not number_one.is_zero()

    def test_is_positive(self, number_one):
        """Test is_positive check."""
        assert number_one.is_positive()

        negative = Number("-5")
        assert not negative.is_positive()

    def test_is_negative(self):
        """Test is_negative check."""
        negative = Number("-5")
        assert negative.is_negative()

        positive = Number("5")
        assert not positive.is_negative()

    def test_signum(self, number_zero, number_one):
        """Test signum function."""
        assert number_zero.signum().equals(Number.ZERO)
        assert number_one.signum().equals(Number.ONE)

        negative = Number("-5")
        assert negative.signum().equals(Number("-1"))

    def test_absolute_value(self):
        """Test absolute value."""
        negative = Number("-42")
        result = negative.abs()
        assert result.equals(Number("42"))

    def test_min_max(self):
        """Test min and max functions."""
        num1 = Number("5")
        num2 = Number("10")

        assert num1.min(num2).equals(num1)
        assert num1.max(num2).equals(num2)
