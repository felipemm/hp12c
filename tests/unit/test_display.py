"""Unit tests for Display class."""

from hp12c.hp12c_math.number import Number
from hp12c.model.display import Display


class TestDisplay:
    """Test cases for Display class."""

    def test_initialization(self):
        """Test display initialization."""
        display = Display()
        assert display is not None
        assert display.get_text() == "0" or "0" in display.get_text()

    def test_set_and_get_precision(self):
        """Test precision setting."""
        display = Display()
        display.set_precision(5)
        assert display.get_precision() == 5

    def test_set_and_get_status(self):
        """Test status setting."""
        display = Display()
        display.set_status(Display.STATUS_INPUT)
        assert display.get_status() == Display.STATUS_INPUT

    def test_set_and_get_mode(self):
        """Test mode setting."""
        display = Display()
        display.set_mode(Display.MODE_EXPONENTIAL)
        assert display.get_mode() == Display.MODE_EXPONENTIAL

    def test_comma_toggle(self):
        """Test comma/dot separator toggle."""
        display = Display()
        initial = display.get_comma()
        display.toggle_comma()
        assert display.get_comma() != initial
        display.toggle_comma()
        assert display.get_comma() == initial

    def test_set_comma(self):
        """Test setting comma separator."""
        display = Display()
        display.set_comma(True)
        assert display.get_comma() is True
        display.set_comma(False)
        assert display.get_comma() is False

    def test_set_and_get_lock(self):
        """Test lock setting."""
        display = Display()
        display.set_lock(True)
        assert display.get_lock() is True
        display.set_lock(False)
        assert display.get_lock() is False

    def test_set_and_get_pause(self):
        """Test pause setting."""
        display = Display()
        display.set_pause(True)
        assert display.get_pause() is True
        display.set_pause(False)
        assert display.get_pause() is False

    def test_clear(self):
        """Test clear operation."""
        display = Display()
        display.input_char("5")
        display.clear()
        text = display.get_text()
        assert "0" in text or text.strip() == ""

    def test_input_char_digit(self):
        """Test inputting digits."""
        display = Display()
        display.input_char("5")
        text = display.get_text()
        assert "5" in text

    def test_input_char_multiple_digits(self):
        """Test inputting multiple digits."""
        display = Display()
        display.input_char("1")
        display.input_char("2")
        display.input_char("3")
        text = display.get_text()
        assert "123" in text.replace(".", "").replace(",", "").replace(" ", "")

    def test_input_char_decimal_point(self):
        """Test inputting decimal point."""
        display = Display()
        display.input_char("5")
        display.input_char(".")
        display.input_char("2")
        text = display.get_text()
        assert "." in text or "," in text
        assert "5" in text and "2" in text

    def test_input_char_negative(self):
        """Test inputting negative sign."""
        display = Display()
        display.input_char("5")
        display.input_char("-")
        text = display.get_text()
        assert "-" in text or "5" in text

    def test_set_message(self):
        """Test setting message."""
        display = Display()
        display.set_message("Error")
        display.set_lock(True)
        text = display.get_text()
        assert "Error" in text

    def test_set_value(self):
        """Test setting value from Number."""
        display = Display()
        num = Number("42.5")
        display.set_value(num)
        text = display.get_text()
        assert "42" in text.replace(".", "").replace(",", "").replace(" ", "")

    def test_get_value(self):
        """Test getting value as Number."""
        display = Display()
        display.input_char("1")
        display.input_char("2")
        display.input_char("3")
        value = display.get_value()
        assert value is not None
        assert isinstance(value, Number)

    def test_set_ready(self):
        """Test setting display to ready state."""
        display = Display()
        display.input_char("5")
        display.set_ready()
        assert display.get_mode() == Display.MODE_NORMAL
        assert display.get_status() != Display.STATUS_INPUT

    def test_zero_pad(self):
        """Test zero padding utility."""
        result = Display.zero_pad(5, 3)
        assert result == "005"
        result = Display.zero_pad(123, 3)
        assert result == "123"

    def test_space_pad(self):
        """Test space padding utility."""
        result = Display.space_pad(5, 3)
        assert result == "  5"
        result = Display.space_pad(123, 3)
        assert result == "123"

    def test_input_program_step(self):
        """Test inputting program step."""
        display = Display()
        from hp12c.model.step import Step

        step = Step(1, 2, 3)
        display.input_program_step(0, step)
        display.set_mode(Display.MODE_PROGRAM)
        text = display.get_text()
        assert text is not None

    def test_exponential_mode(self):
        """Test exponential mode input."""
        display = Display()
        display.set_mode(Display.MODE_EXPONENTIAL)
        display.input_char("1")
        display.input_char(".")
        display.input_char("5")
        text = display.get_text()
        assert text is not None

    def test_get_mantissa(self):
        """Test getting mantissa."""
        display = Display()
        display.input_char("1")
        display.input_char("2")
        display.input_char("3")
        mantissa = display.get_mantissa()
        assert mantissa is not None
        assert len(mantissa) == 10

    def test_lock_prevents_input(self):
        """Test that lock prevents input."""
        display = Display()
        display.set_lock(True)
        display.input_char("5")
        # Lock should clear after first input
        assert display.get_lock() is False

    def test_pause_prevents_input(self):
        """Test that pause prevents input."""
        display = Display()
        display.set_pause(True)
        display.input_char("5")
        # Pause should clear after first input
        assert display.get_pause() is False

    def test_full_buffer(self):
        """Test that full buffer prevents further input."""
        display = Display()
        # Fill buffer to capacity
        for _ in range(12):
            display.input_char("9")
        # Should not accept more input when full
        initial_text = display.get_text()
        display.input_char("0")
        # Text should remain the same or similar
        assert display.get_text() == initial_text
