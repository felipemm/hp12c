"""
Calculator exceptions.
Ported from Java CalculatorException.java and Error.java.
"""

from enum import Enum


class Error(Enum):
    """Error types for calculator."""

    ERROR_MATH = (0, "Math Error")
    ERROR_SRO = (1, "Storage Register Overflow Error")
    ERROR_STAT = (2, "Statistic Error")
    ERROR_IRR1 = (3, "IRR1 Error")
    ERROR_MEM = (4, "Memory Error")
    ERROR_CI = (5, "Compound Interest Error")
    ERROR_SR = (6, "Storage Registers Error")
    ERROR_IRR2 = (7, "IRR2 Error")
    ERROR_CAL = (8, "Calendar Error")
    ERROR_SERV = (9, "Service Error")
    ERROR_PR = (10, "Post Reset Error")
    ERROR_MAG = (99, "Register overflow")

    def __init__(self, code: int, message: str):
        """Initialize error."""
        self._code = code
        self._message = message

    def get_code(self) -> int:
        """Get error code."""
        return self._code

    def get_message(self) -> str:
        """Get error message."""
        return self._message

    def get_name(self) -> str:
        """Get error name."""
        return self.name

    def __str__(self) -> str:
        """String representation."""
        return f"[ERROR {self._code}] {self._message}"


class CalculatorException(Exception):
    """Calculator-specific exception."""

    def __init__(self, error: Error, detail: str = ""):
        """Initialize exception."""
        super().__init__(detail or error.get_message())
        self._error = error
        self._detail = detail

    def get_error(self) -> Error:
        """Get error."""
        return self._error

    def get_detail(self) -> str:
        """Get detail message."""
        return self._detail

    def get_code(self) -> int:
        """Get error code."""
        return self._error.get_code()

    def get_name(self) -> str:
        """Get error name."""
        return self._error.get_name()

    def get_message(self) -> str:
        """Get error message."""
        return self._error.get_message()

    def __str__(self) -> str:
        """String representation."""
        if self._detail:
            return f"{self._error}: {self._detail}"
        return str(self._error)
