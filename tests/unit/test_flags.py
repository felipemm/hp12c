"""Unit tests for Flags class."""

from hp12c.model.flags import Flags


class TestFlags:
    """Test cases for Flags class."""

    def test_initialization(self):
        """Test flags initialization."""
        flags = Flags()
        assert flags is not None
        assert flags.get_flag("f") == 0

    def test_get_flag(self):
        """Test getting flag value."""
        flags = Flags()
        assert flags.get_flag("f") == 0
        assert flags.get_flag("g") == 0
        assert flags.get_flag("nonexistent") == 0

    def test_set_flag(self):
        """Test setting flag value."""
        flags = Flags()
        flags.set_flag("f", 1)
        assert flags.get_flag("f") == 1
        flags.set_flag("f", 0)
        assert flags.get_flag("f") == 0

    def test_toggle(self):
        """Test toggling flag."""
        flags = Flags()
        initial = flags.get_flag("f")
        flags.toggle("f")
        assert flags.get_flag("f") != initial
        flags.toggle("f")
        assert flags.get_flag("f") == initial

    def test_toggle_f(self):
        """Test toggling f flag."""
        flags = Flags()
        initial = flags.get_f()
        flags.toggle_f()
        assert flags.get_f() != initial

    def test_toggle_g(self):
        """Test toggling g flag."""
        flags = Flags()
        initial = flags.get_g()
        flags.toggle_g()
        assert flags.get_g() != initial

    def test_set_sto(self):
        """Test setting sto flag."""
        flags = Flags()
        flags.set_sto(5)
        assert flags.get_sto() == 5

    def test_toggle_sto(self):
        """Test toggling sto flag."""
        flags = Flags()
        initial = flags.get_sto()
        flags.toggle_sto()
        assert flags.get_sto() != initial

    def test_set_rcl(self):
        """Test setting rcl flag."""
        flags = Flags()
        flags.set_rcl(3)
        assert flags.get_rcl() == 3

    def test_toggle_rcl(self):
        """Test toggling rcl flag."""
        flags = Flags()
        initial = flags.get_rcl()
        flags.toggle_rcl()
        assert flags.get_rcl() != initial

    def test_set_gto(self):
        """Test setting gto flag."""
        flags = Flags()
        flags.set_gto(10)
        assert flags.get_gto() == 10

    def test_toggle_gto(self):
        """Test toggling gto flag."""
        flags = Flags()
        initial = flags.get_gto()
        flags.toggle_gto()
        assert flags.get_gto() != initial

    def test_set_dmy(self):
        """Test setting dmy flag."""
        flags = Flags()
        flags.set_dmy(1)
        assert flags.get_dmy() == 1

    def test_set_begin(self):
        """Test setting begin flag."""
        flags = Flags()
        flags.set_begin(1)
        assert flags.get_begin() == 1

    def test_toggle_c(self):
        """Test toggling c flag."""
        flags = Flags()
        initial = flags.get_c()
        flags.toggle_c()
        assert flags.get_c() != initial

    def test_toggle_on(self):
        """Test toggling on flag."""
        flags = Flags()
        initial = flags.get_on()
        flags.toggle_on()
        assert flags.get_on() != initial

    def test_set_wild(self):
        """Test setting wild flag."""
        flags = Flags()
        flags.set_wild(1)
        assert flags.get_wild() == 1

    def test_toggle_wild(self):
        """Test toggling wild flag."""
        flags = Flags()
        initial = flags.get_wild()
        flags.toggle_wild()
        assert flags.get_wild() != initial

    def test_set_brc(self):
        """Test setting brc flag."""
        flags = Flags()
        flags.set_brc(1)
        assert flags.get_brc() == 1

    def test_set_alg(self):
        """Test setting alg flag."""
        flags = Flags()
        flags.set_alg(1)
        assert flags.get_alg() == 1

    def test_set_run(self):
        """Test setting run flag."""
        flags = Flags()
        flags.set_run(1)
        assert flags.get_run() == 1

    def test_toggle_run(self):
        """Test toggling run flag."""
        flags = Flags()
        initial = flags.get_run()
        flags.toggle_run()
        assert flags.get_run() != initial

    def test_set_prgm(self):
        """Test setting prgm flag."""
        flags = Flags()
        flags.set_prgm(1)
        assert flags.get_prgm() == 1

    def test_toggle_prgm(self):
        """Test toggling prgm flag."""
        flags = Flags()
        initial = flags.get_prgm()
        flags.toggle_prgm()
        assert flags.get_prgm() != initial

    def test_clear(self):
        """Test clearing all flags."""
        flags = Flags()
        flags.set_flag("f", 1)
        flags.set_flag("g", 1)
        flags.clear()
        # After clear, flags should be empty strings
        assert flags.get_flag("f") == 0 or flags.get_flag("f") == ""

    def test_reset(self):
        """Test resetting flags to defaults."""
        flags = Flags()
        flags.set_flag("f", 5)
        flags.reset()
        assert flags.get_flag("f") == 0

    def test_get_display_str(self):
        """Test getting display string."""
        flags = Flags()
        display_str = flags.get_display_str()
        assert display_str is not None
        assert len(display_str) == 47

    def test_get_display_str_with_flags(self):
        """Test display string with various flags set."""
        flags = Flags()
        flags.set_alg(1)
        flags.set_begin(1)
        flags.set_dmy(1)
        display_str = flags.get_display_str()
        assert "ALG" in display_str or "BEGIN" in display_str or "D.MY" in display_str
        assert len(display_str) == 47

    def test_string_representation(self):
        """Test string representation."""
        flags = Flags()
        str_repr = str(flags)
        assert "Flags" in str_repr
        assert "f" in str_repr

    def test_getters(self):
        """Test all getter methods."""
        flags = Flags()
        assert flags.get_f() == 0
        assert flags.get_g() == 0
        assert flags.get_sto() == 0
        assert flags.get_rcl() == 0
        assert flags.get_gto() == 0
        assert flags.get_dmy() == 0
        assert flags.get_begin() == 0
        assert flags.get_c() == 0
        assert flags.get_on() == 0
        assert flags.get_wild() == 0
        assert flags.get_brc() == 0
        assert flags.get_alg() == 0
        assert flags.get_run() == 0
        assert flags.get_prgm() == 0
