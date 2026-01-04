"""Unit tests for Configuration class."""

import pytest

from hp12c.calculator.config import Configuration, KeyMapItem


class TestKeyMapItem:
    """Test cases for KeyMapItem class."""

    def test_initialization(self):
        """Test KeyMapItem initialization."""
        item = KeyMapItem(10, "a")
        assert item.get_code() == 10
        assert item.get_char() == "a"

    def test_set_char(self):
        """Test setting character."""
        item = KeyMapItem(10, "a")
        item.set_char("b")
        assert item.get_char() == "b"

    def test_set_code(self):
        """Test setting code."""
        item = KeyMapItem(10, "a")
        item.set_code(20)
        assert item.get_code() == 20


class TestConfiguration:
    """Test cases for Configuration class."""

    def test_initialization(self):
        """Test configuration initialization."""
        config = Configuration()
        assert config is not None
        assert config.get_skin() == Configuration.DEFAULT_SKIN

    def test_set_and_get_size(self):
        """Test size setting and getting."""
        config = Configuration()
        config.set_size(0.5)
        assert config.get_size() == 0.5

    def test_set_and_get_position(self):
        """Test position setting and getting."""
        config = Configuration()
        config.set_x_pos(100)
        config.set_y_pos(200)
        assert config.get_x_pos() == 100
        assert config.get_y_pos() == 200

    def test_set_and_get_skin(self):
        """Test skin setting and getting."""
        config = Configuration()
        config.set_skin("aurum")
        assert config.get_skin() == "aurum"

    def test_set_and_get_language(self):
        """Test language setting and getting."""
        config = Configuration()
        config.set_language("pt")
        assert config.get_language() == "pt"

    def test_set_and_get_ui_framework(self):
        """Test UI framework setting and getting."""
        config = Configuration()
        config.set_ui_framework("pyqt5")
        assert config.get_ui_framework() == "pyqt5"

    def test_set_ui_framework_invalid(self):
        """Test setting invalid UI framework raises error."""
        config = Configuration()
        with pytest.raises(ValueError):
            config.set_ui_framework("invalid")

    def test_set_and_get_stack_size(self):
        """Test stack size setting and getting."""
        config = Configuration()
        config.set_stack_size(8)
        assert config.get_stack_size() == 8

    def test_set_and_get_memory_size(self):
        """Test memory size setting and getting."""
        config = Configuration()
        config.set_memory_size(30)
        assert config.get_memory_size() == 30

    def test_set_and_get_program_size(self):
        """Test program size setting and getting."""
        config = Configuration()
        config.set_program_size(200)
        assert config.get_program_size() == 200

    def test_set_and_get_flags(self):
        """Test flag setting and getting."""
        config = Configuration()
        config.set_c(1)
        config.set_dmy(1)
        config.set_com(1)
        config.set_alg(1)
        config.set_beg(1)
        assert config.get_c() == 1
        assert config.get_dmy() == 1
        assert config.get_com() == 1
        assert config.get_alg() == 1
        assert config.get_beg() == 1

    def test_set_and_get_fix(self):
        """Test fix setting and getting."""
        config = Configuration()
        config.set_fix(5)
        assert config.get_fix() == 5

    def test_set_and_get_mode(self):
        """Test mode setting and getting."""
        config = Configuration()
        config.set_mode(1)
        assert config.get_mode() == 1

    def test_get_key_map_item(self):
        """Test getting key map item."""
        config = Configuration()
        item = config.get_key_map_item(0)
        assert item is not None
        assert isinstance(item, KeyMapItem)

    def test_get_key_map_item_out_of_bounds(self):
        """Test getting key map item out of bounds."""
        config = Configuration()
        item = config.get_key_map_item(1000)
        assert item is None

    def test_set_char(self):
        """Test setting character for code."""
        config = Configuration()
        config.set_char(10, "x")
        item = config.get_code_index(10)
        assert item != -1

    def test_get_code_index(self):
        """Test getting code index."""
        config = Configuration()
        idx = config.get_code_index(0)
        assert idx != -1

    def test_get_code_index_not_found(self):
        """Test getting code index for non-existent code."""
        config = Configuration()
        idx = config.get_code_index(9999)
        assert idx == -1

    def test_get_code(self):
        """Test getting code for character."""
        config = Configuration()
        code = config.get_code("0")
        assert code == 0

    def test_get_code_not_found(self):
        """Test getting code for non-existent character."""
        config = Configuration()
        code = config.get_code("z")
        assert code == -1

    def test_get_key_map(self):
        """Test getting key map."""
        config = Configuration()
        key_map = config.get_key_map()
        assert isinstance(key_map, list)
        assert len(key_map) > 0

    def test_set_key_map(self):
        """Test setting key map."""
        config = Configuration()
        new_map = [KeyMapItem(100, "x")]
        config.set_key_map(new_map)
        assert len(config.get_key_map()) == 1

    def test_set_defaults(self):
        """Test setting defaults."""
        config = Configuration()
        config.set_skin("custom")
        config.set_defaults()
        assert config.get_skin() == Configuration.DEFAULT_SKIN

    def test_create_stack(self):
        """Test creating stack."""
        stack = Configuration.create_stack(4)
        assert stack is not None
        assert stack.get_size() == 4

    def test_create_stack_instance(self):
        """Test creating stack instance from config."""
        config = Configuration()
        stack = config.create_stack_instance()
        assert stack is not None

    def test_create_general_memory(self):
        """Test creating general memory."""
        mem = Configuration.create_general_memory(20)
        assert mem is not None
        assert mem.get_size() == 20

    def test_create_general_memory_instance(self):
        """Test creating general memory instance from config."""
        config = Configuration()
        mem = config.create_general_memory_instance()
        assert mem is not None

    def test_create_program_memory(self):
        """Test creating program memory."""
        prg = Configuration.create_program_memory(100)
        assert prg is not None
        assert prg.get_size() == 100

    def test_create_program_memory_instance(self):
        """Test creating program memory instance from config."""
        config = Configuration()
        prg = config.create_program_memory_instance()
        assert prg is not None

    def test_create_finance_memory(self):
        """Test creating finance memory."""
        fin = Configuration.create_finance_memory()
        assert fin is not None

    def test_create_step(self):
        """Test creating step."""
        step = Configuration.create_step()
        assert step is not None

    def test_create_configuration(self):
        """Test factory method for creating configuration."""
        config = Configuration.create_configuration()
        assert config is not None
        assert isinstance(config, Configuration)
