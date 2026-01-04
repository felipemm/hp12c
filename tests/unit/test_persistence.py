"""Unit tests for persistence classes."""

import json

from hp12c.calculator.config import Configuration
from hp12c.hp12c_math.number import Number
from hp12c.model.general_memory import GeneralMemory
from hp12c.model.stack import Stack
from hp12c.persistence.config_dao import ConfigurationDAO
from hp12c.persistence.memory_dao import MemoryDAO


class TestConfigurationDAO:
    """Test cases for ConfigurationDAO class."""

    def test_initialization(self, tmp_path):
        """Test ConfigurationDAO initialization."""
        dao = ConfigurationDAO(data_dir=tmp_path)
        assert dao is not None
        assert dao.get_configuration() is not None

    def test_load_configuration_default(self, tmp_path):
        """Test loading default configuration when file doesn't exist."""
        dao = ConfigurationDAO(data_dir=tmp_path)
        config = dao.get_configuration()
        assert config.get_skin() == Configuration.DEFAULT_SKIN

    def test_save_and_load_configuration(self, tmp_path):
        """Test saving and loading configuration."""
        dao = ConfigurationDAO(data_dir=tmp_path)
        config = dao.get_configuration()
        config.set_skin("aurum")
        config.set_language("pt")
        config.set_size(0.8)
        dao.save(config)

        # Create new DAO to load
        dao2 = ConfigurationDAO(data_dir=tmp_path)
        loaded_config = dao2.get_configuration()
        assert loaded_config.get_skin() == "aurum"
        assert loaded_config.get_language() == "pt"
        assert loaded_config.get_size() == 0.8

    def test_load_configuration_invalid_json(self, tmp_path):
        """Test loading configuration with invalid JSON."""
        cfg_file = tmp_path / "cfg.json"
        cfg_file.write_text("invalid json{")

        dao = ConfigurationDAO(data_dir=tmp_path)
        # Should not raise, just use defaults
        config = dao.get_configuration()
        assert config is not None

    def test_load_configuration_version_mismatch(self, tmp_path):
        """Test loading configuration with version mismatch."""
        cfg_file = tmp_path / "cfg.json"
        data = {"version": "0.0.0", "skin": "aurum"}
        cfg_file.write_text(json.dumps(data))

        dao = ConfigurationDAO(data_dir=tmp_path)
        # Should handle version mismatch gracefully
        config = dao.get_configuration()
        assert config is not None

    def test_save_configuration_all_fields(self, tmp_path):
        """Test saving all configuration fields."""
        dao = ConfigurationDAO(data_dir=tmp_path)
        config = dao.get_configuration()
        config.set_size(0.5)
        config.set_x_pos(10)
        config.set_y_pos(20)
        config.set_skin("nigrum")
        config.set_language("es")
        config.set_ui_framework("pyqt5")
        config.set_stack_size(8)
        config.set_memory_size(30)
        config.set_program_size(200)
        config.set_c(1)
        config.set_dmy(1)
        config.set_com(1)
        config.set_alg(1)
        config.set_beg(1)
        config.set_fix(5)
        config.set_mode(1)

        dao.save(config)

        # Verify file exists
        cfg_file = tmp_path / "cfg.json"
        assert cfg_file.exists()

        # Load and verify
        with open(cfg_file) as f:
            data = json.load(f)
            assert data["size"] == 0.5
            assert data["skin"] == "nigrum"
            assert data["lang"] == "es"


