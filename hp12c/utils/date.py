"""
Date class for HP12C calculator.
Ported from Java Date.java.
"""

import math
from typing import Optional


class Date:
    """Date class for calendar calculations."""

    # Day constants
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7

    # Month constants
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12

    WEEK_DAYS = ["", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    MONTHS = [
        "",
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]

    def __init__(
        self,
        year: int | None = None,
        month: int | None = None,
        day: int | None = None,
        serial: int | None = None,
        date: Optional["Date"] = None,
    ):
        """Initialize Date."""
        self._day = 0
        self._month = 0
        self._year = 0
        self._error = "No errors found"
        self._valid = False

        if serial is not None:
            self.set_date(serial)
        elif date is not None:
            self._day = date.get_day()
            self._month = date.get_month()
            self._year = date.get_year()
            self._error = "No errors found"
            self.validate()
        elif year is not None and month is not None and day is not None:
            self._day = day
            self._month = month
            self._year = year
            self._error = "No errors found"
            self.validate()
        else:
            self._error = "No errors found"

    @staticmethod
    def get_instance(year: int, month: int, day: int) -> "Date":
        """Factory method to create Date instance."""
        return Date(year, month, day)

    def set_date(self, serial: int):
        """Set date from serial number."""
        dt = Date.serial_to_date(serial)
        self._day = dt.get_day()
        self._month = dt.get_month()
        self._year = dt.get_year()

    def set_date_from_date(self, date: "Date"):
        """Set date from another Date."""
        self._day = date.get_day()
        self._month = date.get_month()
        self._year = date.get_year()

    def set_day(self, day: int):
        """Set day with automatic month/year adjustment."""
        y = self._year
        m = self._month
        d = 0

        if day < 1:
            i = 0
            while i < abs(day):
                if d <= 1:
                    if m == 1:
                        d = 31
                        m = 13
                        y -= 1
                    elif m == 2:
                        d = 31
                    elif m == 3:
                        d = 29 if self.is_gregorian_leap_year(y) else 28
                    elif m == 4:
                        d = 31
                    elif m == 5:
                        d = 30
                    elif m == 6:
                        d = 31
                    elif m == 7:
                        d = 30
                    elif m == 8 or m == 9:
                        d = 31
                    elif m == 10:
                        d = 30
                    elif m == 11:
                        d = 31
                    elif m == 12:
                        d = 30
                    m -= 1
                else:
                    d -= 1
                i += 1
            self._day = d
            self._month = m
            self._year = y
        elif day > 27:
            i = 0
            while i < abs(day) + 1:
                d += 1
                if m == 2:
                    if not self.is_gregorian_leap_year(y):
                        if d > 28:
                            d = 1
                            m += 1
                    elif d > 29:
                        d = 1
                        m += 1
                elif m in [1, 3, 5, 7, 8, 10]:
                    if d > 31:
                        d = 1
                        m += 1
                elif m in [4, 6, 9, 11]:
                    if d > 30:
                        d = 1
                        m += 1
                elif m == 12 and d > 31:
                    d = 1
                    m = 1
                    y += 1
                i += 1
            self._day = d
            self._month = m
            self._year = y
        else:
            self._day = day
        self.validate()

    def set_month(self, month: int):
        """Set month with automatic year adjustment."""
        if month < 1:
            tmp = [abs(month + 1) % 12, abs(month) // 12]
            self._month = 12 - tmp[0]
            self._year -= tmp[1] + 1
            if self._month == 12:
                self._month = 1
                self._year += 1
            else:
                self._month += 1
        elif month > 12:
            tmp = [month % 12, month // 12]
            self._month = tmp[0] + 1
            self._year += tmp[1]
        else:
            self._month = month
        self.validate()

    def set_year(self, year: int):
        """Set year."""
        self._year = year
        self.validate()

    def get_date(self) -> "Date":
        """Get date (returns self)."""
        return self

    def get_day(self) -> int:
        """Get day."""
        return self._day

    def get_month(self) -> int:
        """Get month."""
        return self._month

    def get_year(self) -> int:
        """Get year."""
        return self._year

    def get_error(self) -> str:
        """Get error message."""
        return self._error

    def is_valid(self) -> bool:
        """Check if date is valid."""
        return self._valid

    def validate(self):
        """Validate date."""
        self._valid = True
        y = float(self._year)
        m = float(self._month)
        d = float(self._day)

        if y > 9999.0 or y <= 0.0:
            self._error = "Invalid year"
            self._valid = False
        elif m > 12.0 or m <= 0.0:
            self._error = "Invalid month"
            self._valid = False
        elif d <= 0.0:
            self._error = "Invalid day"
            self._valid = False
        elif m == 2.0:
            if not self.is_gregorian_leap_year(y):
                if d > 28.0 or d <= 0.0:
                    self._error = "February with more than 28 days in a not leapyear"
                    self._valid = False
            elif d > 29.0 or d <= 0.0:
                self._error = "February with more than 29 days in a leapyear"
                self._valid = False
        elif m in [1.0, 3.0, 5.0, 7.0, 8.0, 10.0, 12.0]:
            if d > 31.0 or d <= 0.0:
                self._error = f"Month of {self.MONTHS[int(m)]} with more than 31 days"
                self._valid = False
        elif m in [4.0, 6.0, 9.0, 11.0]:
            if d > 30.0 or d <= 0.0:
                self._error = f"Month of {self.MONTHS[int(m)]} with more than 30 days"
                self._valid = False

    def get_week_day(self) -> int:
        """Get weekday (1=Monday, 7=Sunday)."""
        if self._valid:
            serial = (self.get_serial() - 1) % 7
            return int(serial if serial != 0 else 7)
        return 0

    def get_week_day_string(self) -> str:
        """Get weekday name."""
        if self._valid:
            return self.WEEK_DAYS[self.get_week_day()]
        return ""

    def gregorian_to_julian(self, d: float, m: float, y: float) -> float:
        """Convert Gregorian date to Julian day number."""
        GREGORIAN_EPOCH = 1721425.5
        return (
            GREGORIAN_EPOCH
            - 1.0
            + 365.0 * (y - 1.0)
            + math.floor((y - 1.0) / 4.0)
            - math.floor((y - 1.0) / 100.0)
            + math.floor((y - 1.0) / 400.0)
            + math.floor((367.0 * m - 362.0) / 12.0)
            + (0 if m <= 2.0 else (-1 if self.is_gregorian_leap_year(y) else -2))
            + d
        )

    def is_gregorian_leap_year(self, year: float) -> bool:
        """Check if year is a Gregorian leap year."""
        return year % 4.0 == 0.0 and (year % 100.0 != 0.0 or year % 400.0 == 0.0)

    def julian_week_day(self, day: float) -> float:
        """Get weekday from Julian day."""
        w = math.floor(day + 1.5) % 7.0
        return w

    def get_serial(self) -> int:
        """Get serial date number."""
        dd = float(self._day)
        mm = float(self._month)
        yyyy = float(self._year)
        x = 0.0
        z = 0.0

        if mm <= 2.0:
            x = 0.0
            z = yyyy - 1.0
        else:
            x = int(0.4 * mm + 2.3)
            z = yyyy

        dt = 365.0 * yyyy + 31.0 * (mm - 1.0) + dd + float(int(z / 4.0)) - x
        dt -= 693973.0

        i = 1899
        while float(i) < yyyy:
            if i % 100 == 0 and i % 400 != 0:
                dt -= 1.0
            i += 1

        return int(dt)

    @staticmethod
    def serial_to_date(valor: int) -> "Date":
        """Convert serial number to Date."""
        dt = Date()
        result = 0
        y = 8192.0
        begin_loop = 8192.0

        a = 0
        while a < 100:
            m = 1
            while m < 13:
                d = 1
                while d < 32:
                    dt.set_day(d)
                    dt.set_month(m)
                    dt.set_year(int(round(y)))
                    result = dt.get_serial()
                    if result > valor:
                        y -= begin_loop / (2.0**a)
                    elif result < valor:
                        y += begin_loop / (2.0**a)
                    elif dt.is_valid():
                        d = 32
                        m = 13
                        a = 100
                    d += 1
                m += 1
            a += 1

        return dt

    def get_commercial_serial(self) -> int:
        """Get commercial serial (360-day year)."""
        d1 = 29
        m1 = 11
        a1 = 1899
        z1 = 0.0
        d2 = self._day
        m2 = self._month
        a2 = self._year
        z2 = 0.0

        if d1 == 30:
            z1 = 30.0
        elif d1 != 31:
            z1 = float(d1)

        if d2 == 31 and (d1 == 30 or d1 == 31):
            z2 = 30.0
        elif d2 == 31 and d1 < 30 or d2 < 31:
            z2 = float(d2)

        try:
            fDT1 = float(360 * a1 + 30 * m1) + z1
            fDT2 = float(360 * a2 + 30 * m2) + z2
            retorno = fDT2 - fDT1
        except Exception:
            retorno = 0.0

        return int(retorno)

    @staticmethod
    def diff_dates(beg_date: "Date", end_date: "Date") -> int:
        """Calculate difference in days between two dates."""
        a = beg_date.get_serial()
        b = end_date.get_serial()
        return b - a

    def diff_dates_instance(self, end_date: "Date") -> int:
        """Calculate difference in days from this date to end date."""
        a = self.get_serial()
        b = end_date.get_serial()
        return b - a

    @staticmethod
    def diff_dates_360(begin_date: "Date", end_date: "Date") -> int:
        """Calculate difference in days (360-day year) between two dates."""
        a = begin_date.get_commercial_serial()
        b = end_date.get_commercial_serial()
        return b - a

    def diff_commercial_dates(self, end_date: "Date") -> int:
        """Calculate commercial date difference."""
        a = self.get_commercial_serial()
        b = end_date.get_commercial_serial()
        return b - a

    def __str__(self) -> str:
        """String representation."""
        return f"{self._year}-{self._month}-{self._day}"

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, Date):
            return False
        return self._year == other._year and self._month == other._month and self._day == other._day
