"""Unit tests for Step class."""

from hp12c.model.step import Step


class TestStep:
    """Test cases for Step class."""

    def test_initialization(self):
        """Test step initialization."""
        step = Step()
        assert step is not None
        assert step.get_modifier() == -1
        assert step.get_key() == -1
        assert step.get_complement() == -1

    def test_initialization_with_values(self):
        """Test step initialization with values."""
        step = Step(1, 2, 3)
        assert step.get_modifier() == 1
        assert step.get_key() == 2
        assert step.get_complement() == 3

    def test_initialization_from_step(self):
        """Test step initialization from another step."""
        original = Step(1, 2, 3)
        step = Step(stp=original)
        assert step.get_modifier() == 1
        assert step.get_key() == 2
        assert step.get_complement() == 3

    def test_initialization_from_array(self):
        """Test step initialization from array."""
        step = Step(stp_array=[1, 2, 3])
        assert step.get_modifier() == 1
        assert step.get_key() == 2
        assert step.get_complement() == 3

    def test_set_step(self):
        """Test setting step values."""
        step = Step()
        step.set_step(5, 10, 15)
        assert step.get_modifier() == 5
        assert step.get_key() == 10
        assert step.get_complement() == 15

    def test_set_modifier(self):
        """Test setting modifier."""
        step = Step()
        step.set_modifier(5)
        assert step.get_modifier() == 5

    def test_set_key(self):
        """Test setting key."""
        step = Step()
        step.set_key(10)
        assert step.get_key() == 10

    def test_set_complement(self):
        """Test setting complement."""
        step = Step()
        step.set_complement(15)
        assert step.get_complement() == 15

    def test_get_array(self):
        """Test getting step as array."""
        step = Step(1, 2, 3)
        arr = step.get_array()
        assert arr == [1, 2, 3]

    def test_clear(self):
        """Test clearing step."""
        step = Step(1, 2, 3)
        step.clear()
        assert step.get_modifier() == -1
        assert step.get_key() == -1
        assert step.get_complement() == -1

    def test_is_undefined(self):
        """Test checking if step is undefined."""
        step = Step()
        assert step.is_undefined() is True
        step = Step(1, 2, 3)
        assert step.is_undefined() is False

    def test_is_undefined_static(self):
        """Test static method for checking undefined."""
        step = Step()
        assert Step.is_undefined_static(step) is True
        step = Step(1, 2, 3)
        assert Step.is_undefined_static(step) is False

    def test_set_undefined(self):
        """Test setting step to undefined."""
        step = Step(1, 2, 3)
        step.set_undefined()
        assert step.is_undefined() is True

    def test_set_undefined_static(self):
        """Test static method for setting undefined."""
        step = Step(1, 2, 3)
        Step.set_undefined_static(step)
        assert step.is_undefined() is True

    def test_get_undefined(self):
        """Test getting undefined step."""
        step = Step.get_undefined()
        assert step.is_undefined() is True

    def test_equals(self):
        """Test equality comparison."""
        step1 = Step(1, 2, 3)
        step2 = Step(1, 2, 3)
        step3 = Step(4, 5, 6)
        assert step1.equals(step2) is True
        assert step1.equals(step3) is False

    def test_set_step_from_step(self):
        """Test setting step from another step."""
        step1 = Step(1, 2, 3)
        step2 = Step()
        step2.set_step_from_step(step1)
        assert step2.equals(step1) is True

    def test_set_array_from_array(self):
        """Test setting step from array."""
        step = Step()
        step.set_array_from_array([5, 10, 15])
        assert step.get_modifier() == 5
        assert step.get_key() == 10
        assert step.get_complement() == 15

    def test_is_financial_step(self):
        """Test checking if step is financial."""
        step = Step(0, 11, 0)  # N key
        assert step.is_financial_step() is True
        step = Step(0, 12, 0)  # I key
        assert step.is_financial_step() is True
        step = Step(0, 20, 0)  # Non-financial key
        assert step.is_financial_step() is False

    def test_string_representation(self):
        """Test string representation."""
        step = Step(1, 2, 3)
        str_repr = str(step)
        assert "STEP" in str_repr
        assert "Modifier" in str_repr
        assert "Function" in str_repr
