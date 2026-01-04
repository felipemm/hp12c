"""
Step class for program instructions.
Ported from Java Step.java.
"""

from typing import List, Optional


class Step:
    """Represents a program step with modifier, key, and complement."""

    def __init__(self, mod: int = -1, key: int = -1, cpm: int = -1, stp: Optional['Step'] = None, stp_array: Optional[List[int]] = None):
        """Initialize step."""
        if stp is not None:
            self._mod = stp.get_modifier()
            self._key = stp.get_key()
            self._cpm = stp.get_complement()
        elif stp_array is not None:
            self._mod = stp_array[0]
            self._key = stp_array[1]
            self._cpm = stp_array[2]
        else:
            self._mod = mod
            self._key = key
            self._cpm = cpm

        if mod == -1 and key == -1 and cpm == -1 and stp is None and stp_array is None:
            self.set_undefined()

        self.init()

    def init(self):
        """Initialize step (no-op)."""
        pass

    def set_step(self, mod: int, key: int, cpm: int):
        """Set step values."""
        self._mod = mod
        self._key = key
        self._cpm = cpm
        self.init()

    def get_modifier(self) -> int:
        """Get modifier."""
        return self._mod

    def get_key(self) -> int:
        """Get key."""
        return self._key

    def get_complement(self) -> int:
        """Get complement."""
        return self._cpm

    def set_modifier(self, mod: int):
        """Set modifier."""
        self._mod = mod

    def set_key(self, key: int):
        """Set key."""
        self._key = key

    def set_complement(self, cpm: int):
        """Set complement."""
        self._cpm = cpm

    def get_array(self) -> List[int]:
        """Get step as array."""
        return [self.get_modifier(), self.get_key(), self.get_complement()]

    def clear(self):
        """Clear step."""
        self._mod = -1
        self._key = -1
        self._cpm = -1

    def is_undefined(self) -> bool:
        """Check if step is undefined."""
        return Step.is_undefined_static(self)

    @staticmethod
    def is_undefined_static(step: 'Step') -> bool:
        """Check if step is undefined."""
        return step._mod == -1 or step._key == -1 or step._cpm == -1

    def set_undefined(self):
        """Set step to undefined."""
        Step.set_undefined_static(self)

    @staticmethod
    def set_undefined_static(step: 'Step'):
        """Set step to undefined."""
        step.clear()

    @staticmethod
    def get_undefined() -> 'Step':
        """Get undefined step."""
        return Step()

    def __str__(self) -> str:
        """String representation."""
        from ..calculator.key import Key
        result = "==[STEP]============\n"
        result += f"Modifier: [{Key.get_name(self._mod)}]\n"
        result += f"Function: [{Key.get_name(self._key)}]\n"
        return result

    def equals(self, stp: 'Step') -> bool:
        """Check if equal to another step."""
        return (self.get_modifier() == stp.get_modifier() and
                self.get_key() == stp.get_key() and
                self.get_complement() == stp.get_complement())

    def set_step_from_step(self, stp: 'Step'):
        """Set step from another step."""
        self.set_modifier(stp.get_modifier())
        self.set_key(stp.get_key())
        self.set_complement(stp.get_complement())

    def set_array_from_array(self, step: List[int]):
        """Set step from array."""
        self.set_modifier(step[0])
        self.set_key(step[1])
        self.set_complement(step[2])

    def is_financial_step(self) -> bool:
        """Check if step is a financial step."""
        # This would need Key constants - simplified for now
        return self._key in [11, 12, 13, 14, 15]  # N, I, PV, PMT, FV
