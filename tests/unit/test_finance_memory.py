"""Unit tests for FinanceMemory class."""

import pytest

from hp12c.calculator.exceptions import CalculatorException, Error
from hp12c.hp12c_math.number import Number
from hp12c.model.finance_memory import FinanceMemory


class TestFinanceMemory:
    """Test cases for FinanceMemory class."""

    def test_initialization(self):
        """Test finance memory initialization."""
        fin = FinanceMemory()
        assert fin is not None
        assert fin.get_size() == 5

    def test_initialization_custom_size(self):
        """Test initialization with custom size."""
        fin = FinanceMemory(size=10)
        assert fin.get_size() == 10

    def test_set_and_get(self):
        """Test setting and getting values."""
        fin = FinanceMemory()
        value = Number("100")
        fin.set(0, value)
        assert fin.get(0).equals(value)

    def test_set_and_get_tvm_variables(self):
        """Test setting and getting TVM variables."""
        fin = FinanceMemory()
        n = Number("12")
        i = Number("5")
        pv = Number("1000")
        pmt = Number("100")
        fv = Number("2000")

        fin.set_n(n)
        fin.set_i(i)
        fin.set_pv(pv)
        fin.set_pmt(pmt)
        fin.set_fv(fv)

        assert fin.get_n().equals(n)
        assert fin.get_i().equals(i)
        assert fin.get_pv().equals(pv)
        assert fin.get_pmt().equals(pmt)
        assert fin.get_fv().equals(fv)

    def test_set_and_get_begin(self):
        """Test setting and getting begin mode."""
        fin = FinanceMemory()
        fin.set_begin(True)
        assert fin.is_begin() is True
        fin.set_begin(False)
        assert fin.is_begin() is False

    def test_set_and_get_c(self):
        """Test setting and getting C flag."""
        fin = FinanceMemory()
        fin.set_c(True)
        assert fin.is_c() is True
        fin.set_c(False)
        assert fin.is_c() is False

    def test_clear(self):
        """Test clearing memory."""
        fin = FinanceMemory()
        fin.set_n(Number("12"))
        fin.clear()
        assert fin.get_n().equals(Number.ZERO)

    def test_get_array(self):
        """Test getting memory array."""
        fin = FinanceMemory()
        arr = fin.get_array()
        assert isinstance(arr, list)
        assert len(arr) == fin.get_size()

    def test_set_array(self):
        """Test setting memory array."""
        fin = FinanceMemory()
        new_array = [Number("1"), Number("2"), Number("3"), Number("4"), Number("5")]
        fin.set_array(new_array)
        assert fin.get_array() == new_array

    def test_simple_interest(self):
        """Test simple interest calculation."""
        fin = FinanceMemory()
        fin.set_n(Number("360"))
        fin.set_i(Number("5"))
        fin.set_pv(Number("1000"))
        result = fin.simple_interest()
        assert len(result) == 2
        assert isinstance(result[0], Number)
        assert isinstance(result[1], Number)

    def test_simple_future_value(self):
        """Test simple future value calculation."""
        fin = FinanceMemory()
        fin.set_n(Number("1"))
        fin.set_i(Number("5"))
        fin.set_pv(Number("1000"))
        result = fin.simple_future_value()
        assert isinstance(result, Number)

    def test_future_value(self):
        """Test future value calculation."""
        fin = FinanceMemory()
        fin.set_n(Number("12"))
        fin.set_i(Number("5"))
        fin.set_pv(Number("1000"))
        fin.set_pmt(Number("0"))
        fin.set_begin(False)
        fin.set_c(False)
        result = fin.future_value()
        assert isinstance(result, Number)

    def test_future_value_with_begin(self):
        """Test future value with begin mode."""
        fin = FinanceMemory()
        fin.set_n(Number("12"))
        fin.set_i(Number("5"))
        fin.set_pv(Number("1000"))
        fin.set_pmt(Number("100"))
        fin.set_begin(True)
        fin.set_c(False)
        result = fin.future_value()
        assert isinstance(result, Number)

    def test_future_value_error(self):
        """Test future value with invalid interest rate."""
        fin = FinanceMemory()
        fin.set_n(Number("12"))
        fin.set_i(Number("-101"))  # i <= -100
        fin.set_pv(Number("1000"))
        fin.set_pmt(Number("0"))
        with pytest.raises(CalculatorException) as exc_info:
            fin.future_value()
        assert exc_info.value.get_error() == Error.ERROR_CI

    def test_present_value(self):
        """Test present value calculation."""
        fin = FinanceMemory()
        fin.set_n(Number("12"))
        fin.set_i(Number("5"))
        fin.set_pmt(Number("100"))
        fin.set_fv(Number("2000"))
        fin.set_begin(False)
        fin.set_c(False)
        result = fin.present_value()
        assert isinstance(result, Number)

    def test_present_value_error(self):
        """Test present value with invalid interest rate."""
        fin = FinanceMemory()
        fin.set_n(Number("12"))
        fin.set_i(Number("-101"))  # i <= -100
        fin.set_pmt(Number("100"))
        fin.set_fv(Number("2000"))
        with pytest.raises(CalculatorException) as exc_info:
            fin.present_value()
        assert exc_info.value.get_error() == Error.ERROR_CI

    def test_payment(self):
        """Test payment calculation."""
        fin = FinanceMemory()
        fin.set_n(Number("12"))
        fin.set_i(Number("5"))
        fin.set_pv(Number("1000"))
        fin.set_fv(Number("0"))
        fin.set_begin(False)
        fin.set_c(False)
        result = fin.payment()
        assert isinstance(result, Number)

    def test_payment_error_n_zero(self):
        """Test payment with n == 0."""
        fin = FinanceMemory()
        fin.set_n(Number("0"))
        fin.set_i(Number("5"))
        fin.set_pv(Number("1000"))
        fin.set_fv(Number("0"))
        with pytest.raises(CalculatorException) as exc_info:
            fin.payment()
        assert exc_info.value.get_error() == Error.ERROR_CI

    def test_payment_error_i_zero(self):
        """Test payment with i == 0."""
        fin = FinanceMemory()
        fin.set_n(Number("12"))
        fin.set_i(Number("0"))
        fin.set_pv(Number("1000"))
        fin.set_fv(Number("0"))
        with pytest.raises(CalculatorException) as exc_info:
            fin.payment()
        assert exc_info.value.get_error() == Error.ERROR_CI

    def test_period(self):
        """Test period calculation."""
        fin = FinanceMemory()
        fin.set_i(Number("5"))
        fin.set_pv(Number("1000"))
        fin.set_pmt(Number("150"))
        fin.set_fv(Number("2000"))
        fin.set_begin(False)
        fin.set_c(False)
        result = fin.period()
        assert isinstance(result, Number)

    def test_period_error_invalid_pmt(self):
        """Test period calculation with invalid payment (pmt == fv * i)."""
        fin = FinanceMemory()
        fin.set_i(Number("5"))
        fin.set_pv(Number("1000"))
        fin.set_pmt(Number("100"))  # pmt == fv * i / 100.0 (2000 * 5 / 100 = 100)
        fin.set_fv(Number("2000"))
        fin.set_begin(False)
        fin.set_c(False)
        with pytest.raises(CalculatorException) as exc_info:
            fin.period()
        assert exc_info.value.get_error() == Error.ERROR_CI

    def test_rate(self):
        """Test rate calculation."""
        fin = FinanceMemory()
        fin.set_n(Number("12"))
        fin.set_pv(Number("-1000"))
        fin.set_pmt(Number("100"))
        fin.set_fv(Number("2000"))
        fin.set_begin(False)
        fin.set_c(False)
        result = fin.rate()
        assert isinstance(result, Number)

    def test_string_representation(self):
        """Test string representation."""
        fin = FinanceMemory()
        str_repr = str(fin)
        assert "FINANCE MEMORY" in str_repr
        assert "n" in str_repr
        assert "i" in str_repr
        assert "PV" in str_repr

    def test_initialization_with_tvm_variables(self):
        """Test initialization with TVM variables."""
        n = Number("12")
        i = Number("5")
        pv = Number("1000")
        pmt = Number("100")
        fv = Number("2000")
        fin = FinanceMemory(n=n, i=i, pv=pv, pmt=pmt, fv=fv)
        assert fin.get_n().equals(n)
        assert fin.get_i().equals(i)
        assert fin.get_pv().equals(pv)
        assert fin.get_pmt().equals(pmt)
        assert fin.get_fv().equals(fv)
