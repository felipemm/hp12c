"""
Operation history for HP12C calculator.
Ported from Java History.java.
"""

from hp12c.model.instruction import Instruction


class History:
    """Manages operation history."""

    def __init__(self, size: int = 100, hst: list[Instruction] | None = None):
        """Initialize history."""
        if hst is not None:
            self._instr: list[Instruction | None] = [None] * len(hst)
            for i in range(len(hst)):
                self._instr[i] = hst[i]
        else:
            self._instr = [None] * size
        self._swp: Instruction | None = None
        self.init()

    def init(self):
        """Initialize history (no-op)."""
        pass

    def get(self, index: int) -> Instruction | None:
        """Get instruction at index."""
        return self._instr[index]

    def set(self, index: int, instr: Instruction):
        """Set instruction at index."""
        self._instr[index] = instr

    def shift_up(self):
        """Shift history up."""
        for i in range(len(self._instr) - 1, 0, -1):
            self._instr[i] = self._instr[i - 1]

    def shift_down(self):
        """Shift history down."""
        for i in range(len(self._instr) - 1):
            self._instr[i] = self._instr[i + 1]

    def put(self, instr: Instruction):
        """Put instruction at top."""
        self.shift_up()
        self._instr[0] = instr

    def pop(self) -> Instruction | None:
        """Pop instruction from top."""
        self._swp = self._instr[0]
        self.shift_down()
        return self._swp

    def top(self) -> Instruction | None:
        """Get top instruction."""
        return self._instr[0]

    def get_size(self) -> int:
        """Get history size."""
        return len(self._instr)

    def __str__(self) -> str:
        """String representation."""
        result = "---Program Memory---\n"
        for i in range(len(self._instr)):
            instr = self._instr[i]
            if instr is not None:
                stp = instr.get_step()
                stk = instr.get_stack()
                result += f" - H{i}: {stp.get_modifier()}, {stp.get_key()}, {stp.get_complement()}, {stk.get(0)}\n"
        return result

    def clear(self):
        """Clear history."""
        for i in range(len(self._instr)):
            instr = self._instr[i]
            if instr is not None:
                instr.clear()
