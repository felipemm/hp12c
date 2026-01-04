"""
General memory for HP12C calculator.
Ported from Java GeneralMemory.java.
"""

import math
from typing import List, Optional
from hp12c.hp12c_math.number import Number


class GeneralMemory:
    """Manages general purpose memory registers."""

    def __init__(self, size: int = 20, mem: Optional[List[List[Number]]] = None):
        """Initialize general memory."""
        if mem is not None:
            self._mem = mem
        else:
            self._mem = [[Number.ZERO, Number.ONE] for _ in range(size)]
        self._cur = 0
        self.init()

    def init(self):
        """Initialize general memory (no-op)."""
        pass

    def get_size(self) -> int:
        """Get memory size."""
        return len(self._mem)

    def get_used_registers(self) -> int:
        """Get number of used registers."""
        cnt = 0
        for pair in self._mem:
            if not pair[0].equal_to(Number.ZERO):
                cnt += 1
        return cnt

    def get_available_registers(self) -> int:
        """Get number of available registers."""
        return self.get_size() - self.get_used_registers()

    def set(self, idx: int, value: Number):
        """Set value at index."""
        if idx < len(self._mem):
            self._mem[idx][0] = value

    def get(self, idx: int) -> Number:
        """Get value at index."""
        if idx < len(self._mem):
            return self._mem[idx][0]
        return Number.ZERO

    def get_with_times(self, idx: int) -> List[Number]:
        """Get value and times at index."""
        if idx < len(self._mem):
            return [self._mem[idx][0], self._mem[idx][1]]
        return [Number.ZERO, Number.ZERO]

    def set_times(self, idx: int, times: Number):
        """Set times at index."""
        if idx < len(self._mem):
            self._mem[idx][1] = times

    def get_times(self, idx: int) -> Number:
        """Get times at index."""
        if idx < len(self._mem):
            return self._mem[idx][1]
        return Number.ONE

    def set_with_times(self, idx: int, value: Number, times: Number):
        """Set value and times at index."""
        if idx < len(self._mem) and times.greater_than(Number.ZERO) and times.less_than(Number.HUNDRED):
            self._mem[idx][0] = value
            self._mem[idx][1] = times

    def set_with_times_from_array(self, idx: int, a: List[Number]):
        """Set value and times from array."""
        self.set_with_times(idx, a[0], a[1])

    def get_current_index(self) -> int:
        """Get current index."""
        return self._cur

    def get_array(self) -> List[List[Number]]:
        """Get memory array."""
        return [[pair[0], pair[1]] for pair in self._mem]

    def set_array(self, mem: List[List[Number]]):
        """Set memory array."""
        self._mem = mem

    def put(self, value: Number, times: Number = None):
        """Put value at current index."""
        if times is None:
            times = Number.ONE
        self._cur += 1
        self.set_with_times(self._cur, value, times)

    def put_from_array(self, a: List[Number]):
        """Put from array."""
        self._cur += 1
        self.set_with_times_from_array(self._cur, a)

    def clear(self):
        """Clear memory."""
        for i in range(len(self._mem)):
            self._mem[i][0] = Number.ZERO
            self._mem[i][1] = Number.ONE
        self._cur = 0

    def __str__(self) -> str:
        """String representation."""
        result = "==[GENERAL MEMORY]==\n"
        for i in range(len(self._mem)):
            result += f" - M{i}: {self._mem[i][0]} x {self._mem[i][1]}\n"
        return result

    # Statistical functions
    def sum_stats(self, x: Number, y: Number):
        """Add to statistics."""
        self._mem[1][0] = self._mem[1][0].add(Number.ONE)
        self._mem[1][1] = Number.ONE
        self._mem[2][0] = self._mem[2][0].add(x)
        self._mem[2][1] = Number.ONE
        self._mem[3][0] = self._mem[3][0].add(x.multiply(x))
        self._mem[3][1] = Number.ONE
        self._mem[4][0] = self._mem[4][0].add(y)
        self._mem[4][1] = Number.ONE
        self._mem[5][0] = self._mem[5][0].add(y.multiply(y))
        self._mem[5][1] = Number.ONE
        self._mem[6][0] = self._mem[6][0].add(x.multiply(y))
        self._mem[6][1] = Number.ONE

    def sub_stats(self, x: Number, y: Number):
        """Subtract from statistics."""
        self._mem[1][0] = self._mem[1][0].subtract(Number.ONE)
        self._mem[1][1] = Number.ONE
        self._mem[2][0] = self._mem[2][0].subtract(x)
        self._mem[2][1] = Number.ONE
        self._mem[3][0] = self._mem[3][0].subtract(x.multiply(x))
        self._mem[3][1] = Number.ONE
        self._mem[4][0] = self._mem[4][0].subtract(y)
        self._mem[4][1] = Number.ONE
        self._mem[5][0] = self._mem[5][0].subtract(y.multiply(y))
        self._mem[5][1] = Number.ONE
        self._mem[6][0] = self._mem[6][0].subtract(x.multiply(y))
        self._mem[6][1] = Number.ONE

    # Register accessors
    def set_r1(self, r1: Number):
        self._mem[1][0] = r1
        self._mem[1][1] = Number.ONE

    def set_r2(self, r2: Number):
        self._mem[2][0] = r2
        self._mem[2][1] = Number.ONE

    def set_r3(self, r3: Number):
        self._mem[3][0] = r3
        self._mem[3][1] = Number.ONE

    def set_r4(self, r4: Number):
        self._mem[4][0] = r4
        self._mem[4][1] = Number.ONE

    def set_r5(self, r5: Number):
        self._mem[5][0] = r5
        self._mem[5][1] = Number.ONE

    def set_r6(self, r6: Number):
        self._mem[6][0] = r6
        self._mem[6][1] = Number.ONE

    def get_r1(self) -> Number:
        return self._mem[1][0]

    def get_r2(self) -> Number:
        return self._mem[2][0]

    def get_r3(self) -> Number:
        return self._mem[3][0]

    def get_r4(self) -> Number:
        return self._mem[4][0]

    def get_r5(self) -> Number:
        return self._mem[5][0]

    def get_r6(self) -> Number:
        return self._mem[6][0]

    def clear_stats(self):
        """Clear statistics."""
        for i in range(1, 7):
            self._mem[i][0] = Number.ZERO
            self._mem[i][1] = Number.ONE

    def mean(self) -> List[Number]:
        """Calculate mean."""
        n = self.get_r1()
        x_sum = self.get_r2()
        y_sum = self.get_r4()
        if n.is_zero():
            raise ValueError("Mean of empty list of values")
        return [x_sum.divide(n), y_sum.divide(n)]

    def weighted_mean(self) -> Number:
        """Calculate weighted mean."""
        n = self.get_r1()
        x_sum = self.get_r2()
        xy_sum = self.get_r6()
        if n.is_zero():
            raise ValueError("Weighted mean of empty list of values")
        if x_sum.is_zero():
            raise ValueError("Weight sum in weighted average is ZERO")
        return xy_sum.divide(x_sum)

    def standard_deviation(self) -> List[Number]:
        """Calculate standard deviation."""
        n = self.get_r1()
        x_sum = self.get_r2()
        x2_sum = self.get_r3()
        y_sum = self.get_r4()
        y2_sum = self.get_r5()
        if n.is_zero():
            raise ValueError("Mean of empty list of values")
        return [self._std_dev(x_sum, x2_sum, n), self._std_dev(y_sum, y2_sum, n)]

    def _std_dev(self, _sum: Number, _sqr_sum: Number, _count: Number) -> Number:
        """Calculate standard deviation helper."""
        s = _sum.d()
        sqr = _sqr_sum.d()
        cnt = _count.d()
        p = cnt * sqr - (s ** 2)
        q = cnt * (cnt - 1.0)
        return Number.n(math.sqrt(p / q))

    def y_linear_estimation(self, value: Number) -> List[Number]:
        """Calculate y linear estimation."""
        n = self.get_r1()
        x_sum = self.get_r2()
        x2_sum = self.get_r3()
        y_sum = self.get_r4()
        xy_sum = self.get_r6()
        if n.is_zero():
            raise ValueError("Mean of empty list of values")
        y_est = self._y_lin_est(x_sum, y_sum, xy_sum, x2_sum, n, value)
        r = self._r_lin_est(x_sum, y_sum, xy_sum, x2_sum, self.get_r5(), n)
        return [y_est, r]

    def _y_lin_est(self, x_sum: Number, y_sum: Number, xy_sum: Number, x2_sum: Number, count: Number, x_val: Number) -> Number:
        """Y linear estimation helper."""
        xs = x_sum.d()
        ys = y_sum.d()
        xys = xy_sum.d()
        x2s = x2_sum.d()
        cnt = count.d()
        xv = x_val.d()
        b = (xys - xs * ys / cnt) / (x2s - (xs ** 2) / cnt)
        a = ys / cnt - b * (xs / cnt)
        return Number.n(a + b * xv)

    def _r_lin_est(self, x_sum: Number, y_sum: Number, xy_sum: Number, x2_sum: Number, y2_sum: Number, count: Number) -> Number:
        """Correlation coefficient helper."""
        xs = x_sum.d()
        ys = y_sum.d()
        xys = xy_sum.d()
        x2s = x2_sum.d()
        y2s = y2_sum.d()
        cnt = count.d()
        p = abs(xys - xs * ys / cnt)
        q1 = abs(x2s - (xs ** 2) / cnt)
        q2 = abs(y2s - (ys ** 2) / cnt)
        return Number.n(p / math.sqrt(q1 * q2))
