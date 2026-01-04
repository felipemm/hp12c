"""Unit tests for GeneralMemory class."""

import pytest

from hp12c.hp12c_math.number import Number
from hp12c.model.general_memory import GeneralMemory


class TestGeneralMemory:
    """Test cases for GeneralMemory class."""

    def test_initialization(self):
        """Test general memory initialization."""
        mem = GeneralMemory()
        assert mem is not None
        assert mem.get_size() == 20

    def test_initialization_custom_size(self):
        """Test initialization with custom size."""
        mem = GeneralMemory(size=10)
        assert mem.get_size() == 10

    def test_set_and_get(self):
        """Test setting and getting values."""
        mem = GeneralMemory()
        value = Number("42")
        mem.set(0, value)
        assert mem.get(0).equals(value)

    def test_get_out_of_bounds(self):
        """Test getting value out of bounds."""
        mem = GeneralMemory()
        result = mem.get(100)
        assert result.equals(Number.ZERO)

    def test_set_out_of_bounds(self):
        """Test setting value out of bounds."""
        mem = GeneralMemory()
        value = Number("42")
        mem.set(100, value)
        # Should not raise error, just ignore

    def test_get_with_times(self):
        """Test getting value with times."""
        mem = GeneralMemory()
        result = mem.get_with_times(0)
        assert len(result) == 2
        assert isinstance(result[0], Number)
        assert isinstance(result[1], Number)

    def test_set_times(self):
        """Test setting times."""
        mem = GeneralMemory()
        times = Number("5")
        mem.set_times(0, times)
        assert mem.get_times(0).equals(times)

    def test_get_times(self):
        """Test getting times."""
        mem = GeneralMemory()
        times = mem.get_times(0)
        assert isinstance(times, Number)

    def test_set_with_times(self):
        """Test setting value and times together."""
        mem = GeneralMemory()
        value = Number("42")
        times = Number("3")
        mem.set_with_times(0, value, times)
        assert mem.get(0).equals(value)
        assert mem.get_times(0).equals(times)

    def test_set_with_times_invalid_times(self):
        """Test setting with invalid times (too large)."""
        mem = GeneralMemory()
        value = Number("42")
        times = Number("200")  # > 100
        mem.set_with_times(0, value, times)
        # Should not set if times is invalid
        # Original value should remain

    def test_set_with_times_from_array(self):
        """Test setting from array."""
        mem = GeneralMemory()
        arr = [Number("42"), Number("3")]
        mem.set_with_times_from_array(0, arr)
        assert mem.get(0).equals(Number("42"))
        assert mem.get_times(0).equals(Number("3"))

    def test_get_current_index(self):
        """Test getting current index."""
        mem = GeneralMemory()
        assert mem.get_current_index() == 0

    def test_put(self):
        """Test putting value at current index."""
        mem = GeneralMemory()
        value = Number("42")
        mem.put(value)
        assert mem.get_current_index() == 1
        assert mem.get(1).equals(value)

    def test_put_with_times(self):
        """Test putting value with times."""
        mem = GeneralMemory()
        value = Number("42")
        times = Number("3")
        mem.put(value, times)
        assert mem.get(1).equals(value)
        assert mem.get_times(1).equals(times)

    def test_put_from_array(self):
        """Test putting from array."""
        mem = GeneralMemory()
        arr = [Number("42"), Number("3")]
        mem.put_from_array(arr)
        assert mem.get_current_index() == 1

    def test_clear(self):
        """Test clearing memory."""
        mem = GeneralMemory()
        mem.set(0, Number("42"))
        mem.clear()
        assert mem.get(0).equals(Number.ZERO)
        assert mem.get_current_index() == 0

    def test_get_used_registers(self):
        """Test getting number of used registers."""
        mem = GeneralMemory()
        assert mem.get_used_registers() == 0
        mem.set(0, Number("42"))
        assert mem.get_used_registers() >= 1

    def test_get_available_registers(self):
        """Test getting number of available registers."""
        mem = GeneralMemory(size=10)
        available = mem.get_available_registers()
        assert available == 10
        mem.set(0, Number("42"))
        available = mem.get_available_registers()
        assert available == 9

    def test_get_array(self):
        """Test getting memory array."""
        mem = GeneralMemory()
        arr = mem.get_array()
        assert isinstance(arr, list)
        assert len(arr) == mem.get_size()

    def test_set_array(self):
        """Test setting memory array."""
        mem = GeneralMemory(size=5)
        new_array = [[Number("1"), Number.ONE], [Number("2"), Number.ONE]]
        mem.set_array(new_array)
        # Array should be set (may truncate or extend)

    def test_sum_stats(self):
        """Test adding to statistics."""
        mem = GeneralMemory()
        x = Number("10")
        y = Number("20")
        mem.sum_stats(x, y)
        assert mem.get_r1().greater_than(Number.ZERO)
        assert mem.get_r2().equals(x)
        assert mem.get_r4().equals(y)

    def test_sub_stats(self):
        """Test subtracting from statistics."""
        mem = GeneralMemory()
        x = Number("10")
        y = Number("20")
        mem.sum_stats(x, y)
        mem.sub_stats(x, y)
        # Should return to near zero
        assert mem.get_r1().equals(Number.ZERO)

    def test_clear_stats(self):
        """Test clearing statistics."""
        mem = GeneralMemory()
        mem.sum_stats(Number("10"), Number("20"))
        mem.clear_stats()
        assert mem.get_r1().equals(Number.ZERO)
        assert mem.get_r2().equals(Number.ZERO)

    def test_mean(self):
        """Test calculating mean."""
        mem = GeneralMemory()
        mem.sum_stats(Number("10"), Number("20"))
        mem.sum_stats(Number("20"), Number("30"))
        result = mem.mean()
        assert len(result) == 2
        assert isinstance(result[0], Number)
        assert isinstance(result[1], Number)

    def test_mean_empty(self):
        """Test mean with empty data raises error."""
        mem = GeneralMemory()
        with pytest.raises(ValueError):
            mem.mean()

    def test_weighted_mean(self):
        """Test calculating weighted mean."""
        mem = GeneralMemory()
        mem.sum_stats(Number("10"), Number("20"))
        result = mem.weighted_mean()
        assert isinstance(result, Number)

    def test_weighted_mean_empty(self):
        """Test weighted mean with empty data raises error."""
        mem = GeneralMemory()
        with pytest.raises(ValueError):
            mem.weighted_mean()

    def test_standard_deviation(self):
        """Test calculating standard deviation."""
        mem = GeneralMemory()
        mem.sum_stats(Number("10"), Number("20"))
        mem.sum_stats(Number("20"), Number("30"))
        result = mem.standard_deviation()
        assert len(result) == 2
        assert isinstance(result[0], Number)
        assert isinstance(result[1], Number)

    def test_standard_deviation_empty(self):
        """Test standard deviation with empty data raises error."""
        mem = GeneralMemory()
        with pytest.raises(ValueError):
            mem.standard_deviation()

    def test_y_linear_estimation(self):
        """Test y linear estimation."""
        mem = GeneralMemory()
        mem.sum_stats(Number("10"), Number("20"))
        mem.sum_stats(Number("20"), Number("30"))
        result = mem.y_linear_estimation(Number("15"))
        assert len(result) == 2
        assert isinstance(result[0], Number)
        assert isinstance(result[1], Number)

    def test_y_linear_estimation_empty(self):
        """Test y linear estimation with empty data raises error."""
        mem = GeneralMemory()
        with pytest.raises(ValueError):
            mem.y_linear_estimation(Number("15"))

    def test_register_accessors(self):
        """Test register accessor methods."""
        mem = GeneralMemory()
        mem.set_r1(Number("1"))
        mem.set_r2(Number("2"))
        mem.set_r3(Number("3"))
        mem.set_r4(Number("4"))
        mem.set_r5(Number("5"))
        mem.set_r6(Number("6"))

        assert mem.get_r1().equals(Number("1"))
        assert mem.get_r2().equals(Number("2"))
        assert mem.get_r3().equals(Number("3"))
        assert mem.get_r4().equals(Number("4"))
        assert mem.get_r5().equals(Number("5"))
        assert mem.get_r6().equals(Number("6"))

    def test_string_representation(self):
        """Test string representation."""
        mem = GeneralMemory()
        str_repr = str(mem)
        assert "GENERAL MEMORY" in str_repr
