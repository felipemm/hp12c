"""
Date utility functions.
Ported from Java Date.java.
"""

import datetime
from hp12c.hp12c_math.number import Number
from hp12c.model.stack import Stack


class DateUtils:
    """Date calculation utilities."""

    @staticmethod
    def number_to_date(number: Number, dmy: bool) -> datetime.datetime:
        """Convert number to date."""
        return Stack.number_to_date(number, dmy)

    @staticmethod
    def date_to_number(date: datetime.datetime, dmy: bool) -> Number:
        """Convert date to number."""
        return Stack.date_to_number(date, dmy)
