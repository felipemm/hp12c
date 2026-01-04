"""
Program memory for HP12C calculator.
Ported from Java ProgramMemory.java.
"""

from typing import List, Optional
from hp12c_python_java_port.model.step import Step


class ProgramMemory:
    """Manages program memory and execution."""

    def __init__(self, size: int = 1000, prg: Optional[List[Step]] = None):
        """Initialize program memory."""
        if prg is not None:
            self._prg = prg
        else:
            self._prg = [Step() for _ in range(size)]
        self._idx = 0
        self.init()

    def init(self):
        """Initialize program memory."""
        for i in range(len(self._prg)):
            if self._prg[i] is None:
                self._prg[i] = Step()

    def get_size(self) -> int:
        """Get program memory size."""
        return len(self._prg)

    def get_used_steps(self) -> int:
        """Get number of used steps."""
        i = 1
        while i < len(self._prg):
            if self._prg[i].is_undefined():
                break
            i += 1
        return i - 1

    def get_available_steps(self) -> int:
        """Get number of available steps."""
        return self.get_size() - self.get_used_steps() - 1

    def set(self, idx: int, stp: Step):
        """Set step at index."""
        if idx < len(self._prg):
            self._prg[idx] = stp

    def set_current(self, stp: Step):
        """Set step at current index."""
        if self._idx < len(self._prg):
            self._prg[self._idx] = stp

    def get(self, idx: int) -> Optional[Step]:
        """Get step at index."""
        if idx < len(self._prg):
            return self._prg[idx]
        return None

    def get_current(self) -> Optional[Step]:
        """Get step at current index."""
        if self._idx < len(self._prg):
            return self._prg[self._idx]
        return None

    def next(self) -> bool:
        """Move to next step."""
        if self._idx < len(self._prg) - 1:
            self._idx += 1
            return True
        return False

    def back(self) -> bool:
        """Move to previous step."""
        if self._idx > 0:
            self._idx -= 1
            return True
        return False

    def set_modifier(self, mod: int, idx: Optional[int] = None):
        """Set modifier."""
        target_idx = idx if idx is not None else self._idx
        if target_idx < len(self._prg):
            self._prg[target_idx].set_modifier(mod)

    def set_key(self, key: int, idx: Optional[int] = None):
        """Set key."""
        target_idx = idx if idx is not None else self._idx
        if target_idx < len(self._prg):
            self._prg[target_idx].set_key(key)

    def set_complement(self, cpm: int, idx: Optional[int] = None):
        """Set complement."""
        target_idx = idx if idx is not None else self._idx
        if target_idx < len(self._prg):
            self._prg[target_idx].set_complement(cpm)

    def get_modifier(self, idx: Optional[int] = None) -> int:
        """Get modifier."""
        target_idx = idx if idx is not None else self._idx
        if target_idx < len(self._prg):
            return self._prg[target_idx].get_modifier()
        return -1

    def get_key(self, idx: Optional[int] = None) -> int:
        """Get key."""
        target_idx = idx if idx is not None else self._idx
        if target_idx < len(self._prg):
            return self._prg[target_idx].get_key()
        return -1

    def get_complement(self, idx: Optional[int] = None) -> int:
        """Get complement."""
        target_idx = idx if idx is not None else self._idx
        if target_idx < len(self._prg):
            return self._prg[target_idx].get_complement()
        return -1

    def get_current_index(self) -> int:
        """Get current index."""
        return self._idx

    def set_current_index(self, idx: int):
        """Set current index."""
        if 0 <= idx < len(self._prg):
            self._idx = idx

    def clear(self):
        """Clear program memory."""
        for i in range(len(self._prg)):
            self._prg[i] = Step()
        self._idx = 0

    def __str__(self) -> str:
        """String representation."""
        result = "==[PROGRAM MEMORY]==\n"
        for i in range(min(20, len(self._prg))):  # Show first 20
            if not self._prg[i].is_undefined():
                result += f" - P{i}: {self._prg[i]}\n"
        return result
