"""
Configuration for HP12C calculator.
Ported from Java Configuration.java.
"""

from typing import List, Optional
from hp12c.model.stack import Stack
from hp12c.model.general_memory import GeneralMemory
from hp12c.model.program_memory import ProgramMemory
from hp12c.model.finance_memory import FinanceMemory
from hp12c.model.step import Step


class KeyMapItem:
    """Key mapping item."""

    def __init__(self, code: int, ch: str):
        """Initialize key map item."""
        self._cd = code
        self._ch = ch

    def set_char(self, ch: str):
        """Set character."""
        self._ch = ch

    def set_code(self, code: int):
        """Set code."""
        self._cd = code

    def get_char(self) -> str:
        """Get character."""
        return self._ch

    def get_code(self) -> int:
        """Get code."""
        return self._cd


class Configuration:
    """Calculator configuration."""

    VERSION = "0.2.8"
    DEFAULT_SKIN = "nigrum"

    DEFAULT_KEYMAP = [
        KeyMapItem(0, '0'), KeyMapItem(1, '1'), KeyMapItem(2, '2'), KeyMapItem(3, '3'),
        KeyMapItem(4, '4'), KeyMapItem(5, '5'), KeyMapItem(6, '6'), KeyMapItem(7, '7'),
        KeyMapItem(8, '8'), KeyMapItem(9, '9'), KeyMapItem(10, '/'), KeyMapItem(11, 'n'),
        KeyMapItem(12, 'i'), KeyMapItem(13, 'p'), KeyMapItem(14, 'm'), KeyMapItem(15, 'v'),
        KeyMapItem(16, 'h'), KeyMapItem(20, '*'), KeyMapItem(21, '!'), KeyMapItem(22, '\\'),
        KeyMapItem(23, '#'), KeyMapItem(24, '$'), KeyMapItem(25, '%'), KeyMapItem(26, 'e'),
        KeyMapItem(30, '-'), KeyMapItem(31, '['), KeyMapItem(32, ']'), KeyMapItem(33, 'd'),
        KeyMapItem(34, 'y'), KeyMapItem(35, 'c'), KeyMapItem(36, '\n'), KeyMapItem(40, '+'),
        KeyMapItem(41, 'o'), KeyMapItem(42, 'f'), KeyMapItem(43, 'g'), KeyMapItem(44, 's'),
        KeyMapItem(45, 'r'), KeyMapItem(48, '.'), KeyMapItem(49, 'w')
    ]

    def __init__(self):
        """Initialize configuration."""
        self._size = 0.75
        self._xpos = 0
        self._ypos = 0
        self._skin = Configuration.DEFAULT_SKIN
        self._lang = "en"
        self._ui_framework = "tkinter"  # UI framework: "tkinter" or "pyqt5"
        self._stksize = 4
        self._memsize = 20
        self._prgsize = 100
        self._c = 0
        self._dmy = 0
        self._com = 0
        self._alg = 0
        self._beg = 0
        self._fix = 9
        self._mode = 0
        self._keymap = [KeyMapItem(item.get_code(), item.get_char()) for item in Configuration.DEFAULT_KEYMAP]
        self.set_defaults()

    def set_defaults(self):
        """Set default values."""
        self.set_size(0.75)
        self.set_fix(9)
        self.set_skin(Configuration.DEFAULT_SKIN)
        self.set_language("en")
        self.set_ui_framework("tkinter")  # Default to Tkinter
        self.set_stack_size(4)
        self.set_memory_size(20)
        self.set_program_size(100)
        self._keymap = [KeyMapItem(item.get_code(), item.get_char()) for item in Configuration.DEFAULT_KEYMAP]

    def get_key_map_item(self, index: int) -> Optional[KeyMapItem]:
        """Get key map item at index."""
        if index < len(self._keymap):
            return self._keymap[index]
        return None

    def set_char(self, code: int, ch: str):
        """Set character for code."""
        idx = self.get_code_index(code)
        if idx != -1:
            self._keymap[idx].set_char(ch)
        else:
            # Add new key map item
            self._keymap.append(KeyMapItem(code, ch))

    def get_code_index(self, code: int) -> int:
        """Get index for code."""
        for i in range(len(self._keymap)):
            if self._keymap[i].get_code() == code:
                return i
        return -1

    def get_code(self, ch: str) -> int:
        """Get code for character."""
        ch_upper = ch.upper()
        for item in self._keymap:
            if item.get_char().upper() == ch_upper:
                return item.get_code()
        return -1

    # Setters
    def set_size(self, size: float):
        self._size = size

    def set_x_pos(self, xpos: int):
        self._xpos = xpos

    def set_y_pos(self, ypos: int):
        self._ypos = ypos

    def set_skin(self, skin_name: str):
        self._skin = skin_name

    def set_language(self, lang_code: str):
        self._lang = lang_code

    def set_ui_framework(self, framework: str):
        """Set UI framework preference."""
        if framework not in ["tkinter", "pyqt5"]:
            raise ValueError(f"Invalid UI framework: {framework}. Must be 'tkinter' or 'pyqt5'")
        self._ui_framework = framework

    def set_stack_size(self, size: int):
        self._stksize = size

    def set_memory_size(self, size: int):
        self._memsize = size

    def set_program_size(self, size: int):
        self._prgsize = size

    def set_c(self, bool_val: int):
        self._c = bool_val

    def set_dmy(self, bool_val: int):
        self._dmy = bool_val

    def set_com(self, bool_val: int):
        self._com = bool_val

    def set_alg(self, bool_val: int):
        self._alg = bool_val

    def set_beg(self, bool_val: int):
        self._beg = bool_val

    def set_fix(self, fix: int):
        self._fix = fix

    def set_mode(self, mode: int):
        self._mode = mode

    def set_key_map(self, key_map: List[KeyMapItem]):
        self._keymap = key_map

    # Getters
    def get_size(self) -> float:
        return self._size

    def get_x_pos(self) -> int:
        return self._xpos

    def get_y_pos(self) -> int:
        return self._ypos

    def get_skin(self) -> str:
        return self._skin

    def get_language(self) -> str:
        return self._lang

    def get_ui_framework(self) -> str:
        """Get UI framework preference."""
        return self._ui_framework

    def get_stack_size(self) -> int:
        return self._stksize

    def get_memory_size(self) -> int:
        return self._memsize

    def get_program_size(self) -> int:
        return self._prgsize

    def get_c(self) -> int:
        return self._c

    def get_dmy(self) -> int:
        return self._dmy

    def get_com(self) -> int:
        return self._com

    def get_alg(self) -> int:
        return self._alg

    def get_beg(self) -> int:
        return self._beg

    def get_fix(self) -> int:
        return self._fix

    def get_mode(self) -> int:
        return self._mode

    def get_key_map(self) -> List[KeyMapItem]:
        return self._keymap

    # Factory methods
    @staticmethod
    def create_stack(size: int) -> Stack:
        return Stack(size)

    def create_stack_instance(self) -> Stack:
        return Configuration.create_stack(self.get_stack_size())

    @staticmethod
    def create_general_memory(size: int) -> GeneralMemory:
        return GeneralMemory(size)

    def create_general_memory_instance(self) -> GeneralMemory:
        return Configuration.create_general_memory(self.get_memory_size())

    @staticmethod
    def create_program_memory(size: int) -> ProgramMemory:
        return ProgramMemory(size)

    def create_program_memory_instance(self) -> ProgramMemory:
        return Configuration.create_program_memory(self.get_program_size())

    @staticmethod
    def create_finance_memory() -> FinanceMemory:
        return FinanceMemory()

    @staticmethod
    def create_step() -> Step:
        return Step()

    @staticmethod
    def create_configuration() -> 'Configuration':
        return Configuration()
