"""
Financial memory for HP12C calculator.
Ported from Java FinanceMemory.java.
"""

import math

from hp12c.calculator.exceptions import CalculatorException, Error
from hp12c.hp12c_math.number import Number
from hp12c.utils.date import Date


class FinanceMemory:
    """Manages financial calculator memory (TVM variables)."""

    YEAR_360 = Number.n(360.0)
    YEAR_365 = Number.n(365.0)

    def __init__(
        self,
        size: int = 5,
        fin: list[Number] | None = None,
        n: Number | None = None,
        i: Number | None = None,
        pv: Number | None = None,
        pmt: Number | None = None,
        fv: Number | None = None,
    ):
        """Initialize financial memory."""
        if fin is not None:
            self._fin = fin
        else:
            self._fin = [Number.ZERO] * size

        if (
            n is not None
            and i is not None
            and pv is not None
            and pmt is not None
            and fv is not None
        ):
            self._fin[0] = n
            self._fin[1] = i
            self._fin[2] = pv
            self._fin[3] = pmt
            self._fin[4] = fv

        self._begin = False
        self._c = False
        self.init()

    def init(self):
        """Initialize financial memory (no-op)."""
        pass

    def get(self, idx: int) -> Number:
        """Get value at index."""
        return self._fin[idx]

    def set(self, idx: int, val: Number):
        """Set value at index."""
        self._fin[idx] = val

    def get_size(self) -> int:
        """Get memory size."""
        return len(self._fin)

    def set_array(self, fin: list[Number]):
        """Set memory array."""
        self._fin = fin

    def get_array(self) -> list[Number]:
        """Get memory array (returns direct reference, matching Java behavior)."""
        return self._fin

    def clear(self):
        """Clear memory."""
        for i in range(len(self._fin)):
            self._fin[i] = Number.ZERO

    def set_n(self, n: Number):
        """Set N (number of periods)."""
        self._fin[0] = n

    def set_i(self, i: Number):
        """Set I (interest rate)."""
        self._fin[1] = i

    def set_pv(self, pv: Number):
        """Set PV (present value)."""
        self._fin[2] = pv

    def set_pmt(self, pmt: Number):
        """Set PMT (payment)."""
        self._fin[3] = pmt

    def set_fv(self, fv: Number):
        """Set FV (future value)."""
        self._fin[4] = fv

    def get_n(self) -> Number:
        """Get N."""
        return self._fin[0]

    def get_i(self) -> Number:
        """Get I."""
        return self._fin[1]

    def get_pv(self) -> Number:
        """Get PV."""
        return self._fin[2]

    def get_pmt(self) -> Number:
        """Get PMT."""
        return self._fin[3]

    def get_fv(self) -> Number:
        """Get FV."""
        return self._fin[4]

    def is_begin(self) -> bool:
        """Check if begin mode."""
        return self._begin

    def set_begin(self, begin: bool):
        """Set begin mode."""
        self._begin = begin

    def is_c(self) -> bool:
        """Check if C flag."""
        return self._c

    def set_c(self, c: bool):
        """Set C flag."""
        self._c = c

    def __str__(self) -> str:
        """String representation."""
        result = "==[FINANCE MEMORY]==\n"
        result += f" - n  : {self._fin[0]}\n"
        result += f" - i  : {self._fin[1]}\n"
        result += f" - PV : {self._fin[2]}\n"
        result += f" - PMT: {self._fin[3]}\n"
        result += f" - FV : {self._fin[4]}\n"
        return result

    def print(self):
        """Print financial memory (equivalent to Java print method)."""
        print(self)

    # Financial calculations - full implementations

    @staticmethod
    def _simple_interest(n: Number, i: Number, pv: Number) -> Number:
        """Calculate simple interest."""
        return pv.multiply(i.divide(Number.HUNDRED)).multiply(n).negate()

    def simple_interest(self) -> list[Number]:
        """Calculate simple interest for 360 and 365 day years."""
        _n = self.get_n()
        _i = self.get_i()
        _pv = self.get_pv()
        tmp = [
            FinanceMemory._simple_interest(_n, _i.divide(self.YEAR_360), _pv),
            FinanceMemory._simple_interest(_n, _i.divide(self.YEAR_365), _pv),
        ]
        return tmp

    def simple_future_value(self) -> Number:
        """Calculate simple future value."""
        _n = self.get_n().d()
        _i = self.get_i().d()
        _pv = self.get_pv().d()
        return Number.n(FinanceMemory._simple_future_value(_n, _i, _pv))

    @staticmethod
    def _simple_future_value(n: float, i: float, pv: float) -> float:
        """Calculate simple future value (static helper)."""
        return -(pv + pv * (i / 100.0) * n)

    def future_value(self) -> Number:
        """Calculate future value (full implementation with fractional periods)."""
        _n = self.get_n().d()
        _i = self.get_i().d()
        _pv = self.get_pv().d()
        _pmt = self.get_pmt().d()
        _begin = 1.0 if self._begin else 0.0
        _c = 1.0 if self._c else 0.0
        return Number.n(FinanceMemory._future_value(_n, _i, _pv, _pmt, _begin, _c))

    @staticmethod
    def _future_value(n: float, i: float, pv: float, pmt: float, beg: float, c: float) -> float:
        """Calculate future value (static helper with fractional periods)."""
        if i <= -100.0:
            raise CalculatorException(Error.ERROR_CI, "Compound Interest Error: i <= -100")
        fv = 0.0
        tmp = [0.0] * 4
        i /= 100.0
        if FinanceMemory._frac_part(n) == 0.0:
            tmp[0] = 1.0 + i * beg
            tmp[1] = (1.0 - math.pow(1.0 + i, 0.0 - n)) / i
            tmp[2] = math.pow(1.0 + i, 0.0 - n)
            fv = -((pv + tmp[0] * pmt * tmp[1]) / tmp[2])
        else:
            tmp[0] = (
                1.0 + i * FinanceMemory._frac_part(n)
                if c == 0.0
                else math.pow(1.0 + i, FinanceMemory._frac_part(n))
            )
            tmp[1] = 1.0 + i * beg
            tmp[2] = (1.0 - math.pow(1.0 + i, 0.0 - FinanceMemory._int_part(n))) / i
            tmp[3] = math.pow(1.0 + i, 0.0 - FinanceMemory._int_part(n))
            fv = -((pv * tmp[0] + tmp[1] * pmt * tmp[2]) / tmp[3])
        return fv

    def period(self) -> Number:
        """Calculate number of periods (full implementation)."""
        _i = self.get_i().d()
        _pv = self.get_pv().d()
        _pmt = self.get_pmt().d()
        _fv = self.get_fv().d()
        _begin = 1.0 if self._begin else 0.0
        _c = 1.0 if self._c else 0.0
        return Number.n(FinanceMemory._period(_i, _pv, _pmt, _fv, _begin, _c))

    @staticmethod
    def _period(i: float, pv: float, pmt: float, fv: float, beg: float, _c: float) -> float:
        """Calculate number of periods (static helper)."""
        n = 0.0
        tmp = [0.0] * 3
        d = i / 100.0 / (1.0 + i * (beg / 100.0))
        if pmt == fv * i:
            raise CalculatorException(Error.ERROR_CI, "Compound Interest Error: pmt == fv * i")
        if i <= -100.0:
            raise CalculatorException(Error.ERROR_CI, "Compound Interest Error: i <= -100")
        if i == 0.0 and pmt == 0.0:
            raise CalculatorException(
                Error.ERROR_CI, "Compound Interest Error: i == 0 and PMT == 0"
            )
        if pmt >= fv * d and pmt <= -pv * d:
            raise CalculatorException(
                Error.ERROR_CI,
                "Compound Interest Error: PMT between (FV * d) and (-PV * d), inclusive.",
            )
        tmp[0] = pmt - (i := i / 100.0) * fv + i * pmt * beg
        tmp[1] = pmt + i * pv + i * pmt * beg
        tmp[2] = math.log(i + 1.0)
        n = math.log(tmp[0] / tmp[1]) / tmp[2]
        n = math.floor(n) if FinanceMemory._frac_part(n) < 0.005 else math.ceil(n)
        return n

    def present_value(self) -> Number:
        """Calculate present value (full implementation with fractional periods)."""
        _n = self.get_n().d()
        _i = self.get_i().d()
        _pmt = self.get_pmt().d()
        _fv = self.get_fv().d()
        _begin = 1.0 if self._begin else 0.0
        _c = 1.0 if self._c else 0.0
        return Number.n(FinanceMemory._present_value(_n, _i, _pmt, _fv, _begin, _c))

    @staticmethod
    def _present_value(n: float, i: float, pmt: float, fv: float, begin: float, c: float) -> float:
        """Calculate present value (static helper with fractional periods)."""
        if i <= -100.0:
            raise CalculatorException(Error.ERROR_CI, "Compound Interest Error: i <= -100")
        pv = 0.0
        tmp = [0.0] * 4
        i /= 100.0
        if FinanceMemory._frac_part(n) == 0.0:
            tmp[0] = 1.0 + i * begin
            tmp[1] = (1.0 - math.pow(1.0 + i, 0.0 - n)) / i
            tmp[2] = math.pow(1.0 + i, 0.0 - n)
            pv = -(tmp[0] * pmt * tmp[1] + fv * tmp[2])
        else:
            tmp[0] = (
                1.0 + i * FinanceMemory._frac_part(n)
                if c == 0.0
                else math.pow(1.0 + i, FinanceMemory._frac_part(n))
            )
            tmp[1] = 1.0 + i * begin
            tmp[2] = (1.0 - math.pow(1.0 + i, 0.0 - FinanceMemory._int_part(n))) / i
            tmp[3] = math.pow(1.0 + i, 0.0 - FinanceMemory._int_part(n))
            pv = -((tmp[1] * pmt * tmp[2] + fv * tmp[3]) / tmp[0])
        return pv

    def price_payment(self) -> Number:
        """Calculate payment (full implementation with fractional periods)."""
        _n = self.get_n().d()
        _i = self.get_i().d()
        _pv = self.get_pv().d()
        _fv = self.get_fv().d()
        _begin = 1.0 if self._begin else 0.0
        _c = 1.0 if self._c else 0.0
        return Number.n(FinanceMemory._price_payment(_n, _i, _pv, _fv, _begin, _c))

    @staticmethod
    def _price_payment(
        _n: float, _i: float, _pv: float, _fv: float, _begin: float, _c: float
    ) -> float:
        """Calculate payment (static helper with fractional periods)."""
        n_frac = Number.n(_n).fractional_part().d()
        if _n == 0.0:
            raise CalculatorException(Error.ERROR_CI, "Compound Interest Error: n == 0")
        if _i == 0.0:
            raise CalculatorException(Error.ERROR_CI, "Compound Interest Error: i == 0")
        if _i <= -100.0:
            raise CalculatorException(Error.ERROR_CI, "Compound Interest Error: i <= -100")
        pmt = 0.0
        tmp = [0.0] * 4
        _i /= 100.0
        if n_frac == 0.0:
            tmp[0] = 1.0 + _i * _begin
            tmp[1] = (1.0 - math.pow(1.0 + _i, 0.0 - _n)) / _i
            tmp[2] = math.pow(1.0 + _i, 0.0 - _n)
            pmt = -((_pv + _fv * tmp[2]) / (tmp[0] * tmp[1]))
        else:
            tmp[0] = 1.0 + _i * n_frac if _c == 0.0 else math.pow(1.0 + _i, n_frac)
            tmp[1] = 1.0 + _i * _begin
            tmp[2] = (1.0 - math.pow(1.0 + _i, 0.0 - n_frac)) / _i
            tmp[3] = math.pow(1.0 + _i, 0.0 - n_frac)
            pmt = -((_pv * tmp[0] + _fv * tmp[3]) / (tmp[1] * tmp[2]))
        return pmt

    def payment(self) -> Number:
        """Alias for price_payment."""
        return self.price_payment()

    def rate(self) -> Number:
        """Calculate interest rate (full bisection method)."""
        _n = self.get_n().d()
        _pv = self.get_pv().d()
        _pmt = self.get_pmt().d()
        _fv = self.get_fv().d()
        _begin = 1.0 if self._begin else 0.0
        _c = 1.0 if self._c else 0.0
        return Number.n(FinanceMemory._rate(_n, _pv, _pmt, _fv, _begin, _c))

    @staticmethod
    def _rate(n: float, pv: float, pmt: float, fv: float, beg: float, c: float) -> float:
        """Calculate interest rate using bisection method (static helper)."""
        if pmt == 0.0 and n < 0.0:
            raise CalculatorException(
                Error.ERROR_CI, "Compound Interest Error: no solution exists for N."
            )
        if (pv > 0.0 and fv > 0.0) or (pv < 0.0 and fv < 0.0):
            raise CalculatorException(
                Error.ERROR_CI, "Compound Interest Error: both PV and FV are positive or negative."
            )
        init_interest = -1.0
        final_interest = 99999.0
        suposed_interest = 0.0
        suposed_payment = 0.0
        suposed_difference = 0.0
        cnt = 1
        found = False
        pv = -abs(pv)
        pmt = abs(pmt)
        fv = abs(fv)
        while True:
            suposed_interest = (final_interest + init_interest) / 2.0
            suposed_payment = FinanceMemory._price_payment(n, suposed_interest, pv, fv, beg, c)
            suposed_difference = abs(pmt - suposed_payment)
            if suposed_difference > 1.0e-9:
                if suposed_payment > pmt:
                    final_interest = suposed_interest
                else:
                    init_interest = suposed_interest
            else:
                found = True
                break
            if cnt > 10000:
                break
            cnt += 1
        if not found:
            raise CalculatorException(Error.ERROR_CI, "Compound Interest Error: no solution found.")
        return final_interest

    def irr(self, cf: list[list[Number]]) -> Number:
        """Calculate Internal Rate of Return."""
        _n = self.get_n().d()
        doubles = [[cf[i][j].d() for j in range(len(cf[0]))] for i in range(len(cf))]
        return Number.n(FinanceMemory._irr(_n, doubles))

    @staticmethod
    def _irr(n: float, cf: list[list[float]]) -> float:
        """Calculate IRR (static helper)."""
        IRRBegin = 0.0
        npv = 0.0
        irr = 0.0
        u = 0.0
        cont = 0.0
        expo = 0.0
        if len(cf) < n:
            return 0.0
        sign_before = True
        sign_after = True
        a = 0
        while float(a) < n:
            cont += cf[a][1]
            a += 1
        irr = IRRBegin = 100.0
        m = 0
        while m < 100:
            u = 1.0 + irr / 100.0
            expo = 0.0
            sign_before = npv >= 0.0
            j = 0
            while float(j) <= n:
                if j == 0:
                    npv = cf[0][0]
                    sign_before = npv >= 0.0
                    cont += 1.0
                else:
                    k = 0
                    while float(k) < cf[j][1]:
                        if expo <= cont:
                            expo += 1.0
                            npv += cf[j][0] / math.pow(u, expo)
                        k += 1
                j += 1
            sign_after = npv >= 0.0
            # Match Java ternary: irr = condition ? (irr += value) : (irr -= value)
            if sign_before != sign_after:
                irr = irr + IRRBegin / math.pow(2.0, m)
            else:
                irr = irr - IRRBegin / math.pow(2.0, m)
            if npv == 0.0:
                m = 100000
            m += 1
        return irr

    def npv(self, cf: list[list[Number]]) -> Number:
        """Calculate Net Present Value."""
        _n = self.get_n().d()
        _i = self.get_i().d()
        doubles = [[cf[i][j].d() for j in range(len(cf[0]))] for i in range(len(cf))]
        return Number.n(FinanceMemory._npv(_n, _i, doubles))

    @staticmethod
    def _npv(n: float, i: float, cf: list[list[float]]) -> float:
        """Calculate NPV (static helper)."""
        if i <= -100.0:
            raise CalculatorException(Error.ERROR_CI, "Compound Interest Error: i <= -100")
        npv = 0.0
        u = 1.0 + i / 100.0
        cont = 0.0
        expo = 0.0
        if len(cf) < n:
            return 0.0
        a = 0
        while float(a) <= n:
            cont += cf[a][1]
            a += 1
        j = 0
        while float(j) <= n:
            if j == 0:
                npv = cf[0][0]
                cont += 1.0
            else:
                k = 0
                while float(k) < cf[j][1]:
                    if expo <= cont:
                        expo += 1.0
                        npv += cf[j][0] / math.pow(u, expo)
                    k += 1
            j += 1
        return npv

    def amortization(self, x: Number, precision: int) -> list[Number]:
        """Calculate amortization."""
        _x = x.d()
        _precision = float(precision)
        _n = self.get_n().d()
        _i = self.get_i().d()
        _pv = self.get_pv().d()
        _pmt = self.get_pmt().d()
        _begin = 1.0 if self._begin else 0.0
        doubles = FinanceMemory._amortization(_x, _n, _i, _pv, _pmt, _begin, _precision)
        return [Number.n(d) for d in doubles]

    @staticmethod
    def _amortization(
        x: float, n: float, i: float, pv: float, pmt: float, begin: float, precision: float
    ) -> list[float]:
        """Calculate amortization (static helper)."""
        tmp = [0.0] * 5
        INT = 0.0
        SumINT = 0.0
        PRN = 0.0
        SumPRN = 0.0
        PVj = pv
        n += x
        j = 0
        while float(j) < x:
            if j == 0 and begin == 1.0:
                INT = 0.0
            else:
                INT = abs(PVj * i / 100.0)
                INT = round(INT * math.pow(10.0, precision)) / math.pow(10.0, precision)
                if pmt < 0.0:
                    INT = -INT
            SumINT += INT
            PRN = pmt - INT
            SumPRN += PRN
            PVj += PRN
            j += 1
        tmp[0] = float(j)
        tmp[1] = SumPRN
        tmp[2] = SumINT
        tmp[3] = PVj
        tmp[4] = n
        return tmp

    def depreciation_sl(self, x: Number) -> list[Number]:
        """Calculate straight-line depreciation."""
        _n = self.get_n().d()
        _i = self.get_i().d()
        _pv = self.get_pv().d()
        _fv = self.get_fv().d()
        _x = x.d()
        doubles = FinanceMemory._sl_depreciation(_n, _i, _pv, _fv, _x)
        return [Number.n(d) for d in doubles]

    @staticmethod
    def _sl_depreciation(n: float, _i: float, pv: float, fv: float, x: float) -> list[float]:
        """Calculate straight-line depreciation (static helper)."""
        cost = pv
        sell = fv
        life = n
        year = x
        depr = 0.0
        rest = cost - sell
        tmp = [0.0] * 2
        if year < 0.0:
            raise CalculatorException(Error.ERROR_CI, "year < 0")
        if year != math.floor(year):
            raise CalculatorException(Error.ERROR_CI, "year is not integer")
        if life <= 0.0:
            raise CalculatorException(Error.ERROR_CI, "life <= 0")
        if life > math.pow(10.0, 10.0):
            raise CalculatorException(Error.ERROR_CI, "life > 10^10")
        depr = (cost - sell) / life
        while (year := year - 1.0) >= 0.0:
            rest -= depr
        tmp[0] = depr
        tmp[1] = rest
        return tmp

    def depreciation_syd(self, x: Number) -> list[Number]:
        """Calculate sum-of-years digits depreciation."""
        _n = self.get_n().d()
        _i = self.get_i().d()
        _pv = self.get_pv().d()
        _fv = self.get_fv().d()
        _x = x.d()
        doubles = FinanceMemory._soyd_depreciation(_n, _i, _pv, _fv, _x)
        return [Number.n(d) for d in doubles]

    @staticmethod
    def _soyd_depreciation(n: float, _i: float, pv: float, fv: float, x: float) -> list[float]:
        """Calculate sum-of-years digits depreciation (static helper)."""
        cost = pv
        sell = fv
        life = n
        year = x
        depr = 0.0
        rest = cost - sell
        tmp = [0.0] * 2
        if year < 0.0:
            raise CalculatorException(Error.ERROR_CI, "year < 0")
        if year != math.floor(year):
            raise CalculatorException(Error.ERROR_CI, "year is not integer")
        if life <= 0.0:
            raise CalculatorException(Error.ERROR_CI, "life <= 0")
        if life > math.pow(10.0, 10.0):
            raise CalculatorException(Error.ERROR_CI, "life > 10^10")
        year_up = 0.0
        soyd = life * (life + 1.0) / 2.0
        while (year := year - 1.0) >= 0.0:
            year_up += 1.0
            depr = (cost - sell) * (life - year_up + 1.0) / soyd
            rest -= depr
        tmp[0] = depr
        tmp[1] = rest
        return tmp

    def depreciation_db(self, x: Number) -> list[Number]:
        """Calculate declining balance depreciation."""
        _n = self.get_n().d()
        _i = self.get_i().d()
        _pv = self.get_pv().d()
        _fv = self.get_fv().d()
        _x = x.d()
        doubles = FinanceMemory._db_depreciation(_n, _i, _pv, _fv, _x)
        return [Number.n(d) for d in doubles]

    @staticmethod
    def _db_depreciation(n: float, i: float, pv: float, fv: float, x: float) -> list[float]:
        """Calculate declining balance depreciation (static helper)."""
        cost = pv
        sell = fv
        life = n
        db = i / 100.0
        year = x
        depr = 0.0
        rest = cost - sell
        tmp = [0.0] * 2
        if year < 0.0:
            raise CalculatorException(Error.ERROR_CI, "year < 0")
        if year != math.floor(year):
            raise CalculatorException(Error.ERROR_CI, "year is not integer")
        if life <= 0.0:
            raise CalculatorException(Error.ERROR_CI, "life <= 0")
        if life > math.pow(10.0, 10.0):
            raise CalculatorException(Error.ERROR_CI, "life > 10^10")
        depr = (rest + sell) * db / life
        while (year := year - 1.0) >= 0.0:
            rest -= depr
        tmp[0] = depr
        tmp[1] = rest
        return tmp

    def bond_price(self, y: Date, x: Date) -> list[Number]:
        """Calculate bond price."""
        _i = self.get_i().d()
        _pmt = self.get_pmt().d()
        doubles = FinanceMemory._bond_price(_i, _pmt, y, x)
        return [Number.n(d) for d in doubles]

    @staticmethod
    def _bond_price(i: float, pmt: float, y: Date, x: Date) -> list[float]:
        """Calculate bond price (static helper)."""
        if x is None or not x.is_valid():
            raise CalculatorException(Error.ERROR_CAL, "invalid x date (maturity)")
        if y is None or not y.is_valid():
            raise CalculatorException(Error.ERROR_CAL, "invalid y date (buy)")
        if i <= -100.0:
            raise CalculatorException(Error.ERROR_CI, "i <= -100")
        dsm = 0.0
        dcs = 0.0
        e = 0.0
        dsc = e - dcs
        n = 0.0
        cpn = 0.0
        yield_val = 0.0
        rdv = 0.0
        tmp = [0.0] * 2
        yield_val = i
        cpn = pmt
        rdv = 100.0
        settlement = Date(date=y)
        maturity = Date(date=x)
        dsm = Date.diff_dates(settlement, maturity)
        a = Date(date=maturity)
        b = Date()
        while a.get_serial() > settlement.get_serial():
            b = Date(date=a)
            n += 1.0
            a.set_day(1)
            a.set_month(a.get_month() - 6)
            a.set_day(maturity.get_day())
        e = Date.diff_dates(a, b)
        dcs = Date.diff_dates(settlement, b)
        dsc = e - dcs
        if dsm <= e:
            tmp[0] = 100.0 * (rdv + cpn / 2.0)
            tmp[1] = 100.0 + dsm / e * (yield_val / 2.0)
            tmp[0] = tmp[0] / tmp[1]
        else:
            tmp[0] = rdv / math.pow(1.0 + yield_val / 200.0, n - 1.0 + dcs / e)
            tmp[1] = 0.0
            k = 1
            while float(k) <= n:
                tmp[1] = tmp[1] + cpn / 2.0 / math.pow(
                    1.0 + yield_val / 200.0, float(k - 1) + dcs / e
                )
                k += 1
            tmp[0] = tmp[0] + tmp[1]
        tmp[1] = cpn / 2.0 * (dsc / e)
        tmp[0] = tmp[0] - tmp[1]
        tmp[0] = tmp[0]  # Redundant assignment matching Java code
        tmp[1] = tmp[1]  # Redundant assignment matching Java code
        return tmp

    def bond_price_old(self, y: Date, x: Date) -> list[Number]:
        """Calculate bond price (OLD version - same as bond_price)."""
        _i = self.get_i().d()
        _pmt = self.get_pmt().d()
        doubles = FinanceMemory._bond_price(_i, _pmt, y, x)
        return [Number.n(d) for d in doubles]

    @staticmethod
    def bond_yield(_pv: float, _pmt: float, _y: Date, _x: Date) -> float:
        """Calculate bond yield (placeholder - returns 0.0)."""
        return 0.0

    @staticmethod
    def _int_part(x: float) -> float:
        """Get integer part of number."""
        return math.floor(x)

    @staticmethod
    def _frac_part(x: float) -> float:
        """Get fractional part of number."""
        return x - FinanceMemory._int_part(x)
