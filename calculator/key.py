"""
Key enumeration for HP12C calculator.
Ported from Java Key.java enum.
"""

from enum import Enum


class Key(Enum):
    """Calculator key enumeration."""

    KEY_NULL = (-1,)
    KEY_0 = (0,)
    KEY_1 = (1,)
    KEY_2 = (2,)
    KEY_3 = (3,)
    KEY_4 = (4,)
    KEY_5 = (5,)
    KEY_6 = (6,)
    KEY_7 = (7,)
    KEY_8 = (8,)
    KEY_9 = (9,)
    KEY_DIV = (10,)
    KEY_MUL = (20,)
    KEY_SUB = (30,)
    KEY_SUM = (40,)
    KEY_N = (11,)
    KEY_I = (12,)
    KEY_PV = (13,)
    KEY_PMT = (14,)
    KEY_FV = (15,)
    KEY_CHS = (16,)
    KEY_POW = (21,)
    KEY_RECIPROCAL = (22,)
    KEY_PERC_TOT = (23,)
    KEY_PERC_DELTA = (24,)
    KEY_PERC = (25,)
    KEY_EEX = (26,)
    KEY_RS = (31,)
    KEY_SST = (32,)
    KEY_ROLL = (33,)
    KEY_XY = (34,)
    KEY_CLX = (35,)
    KEY_ENTER = (36,)
    KEY_ON = (41,)
    KEY_F = (42,)
    KEY_G = (43,)
    KEY_STO = (44,)
    KEY_RCL = (45,)
    KEY_DOT = (48,)
    KEY_TOT = (49,)

    def __init__(self, code: int):
        """Initialize key with code."""
        self._code = code

    def get_name(self) -> str:
        """Get key name."""
        return self.name

    def get_code(self) -> int:
        """Get key code."""
        return self._code

    @staticmethod
    def get_key(code: int) -> 'Key':
        """Get key by code."""
        for k in Key:
            if k.get_code() == code:
                return k
        return Key.KEY_NULL

    @staticmethod
    def get_key_by_name(name: str) -> 'Key':
        """Get key by name."""
        try:
            return Key[name]
        except KeyError:
            return Key.KEY_NULL

    @staticmethod
    def get_name(code: int) -> str:
        """Get key name by code."""
        if code == -1:
            return ""
        for k in Key:
            if k.get_code() == code:
                return k.name
        return ""

    def __str__(self) -> str:
        """String representation."""
        return f"==[KEY]=============\n{self.name}: {self._code}\n"