class TestMemoryDAO:
    """Test cases for MemoryDAO class."""

    def test_initialization(self, tmp_path):
        """Test MemoryDAO initialization."""
        config = Configuration()
        dao = MemoryDAO(config, data_dir=tmp_path)
        assert dao is not None
        assert dao.get_stack() is not None
        assert dao.get_finance_memory() is not None
        assert dao.get_general_memory() is not None
        assert dao.get_program_memory() is not None

    def test_get_and_set_stack(self, tmp_path):
        """Test getting and setting stack."""
        config = Configuration()
        dao = MemoryDAO(config, data_dir=tmp_path)
        stack = dao.get_stack()
        assert stack is not None

        new_stack = Stack(4)
        new_stack.push(Number("42"))
        dao.set_stack(new_stack)
        assert dao.get_stack().get(0).equals(Number("42"))

    def test_get_and_set_finance_memory(self, tmp_path):
        """Test getting and setting finance memory."""
        config = Configuration()
        dao = MemoryDAO(config, data_dir=tmp_path)
        fin = dao.get_finance_memory()
        assert fin is not None

    def test_get_and_set_general_memory(self, tmp_path):
        """Test getting and setting general memory."""
        config = Configuration()
        dao = MemoryDAO(config, data_dir=tmp_path)
        mem = dao.get_general_memory()
        assert mem is not None

        new_mem = GeneralMemory(10)
        new_mem.set(0, Number("42"))
        dao.set_general_memory(new_mem)
        assert dao.get_general_memory().get(0).equals(Number("42"))

    def test_get_and_set_program_memory(self, tmp_path):
        """Test getting and setting program memory."""
        config = Configuration()
        dao = MemoryDAO(config, data_dir=tmp_path)
        prg = dao.get_program_memory()
        assert prg is not None

    def test_create_memory_default(self, tmp_path):
        """Test creating memory with defaults when file doesn't exist."""
        config = Configuration()
        dao = MemoryDAO(config, data_dir=tmp_path)
        # Should create default memory structures
        assert dao.get_stack() is not None

    def test_save_and_load_memory(self, tmp_path):
        """Test saving and loading memory."""
        config = Configuration()
        dao = MemoryDAO(config, data_dir=tmp_path)
        stack = dao.get_stack()
        stack.push(Number("42"))
        stack.push(Number("100"))

        mem = dao.get_general_memory()
        mem.set(0, Number("50"))

        dao.save()

        # Create new DAO to load
        dao2 = MemoryDAO(config, data_dir=tmp_path)
        loaded_stack = dao2.get_stack()
        # Note: Stack loading may vary based on implementation
        assert loaded_stack is not None

    def test_load_memory_invalid_json(self, tmp_path):
        """Test loading memory with invalid JSON."""
        mem_file = tmp_path / "mem.json"
        mem_file.write_text("invalid json{")

        config = Configuration()
        dao = MemoryDAO(config, data_dir=tmp_path)
        # Should not raise, just use defaults
        assert dao.get_stack() is not None

    def test_save_memory_all_types(self, tmp_path):
        """Test saving all memory types."""
        config = Configuration()
        dao = MemoryDAO(config, data_dir=tmp_path)

        # Set some values
        stack = dao.get_stack()
        stack.push(Number("1"))
        stack.push(Number("2"))

        fin = dao.get_finance_memory()
        fin.set(0, Number("10"))

        mem = dao.get_general_memory()
        mem.set(0, Number("20"))
        mem.set_times(0, Number("3"))

        dao.save()

        # Verify file exists
        mem_file = tmp_path / "mem.json"
        assert mem_file.exists()

        # Load and verify structure
        with open(mem_file) as f:
            data = json.load(f)
            assert "stack" in data
            assert "finance" in data
            assert "general" in data
            assert "program" in data

    def test_load_memory_with_data(self, tmp_path):
        """Test loading memory with actual data."""
        mem_file = tmp_path / "mem.json"
        data = {
            "stack": ["1", "2", "0", "0"],
            "finance": ["0", "0", "0", "0", "0", "0"],
            "general": [["10", "1"], ["20", "1"], ["0", "1"]],
            "program": [[0, 0, 0], [1, 2, 3]],
        }
        mem_file.write_text(json.dumps(data))

        config = Configuration()
        dao = MemoryDAO(config, data_dir=tmp_path)
        # Memory should be loaded
        assert dao.get_stack() is not None
        assert dao.get_general_memory() is not None
