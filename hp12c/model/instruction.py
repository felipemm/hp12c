"""
Instruction class for history.
Ported from Java Instruction.java.
"""


from hp12c.model.stack import Stack
from hp12c.model.step import Step


class Instruction:
    """Represents an instruction with step and stack state."""

    def __init__(self, stp: Step | None = None, stk: Stack | None = None):
        """Initialize instruction."""
        if stp is not None:
            self._stp = Step(stp=stp)
        else:
            self._stp = Step()

        if stk is not None:
            self._stk = Stack(other=stk)
        else:
            self._stk = Stack()

        self.init()

    def init(self):
        """Initialize instruction (no-op)."""
        pass

    def set_step(self, stp: Step):
        """Set step."""
        self._stp.set_modifier(stp.get_modifier())
        self._stp.set_key(stp.get_key())
        self._stp.set_complement(stp.get_complement())

    def set_stack(self, stk: Stack):
        """Set stack."""
        self._stk = Stack(other=stk)

    def get_step(self) -> Step:
        """Get step."""
        return self._stp

    def get_stack(self) -> Stack:
        """Get stack."""
        return self._stk

    def clear(self):
        """Clear instruction."""
        self._stp.clear()
        self._stk.clear()

    def __str__(self) -> str:
        """String representation."""
        result = "==[INSTRUCTION]=====\n"
        result += " - Instr: "
        result += f"{self._stp.get_modifier()}, "
        result += f"{self._stp.get_key()}, "
        result += f"{self._stp.get_complement()}, "
        result += f"{self._stk.get(0)}\n"
        return result
