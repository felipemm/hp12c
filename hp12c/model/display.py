"""
Display formatting for HP12C calculator.
Ported from Java Display.java.
"""

import re
from typing import Optional
from hp12c.hp12c_math.number import Number


class Display:
    """Manages calculator display formatting and input."""

    MIN_VALUE = 1.0E-10
    MAX_VALUE = 1.0E10
    ZEROFILL = "0000000000"

    STATUS_READY = 0
    STATUS_INPUT = 1
    STATUS_OUTPUT = 2
    STATUS_OUTPUT2 = 3

    MODE_NORMAL = 0
    MODE_EXPONENTIAL = 1
    MODE_PROGRAM = 2

    def __init__(self):
        """Initialize display."""
        self._buf = "0"
        self._str = ""
        self._msg = ""
        self._val = 0.0
        self._expo = 0
        self._stp = [0, 0, 0, 0]
        self._status = 0
        self._mode = 0
        self._dot = False
        self._neg = False
        self._full = False
        self._lock = False
        self._pause = False
        self._comma = False
        self._prec = 9
        self._bf = []
        self.clear()

    def init(self):
        """Initialize display (no-op in Python)."""
        pass

    def set_message(self, msg: str):
        """Set display message."""
        self._msg = msg

    def set_precision(self, prec: int):
        """Set display precision."""
        self._prec = prec

    def get_precision(self) -> int:
        """Get display precision."""
        return self._prec

    def set_status(self, status: int):
        """Set display status."""
        self._status = status

    def get_status(self) -> int:
        """Get display status."""
        return self._status

    def toggle_comma(self):
        """Toggle comma/dot decimal separator."""
        self.set_comma(not self.get_comma())

    def set_comma(self, comma: bool):
        """Set comma as decimal separator (True) or dot (False)."""
        self._comma = comma

    def get_comma(self) -> bool:
        """Get comma setting."""
        return self._comma

    def set_mode(self, mode: int):
        """Set display mode."""
        self._mode = mode

    def get_mode(self) -> int:
        """Get display mode."""
        return self._mode

    def set_lock(self, lock: bool):
        """Set display lock."""
        self._lock = lock

    def get_lock(self) -> bool:
        """Get display lock."""
        return self._lock

    def set_pause(self, pause: bool):
        """Set pause state."""
        self._pause = pause

    def get_pause(self) -> bool:
        """Get pause state."""
        return self._pause

    def clear(self):
        """Clear display."""
        self._str = ""
        self._buf = "0"
        self._val = 0.0
        self._expo = 0
        self._stp = [0, 0, 0, 0]

    def __str__(self) -> str:
        """String representation."""
        return f"Dsp: {self._str}"

    def input_char(self, ch: str):
        """Input character."""
        if len(ch) != 1:
            return

        if self._lock or self._pause:
            self._lock = False
            self._pause = False
            return

        if self._mode == 0:  # Normal mode
            if ch == '-':
                self._neg = not self._neg
                return

            if self._status != 1:
                self.set_ready()

            if self._full:
                return

            if ch == '.':
                if not self._dot:
                    if self._status != 1:
                        self._dot = True
                        self._status = 1
                        self._buf = "0."
                        return
                    self._dot = True
                    self._buf += "."
                    return
                return

            if self._status != 1:
                if ch == '0':
                    self._buf = "0"
                    self._status = 1
                    return
                self._buf = ch
                self._status = 1
            else:
                self._buf += ch
                if not self._dot:
                    self._buf = str(int(self._buf))

            if self._dot:
                if len(self._buf) >= 11:
                    self._full = True
                    return
            elif len(self._buf) >= 10:
                self._full = True
                return

        elif self._mode == 1:  # Exponential mode
            if ch == '-':
                if self._status != 1:
                    self._neg = not self._neg
                    return
                self._expo = -self._expo
                return

            if self._status != 1:
                self.set_ready()
                self.input_char(ch)
                return

            if self._expo == 0:
                self._expo = int(ch)
            elif self._expo > 0 and self._expo < 10:
                self._expo *= 10
                self._expo += int(ch)
            elif self._expo < 0 and self._expo > -10:
                self._expo *= 10
                self._expo -= int(ch)
            elif self._expo >= 10:
                self._expo *= 10
                self._expo %= 100
                self._expo += int(ch)
            elif self._expo <= -10:
                self._expo *= 10
                self._expo %= 100
                self._expo -= int(ch)

    def input_program_step(self, idx: int, stp):
        """Input program step."""
        from hp12c.model.step import Step
        self._stp = [idx, stp.get_modifier(), stp.get_key(), stp.get_complement()]

    def get_string(self) -> str:
        """Get formatted display string."""
        if self._lock or self._pause:
            return " " + self._msg

        if self._mode != 2:  # Not program mode
            if self._status != 1:
                self.update_value()
                if (abs(self._val) > Display.MIN_VALUE and abs(self._val) < Display.MAX_VALUE) or self._val == 0.0:
                    self._get_normal_string()
                else:
                    self._get_exponential_string()
            elif self._mode == 0:
                self._get_normal_string()
            elif self._mode == 1:
                self._get_exponential_string()
        else:
            self._get_program_string()

        return self._str

    def _digit_separators(self):
        """Add digit separators (thousands separators)."""
        grpcount = 0
        grpchar = ','
        decchar = '.'

        tmp = self._str.split(".")
        if self._comma:
            grpchar = '.'
            decchar = ','

        revstr = ""
        for i in range(len(tmp[0]) - 1, -1, -1):
            grpcount += 1
            if grpcount == 3:
                revstr += tmp[0][i]
                if i > 1:
                    revstr += grpchar
                grpcount = 0
            else:
                revstr += tmp[0][i]

        newstr = [''] * len(revstr)
        for i in range(len(revstr)):
            newstr[len(revstr) - 1 - i] = revstr[i]

        self._str = ''.join(newstr)
        self._str += decchar + (tmp[1] if len(tmp) > 1 else "")

    def _get_exponential_string(self):
        """Get exponential format string."""
        if self._status != 1:
            self._val = float(f"{self._buf}e{self._expo}")
            self._str = str(self._val)
            self._dot = True
            self._bf = self._str.split("E")
            if len(self._bf) > 0:
                self._buf = f"{float(self._bf[0]):.{self._prec}f}"
            self._expo = int(self._bf[1]) if len(self._bf) == 2 else 0

        self._bf = [self._buf, ""]
        if self._dot:
            if len(self._buf) < 8:
                self._bf[0] = self._buf + " " * (8 - len(self._buf))
            else:
                self._bf[0] = self._buf[:8]
        else:
            if len(self._buf) < 7:
                self._bf[0] = self._buf + "."
                self._bf[0] += " " * (7 - len(self._buf))
            else:
                self._bf[0] = self._buf[:7] + "."

        self._bf[0] += " " if self._expo >= 0 else "-"
        self._bf[1] = f"{abs(self._expo):02d}" if abs(self._expo) < 10 else f"{abs(self._expo)}"
        self._str = self._bf[0] + self._bf[1]
        self._str = ("-" if self._neg else " ") + self._str
        self._digit_separators()

    def _get_normal_string(self):
        """Get normal format string."""
        if self._status != 1:
            val_str = f"{self._buf}E{self._expo}"
            self._str = f"{float(val_str):.{self._prec}f}"
            if len(self._str) > 11:
                self._bf = self._str.split(".")
                prec = 10 - len(self._bf[0])
                self._str = f"{float(val_str):.{prec}f}"
            self._bf = self._str.split(".")
            self._str = self._bf[0] + "."
            self._str = ("-" if self._neg else " ") + self._str + (self._bf[1] if len(self._bf) == 2 else "")
        elif self._dot:
            self._str = ("-" if self._neg else " ") + self._buf
        else:
            self._str = ("-" if self._neg else " ") + self._buf + "."

        self._digit_separators()

    def _get_program_string(self):
        """Get program mode string."""
        i, m, k, c = self._stp[0], self._stp[1], self._stp[2], self._stp[3]

        if m > -1 and k > -1 and c > -1:
            if k == 33:
                self._str = f"{Display.zero_pad(i, 3)}-{Display.space_pad(m, 2)},{Display.space_pad(k, 2)},{Display.zero_pad(c, 3)}"
            else:
                c_str = Display.zero_pad(c, 3) if c > 99 else f"r{Display.zero_pad(c, 2)}"
                self._str = f"{Display.zero_pad(i, 3)}-{Display.space_pad(m, 2)},{Display.space_pad(k, 2)},{c_str}"
        elif k > -1 and c > -1:
            c_str = Display.zero_pad(c, 3) if c > 99 else f"r{Display.zero_pad(c, 2)}"
            self._str = f"{Display.zero_pad(i, 3)}-  {Display.space_pad(k, 2)},{c_str}"
        elif m > -1 and k > -1:
            self._str = f"{Display.zero_pad(i, 3)}-  {Display.space_pad(m, 2)},{Display.space_pad(k, 3)}"
        elif k > -1:
            self._str = f"{Display.zero_pad(i, 3)}-    {Display.space_pad(k, 3)}"
        else:
            self._str = f"{Display.zero_pad(i, 3)}-    {Display.zero_pad(0, 3)}"

    def get_mantissa(self) -> str:
        """Get mantissa string."""
        self._bf = self._buf.split(".")
        rtn = self._bf[0] + (self._bf[1] if len(self._bf) == 2 else "")
        rtn += Display.ZEROFILL
        if len(rtn) > 10:
            rtn = rtn[:10]
        return rtn

    def set_value(self, val: Number):
        """Set display value from Number."""
        self._val = val.double_value()
        if (abs(self._val) > Display.MIN_VALUE and abs(self._val) < Display.MAX_VALUE) or self._val == 0.0:
            self._buf = f"{val.abs().d():10.9f}"
            self._expo = 0
            self._neg = val.less_than(Number.ZERO)
        else:
            self._str = str(val.abs())
            self._bf = self._str.split("E")
            self._buf = self._bf[0]
            self._expo = int(self._bf[1]) if len(self._bf) == 2 else 0
            self._neg = val.less_than(Number.ZERO)

    def get_value(self) -> Number:
        """Get value as Number."""
        self.update_value()
        return Number.get_instance(self._val)

    def update_value(self):
        """Update internal value from buffer."""
        try:
            self._bf = ["", ""]
            if self._expo != 0:
                self._bf[0] = f"{self._buf}E{self._expo}"
                self._val = float(self._bf[0])
            else:
                self._bf[0] = self._buf
                self._val = float(self._bf[0])

            if self._neg:
                self._val = -self._val
        except (ValueError, Exception):
            pass

    def set_ready(self):
        """Set display to ready state."""
        self._mode = 0
        self._dot = False
        self._neg = False
        self._full = False
        self._buf = ""
        self._bf = None
        self._expo = 0
        self._val = 0.0

    @staticmethod
    def zero_pad(val: int, size: int) -> str:
        """Zero-pad integer to specified size."""
        v_str = str(val)
        if len(v_str) < size:
            return '0' * (size - len(v_str)) + v_str
        return v_str

    @staticmethod
    def space_pad(val: int, size: int) -> str:
        """Space-pad integer to specified size."""
        v_str = str(val)
        if len(v_str) < size:
            return ' ' * (size - len(v_str)) + v_str
        return v_str
