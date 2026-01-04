"""
Calculator flags for HP12C.
Ported from Java Flags.java.
"""

from typing import List, Tuple


class Flags:
    """Manages calculator state flags."""

    DEFAULT = [
        ["f", "0"], ["g", "0"], ["sto", "0"], ["rcl", "0"], ["gto", "0"],
        ["dmy", "0"], ["beg", "0"], ["c", "0"], ["on", "0"], ["brc", "0"],
        ["alg", "0"], ["prgm", "0"], ["run", "0"], ["wild", "0"]
    ]

    def __init__(self, size: int = 14, flg: List[List[str]] = None):
        """Initialize flags."""
        if flg is not None:
            self._flg = flg
        else:
            self._flg = [["", ""]] * size
        self._display_str = ""
        self.init()

    def init(self):
        """Initialize flags to defaults."""
        self._flg = [list(pair) for pair in Flags.DEFAULT]

    def get_flag(self, key: str) -> int:
        """Get flag value."""
        try:
            for pair in self._flg:
                if pair[0] == key:
                    return int(pair[1])
            return 0
        except (ValueError, IndexError):
            return 0

    def set_flag(self, key: str, value: int):
        """Set flag value."""
        for pair in self._flg:
            if pair[0] == key:
                pair[1] = str(value)
                return

    def clear(self):
        """Clear all flags."""
        for pair in self._flg:
            pair[1] = ""

    def __str__(self) -> str:
        """String representation."""
        result = "-------Flags--------\n"
        for pair in self._flg:
            result += f" - Flg: {pair[0]} = {pair[1]}\n"
        return result

    def reset(self):
        """Reset flags to defaults."""
        self._flg = [list(pair) for pair in Flags.DEFAULT]

    def toggle(self, flg: str):
        """Toggle flag."""
        if self.get_flag(flg) > 0:
            self.set_flag(flg, 0)
        else:
            self.set_flag(flg, 1)

    def toggle_f(self):
        """Toggle f flag."""
        self.toggle("f")

    def toggle_g(self):
        """Toggle g flag."""
        self.toggle("g")

    def set_sto(self, sto: int):
        """Set sto flag."""
        self.set_flag("sto", sto)

    def toggle_sto(self):
        """Toggle sto flag."""
        self.toggle("sto")

    def set_rcl(self, rcl: int):
        """Set rcl flag."""
        self.set_flag("rcl", rcl)

    def toggle_rcl(self):
        """Toggle rcl flag."""
        self.toggle("rcl")

    def set_gto(self, gto: int):
        """Set gto flag."""
        self.set_flag("gto", gto)

    def toggle_gto(self):
        """Toggle gto flag."""
        self.toggle("gto")

    def set_dmy(self, dmy: int):
        """Set dmy flag."""
        self.set_flag("dmy", dmy)

    def set_begin(self, beg: int):
        """Set begin flag."""
        self.set_flag("beg", beg)

    def toggle_c(self):
        """Toggle c flag."""
        self.toggle("c")

    def toggle_on(self):
        """Toggle on flag."""
        self.toggle("on")

    def set_wild(self, wild: int):
        """Set wild flag."""
        self.set_flag("wild", wild)

    def toggle_wild(self):
        """Toggle wild flag."""
        self.toggle("wild")

    def set_brc(self, brc: int):
        """Set brc flag."""
        self.set_flag("brc", brc)

    def set_alg(self, alg: int):
        """Set alg flag."""
        self.set_flag("alg", alg)

    def set_run(self, run: int):
        """Set run flag."""
        self.set_flag("run", run)

    def toggle_run(self):
        """Toggle run flag."""
        self.toggle("run")

    def set_prgm(self, prgm: int):
        """Set prgm flag."""
        self.set_flag("prgm", prgm)

    def toggle_prgm(self):
        """Toggle prgm flag."""
        self.toggle("prgm")

    # Getters
    def get_f(self) -> int:
        return self.get_flag("f")

    def get_g(self) -> int:
        return self.get_flag("g")

    def get_sto(self) -> int:
        return self.get_flag("sto")

    def get_rcl(self) -> int:
        return self.get_flag("rcl")

    def get_gto(self) -> int:
        return self.get_flag("gto")

    def get_dmy(self) -> int:
        return self.get_flag("dmy")

    def get_begin(self) -> int:
        return self.get_flag("beg")

    def get_c(self) -> int:
        return self.get_flag("c")

    def get_on(self) -> int:
        return self.get_flag("on")

    def get_wild(self) -> int:
        return self.get_flag("wild")

    def get_brc(self) -> int:
        return self.get_flag("brc")

    def get_alg(self) -> int:
        return self.get_flag("alg")

    def get_run(self) -> int:
        return self.get_flag("run")

    def get_prgm(self) -> int:
        return self.get_flag("prgm")

    def get_display_str(self) -> str:
        """Get display string for flags."""
        # Increased spaces for better readability
        self._display_str = "     ALG  " if self.get_alg() == 1 else "  RPN     "
        self._display_str += "( )  " if self.get_brc() == 1 else "      "
        self._display_str += "f  " if self.get_f() == 1 else "   "
        self._display_str += "g  " if self.get_g() == 1 else "   "
        self._display_str += "BEGIN  " if self.get_begin() == 1 else "        "
        self._display_str += "D.MY  " if self.get_dmy() == 1 else "       "
        self._display_str += "C  " if self.get_c() == 1 else "   "
        self._display_str += "PRGM  " if self.get_prgm() == 1 else "       "
        # Ensure the string is exactly 47 characters
        if len(self._display_str) < 47:
            self._display_str = self._display_str.ljust(47)
        elif len(self._display_str) > 47:
            self._display_str = self._display_str[:47]
        return self._display_str
