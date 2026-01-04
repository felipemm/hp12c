"""
RPN Stack implementation for HP12C calculator.
Ported from Java Stack.java.
"""

import datetime
from typing import List, Optional
from hp12c.hp12c_math.number import Number


class Stack:
    """4-level RPN stack (X, Y, Z, T registers) with LAST X support."""

    MAX_MAGNITUDE = Number.n(9.999999999).multiply(Number.n(10.0).pow(Number.n(99.0)))
    MIN_MAGNITUDE = Number.n(1.0E-98)

    def __init__(self, size: int = 4, stk: Optional[List[Number]] = None, other: Optional['Stack'] = None):
        """
        Initialize stack.

        Args:
            size: Stack size (default 4)
            stk: Optional array to initialize from
            other: Optional Stack to copy from
        """
        if other is not None:
            stk = other.get_array()
            self._stk = [Number.ZERO] * len(stk)
            self.set_array(stk)
            self._last_top = other.get_last_top()
            self._last_bottom = other.get_last_bottom()
        elif stk is not None:
            self._stk = [Number.ZERO] * len(stk)
            self.set_array(stk)
        else:
            self._stk = [Number.ZERO] * size
            self.clear()

        self._swp = Number.ZERO
        self._last_top = Number.ZERO
        self._last_bottom = Number.ZERO
        self._dmy = False
        self.init()

    def init(self):
        """Initialize last top and bottom."""
        self._last_top = Number.ZERO
        self._last_bottom = Number.ZERO

    def get(self, idx: int) -> Number:
        """Get value at index."""
        return self._stk[idx]

    @staticmethod
    def fit_magnitude(number: Number) -> Number:
        """
        Fit number to valid magnitude range.

        Raises:
            ValueError: If number exceeds maximum magnitude
        """
        if number.abs().greater_than_or_equal_to(Stack.MAX_MAGNITUDE):
            raise ValueError(f"Number larger than or equal to {Stack.MAX_MAGNITUDE.double_value()}")
        if number.abs().lt(Stack.MIN_MAGNITUDE):
            return Number.ZERO
        return number

    def set(self, idx: int, val: Number):
        """Set value at index, fitting magnitude."""
        try:
            self._stk[idx] = Stack.fit_magnitude(val)
        except ValueError:
            # If magnitude error, set to max/min
            self._stk[idx] = Stack.MAX_MAGNITUDE.negate() if val.is_negative() else Stack.MAX_MAGNITUDE

    def put(self, val: Number):
        """Put value on top of stack (shifts down)."""
        self.shift_down()
        self.set(0, val)

    def get_array(self) -> List[Number]:
        """Get stack as array."""
        return self._stk.copy()

    def set_array(self, stk: List[Number]):
        """Set stack from array."""
        for i in range(len(stk)):
            self.set(i, stk[i])

    def pop(self) -> Number:
        """Pop top value (shifts up)."""
        self._swp = self._stk[0]
        self.shift_up()
        return self._swp

    def top(self) -> Number:
        """Get top value without popping."""
        return self._stk[0]

    def bottom(self) -> Number:
        """Get bottom value."""
        return self._stk[self.get_size() - 1]

    def get_size(self) -> int:
        """Get stack size."""
        return len(self._stk)

    def clear(self):
        """Clear stack (set all to zero)."""
        for i in range(len(self._stk)):
            self._stk[i] = Number.ZERO

    def shift_down(self):
        """Shift stack down (for entering new value)."""
        self.set_last_bottom()
        for i in range(len(self._stk) - 1, 0, -1):
            self._stk[i] = self._stk[i - 1]

    def shift_up(self):
        """Shift stack up (after popping)."""
        for i in range(len(self._stk) - 1):
            self._stk[i] = self._stk[i + 1]
        self._stk[len(self._stk) - 1] = Number.ZERO

    def roll_up(self):
        """Roll stack up (bottom to top)."""
        self._swp = self._stk[len(self._stk) - 1]
        self.shift_down()
        self._stk[0] = self._swp

    def roll_down(self):
        """Roll stack down (top to bottom)."""
        self._swp = self._stk[0]
        self.shift_up()
        self._stk[len(self._stk) - 1] = self._swp

    def __str__(self) -> str:
        """String representation."""
        result = "==[STACK]===========\n"
        for i in range(len(self._stk)):
            result += f" - S{i}: {self._stk[i]}\n"
        return result

    def swap_top_pair(self):
        """Swap top two stack values."""
        self._swp = self._stk[1]
        self._stk[1] = self._stk[0]
        self._stk[0] = self._swp

    def lower_top_pair(self):
        """Lower top pair if top > second."""
        if self._stk[0].greater_than(self._stk[1]):
            self._swp = self._stk[1]
            self._stk[1] = self._stk[0]
            self._stk[0] = self._swp

    def set_last_top(self, top: Optional[Number] = None):
        """Set last top value."""
        if top is None:
            self._last_top = self._stk[0]
        else:
            self._last_top = top

    def get_last_top(self) -> Number:
        """Get last top value (LAST X register)."""
        return self._last_top

    def clear_last_top(self):
        """Clear last top value."""
        self._last_top = Number.ZERO

    def set_last_bottom(self, bottom: Optional[Number] = None):
        """Set last bottom value."""
        if bottom is None:
            self._last_bottom = self._stk[self.get_size() - 1]
        else:
            self._last_bottom = bottom

    def get_last_bottom(self) -> Number:
        """Get last bottom value."""
        return self._last_bottom

    def clear_last_bottom(self):
        """Clear last bottom value."""
        self._last_bottom = Number.ZERO

    def is_dmy(self) -> bool:
        """Check if DMY date format."""
        return self._dmy

    def set_dmy(self, dmy: bool):
        """Set DMY date format."""
        self._dmy = dmy

    # Arithmetic operations

    def add(self):
        """Add: y + x."""
        x = self.pop()
        y = self.pop()
        self.put(y.add(x))
        self.set_last_top(x)

    def subtract(self):
        """Subtract: y - x."""
        x = self.pop()
        y = self.pop()
        self.put(y.subtract(x))
        self.set_last_top(x)

    def multiply(self):
        """Multiply: y * x."""
        x = self.pop()
        y = self.pop()
        self.put(y.multiply(x))
        self.set_last_top(x)

    def divide(self):
        """Divide: y / x."""
        x = self.pop()
        y = self.pop()
        if x.is_zero():
            raise ZeroDivisionError("Division by ZERO")
        self.put(y.divide(x))
        self.set_last_top(x)

    def remainder(self):
        """Remainder: y % x."""
        x = self.pop()
        y = self.pop()
        self.put(y.remainder(x))
        self.set_last_top(x)

    def negate(self):
        """Negate top value."""
        x = self.pop()
        self.put(x.negate())
        self.set_last_top(x)

    def squared(self):
        """Square top value."""
        x = self.pop()
        self.put(x.pow(Number.TWO))
        self.set_last_top(x)

    def sqrt(self):
        """Square root of top value."""
        x = self.pop()
        self.put(x.sqrt())
        self.set_last_top(x)

    def reciprocal(self):
        """Reciprocal (1/x) of top value."""
        x = self.pop()
        self.put(x.reciprocal())
        self.set_last_top(x)

    def integral_part(self):
        """Integral part of top value."""
        x = self.pop()
        self.set(0, x.integral_part())
        self.set_last_top(x)

    def fractional_part(self):
        """Fractional part of top value."""
        x = self.pop()
        self.set(0, x.fractional_part())
        self.set_last_top(x)

    def pow(self):
        """Power: base^exponent."""
        exponent = self.pop()
        base = self.pop()
        self.put(base.pow(exponent))
        self.set_last_top(exponent)

    def exp(self):
        """Exponential: e^x."""
        exponent = self.pop()
        self.put(exponent.exp())
        self.set_last_top(exponent)

    def log(self):
        """Natural logarithm."""
        x = self.pop()
        self.put(x.log())
        self.set_last_top(x)

    def factorial(self):
        """Factorial of top value."""
        base = self.pop()
        self.put(base.factorial())
        self.set_last_top(base)

    def round(self, scale: int):
        """Round top value to scale."""
        x = self.pop()
        self.put(x.round(scale))
        self.set_last_top(x)

    def percent(self):
        """Percent: base * rate / 100."""
        rate = self.pop()
        base = self.pop()
        ans = base.multiply(rate).divide(Number.HUNDRED)
        self.put(base)
        self.put(ans)
        self.set_last_top(rate)

    def percent_difference(self):
        """Percent difference: 100 * (other - base) / base."""
        other = self.pop()
        base = self.pop()
        ans = Number.HUNDRED.multiply(other.subtract(base).divide(base))
        self.put(base)
        self.put(ans)
        self.set_last_top(other)

    def percent_of_total(self):
        """Percent of total: 100 * other / total."""
        other = self.pop()
        total = self.pop()
        ans = Number.HUNDRED.multiply(other.divide(total))
        self.put(total)
        self.put(ans)
        self.set_last_top(other)

    # Date operations

    @staticmethod
    def number_to_date(number: Number, dmy: bool) -> datetime.datetime:
        """
        Convert number to date.

        Args:
            number: Date as number (MM.DDYYYY or DD.MMYYYY)
            dmy: True for DD.MMYYYY, False for MM.DDYYYY

        Returns:
            datetime object
        """
        m = number.round(0).int_value()
        d = number.fractional_part().multiply(Number.HUNDRED).round(0).int_value()
        y = number.fractional_part().multiply(Number.HUNDRED).fractional_part().multiply(Number.n(10000.0)).round(0).int_value()

        if dmy:
            tmp = d
            d = m
            m = tmp

        try:
            return datetime.datetime(y, m, d, 0, 0, 0)
        except Exception:
            raise ValueError("Invalid date")

    @staticmethod
    def date_to_number(date: datetime.datetime, dmy: bool) -> Number:
        """
        Convert date to number.

        Args:
            date: datetime object
            dmy: True for DD.MMYYYY, False for MM.DDYYYY

        Returns:
            Number representing date
        """
        day = f"{date.day:02d}"
        month = f"{date.month:02d}"
        year = f"{date.year:04d}"

        if dmy:
            str_number = f"{day}.{month}{year}"
        else:
            str_number = f"{month}.{day}{year}"

        return Number.n(str_number)

    @staticmethod
    def _add_days(number: Number, days: Number, dmy: bool) -> datetime.datetime:
        """Add days to date."""
        calendar = Stack.number_to_date(number, dmy)
        delta = datetime.timedelta(days=days.int_value())
        return calendar + delta

    @staticmethod
    def _diff_dates_365(beg_date: datetime.datetime, end_date: datetime.datetime) -> Number:
        """Difference in days using 365-day year."""
        delta = end_date - beg_date
        return Number.n(delta.days)

    @staticmethod
    def _diff_dates_360(beg_date: datetime.datetime, end_date: datetime.datetime) -> Number:
        """Difference in days using 360-day year."""
        dd1 = beg_date.day
        mm1 = beg_date.month
        yyyy1 = beg_date.year
        dd2 = end_date.day
        mm2 = end_date.month
        yyyy2 = end_date.year

        z1 = 30 if dd1 == 31 else dd1
        if dd2 == 31 and dd1 >= 30:
            z2 = 30
        elif dd2 == 31 and dd1 < 30:
            z2 = dd2
        elif dd2 < 31:
            z2 = dd2
        else:
            z2 = dd2

        date1 = yyyy1 * 360 + mm1 * 30 + z1
        date2 = yyyy2 * 360 + mm2 * 30 + z2
        return Number.n(date2 - date1)

    def add_days_to_date(self):
        """Add days to date on stack."""
        days = self.pop()
        number = self.pop()
        calendar = Stack._add_days(number, days, self._dmy)
        date_number = Stack.date_to_number(calendar, self._dmy)
        self.put(date_number)
        self.set_last_top(days)

    def diff_of_days_between_dates(self):
        """Calculate difference in days between two dates."""
        x = self.pop()
        y = self.pop()
        beg_date = Stack.number_to_date(y, self._dmy)
        end_date = Stack.number_to_date(x, self._dmy)
        diff360 = Stack._diff_dates_360(beg_date, end_date)
        diff365 = Stack._diff_dates_365(beg_date, end_date)
        self.put(diff360)
        self.put(diff365)
        self.set_last_top(x)

    def day_of_week(self) -> Number:
        """Get day of week (1=Monday, 7=Sunday)."""
        date = self.top()
        calendar = Stack.number_to_date(date, self._dmy)
        dow = calendar.weekday() + 1  # Python: Monday=0, Sunday=6; HP12C: Monday=1, Sunday=7
        return Number.n(dow)
