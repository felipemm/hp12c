"""
Memory persistence using JSON.
Ported from Java MemoryDAO.java (using JSON instead of XML).
"""

import json
import os
from pathlib import Path
from hp12c_python_java_port.calculator.config import Configuration
from hp12c_python_java_port.model.stack import Stack
from hp12c_python_java_port.model.finance_memory import FinanceMemory
from hp12c_python_java_port.model.general_memory import GeneralMemory
from hp12c_python_java_port.model.program_memory import ProgramMemory
from hp12c_python_java_port.hp12c_math.number import Number


class MemoryDAO:
    """Data access object for memory persistence."""

    def __init__(self, cfg: Configuration):
        """Initialize memory DAO."""
        self._path = Path("data") / "mem.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._stk = Configuration.create_stack(cfg.get_stack_size())
        self._fin = Configuration.create_finance_memory()
        self._mem = Configuration.create_general_memory(cfg.get_memory_size())
        self._prg = Configuration.create_program_memory(cfg.get_program_size())
        self.create_memory()

    def get_stack(self) -> Stack:
        """Get stack."""
        return self._stk

    def get_finance_memory(self) -> FinanceMemory:
        """Get finance memory."""
        return self._fin

    def get_general_memory(self) -> GeneralMemory:
        """Get general memory."""
        return self._mem

    def get_program_memory(self) -> ProgramMemory:
        """Get program memory."""
        return self._prg

    def set_stack(self, stk: Stack):
        """Set stack."""
        self._stk = stk

    def set_finance_memory(self, fin: FinanceMemory):
        """Set finance memory."""
        self._fin = fin

    def set_general_memory(self, mem: GeneralMemory):
        """Set general memory."""
        self._mem = mem

    def set_program_memory(self, prg: ProgramMemory):
        """Set program memory."""
        self._prg = prg

    def create_memory(self):
        """Load memory from file."""
        if not self._path.exists():
            return

        try:
            with open(self._path, 'r') as f:
                data = json.load(f)

            # Load stack
            if 'stack' in data:
                for i, val in enumerate(data['stack']):
                    if i < self._stk.get_size():
                        self._stk.set(i, Number.n(str(val)))

            # Load finance memory
            if 'finance' in data:
                for i, val in enumerate(data['finance']):
                    if i < self._fin.get_size():
                        self._fin.set(i, Number.n(str(val)))

            # Load general memory
            if 'general' in data:
                for i, item in enumerate(data['general']):
                    if i < self._mem.get_size():
                        if isinstance(item, list) and len(item) >= 2:
                            self._mem.set_with_times(i, Number.n(str(item[0])), Number.n(str(item[1])))
                        else:
                            self._mem.set(i, Number.n(str(item)))

            # Load program memory
            if 'program' in data:
                for i, step_data in enumerate(data['program']):
                    if i < self._prg.get_size():
                        from ..model.step import Step
                        if isinstance(step_data, list) and len(step_data) >= 3:
                            step = Step(step_data[0], step_data[1], step_data[2])
                            self._prg.set(i, step)
        except Exception as e:
            print(f"Error loading memory: {e}")

    def save(self):
        """Save memory to file."""
        data = {
            'stack': [str(self._stk.get(i)) for i in range(self._stk.get_size())],
            'finance': [str(self._fin.get(i)) for i in range(self._fin.get_size())],
            'general': [
                [str(self._mem.get(i)), str(self._mem.get_times(i))]
                for i in range(self._mem.get_size())
            ],
            'program': [
                [
                    self._prg.get_modifier(i),
                    self._prg.get_key(i),
                    self._prg.get_complement(i)
                ]
                for i in range(self._prg.get_size())
            ],
        }

        try:
            with open(self._path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving memory: {e}")
