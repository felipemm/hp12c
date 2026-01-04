"""
Configuration persistence using JSON.
Ported from Java ConfigurationDAO.java (using JSON instead of XML).
"""

import json
import os
from pathlib import Path

try:
    from platformdirs import user_data_dir

    _HAS_PLATFORMDIRS = True
except ImportError:
    _HAS_PLATFORMDIRS = False

from hp12c.calculator.config import Configuration
from hp12c.utils.logger import get_logger


class ConfigurationDAO:
    """Data access object for configuration persistence."""

    def __init__(self, data_dir: Path | None = None) -> None:
        """Initialize configuration DAO.

        Args:
            data_dir: Optional custom data directory. If None, uses:
                     - Environment variable HP12C_DATA_DIR if set
                     - platformdirs user_data_dir if available
                     - "data" directory in current working directory (fallback)
        """
        self._logger = get_logger(__name__)
        self._cfg = Configuration.create_configuration()

        # Determine data directory
        if data_dir:
            self._data_dir = Path(data_dir)
        elif env_dir := os.getenv("HP12C_DATA_DIR"):
            self._data_dir = Path(env_dir)
        elif _HAS_PLATFORMDIRS:
            self._data_dir = Path(user_data_dir("hp12c", "hp12c"))
        else:
            self._data_dir = Path("data")

        self._path = self._data_dir / "cfg.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self.load_configuration()

    def get_configuration(self) -> Configuration:
        """Get configuration."""
        return self._cfg

    def load_configuration(self) -> None:
        """Load configuration from file."""
        if not self._path.exists():
            return

        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)

            if "version" in data:
                v = data["version"]
                if v != Configuration.VERSION and v != "ALL":
                    raise OSError(f"[Version] Incompatible version: {v}")

            if "size" in data:
                self._cfg.set_size(float(data["size"]))
            if "xpos" in data:
                self._cfg.set_x_pos(int(data["xpos"]))
            if "ypos" in data:
                self._cfg.set_y_pos(int(data["ypos"]))
            if "skin" in data:
                self._cfg.set_skin(data["skin"])
            if "lang" in data:
                self._cfg.set_language(data["lang"])
            if "ui_framework" in data:
                self._cfg.set_ui_framework(data["ui_framework"])
            if "stksize" in data:
                self._cfg.set_stack_size(int(data["stksize"]))
            if "memsize" in data:
                self._cfg.set_memory_size(int(data["memsize"]))
            if "prgsize" in data:
                self._cfg.set_program_size(int(data["prgsize"]))
            if "c" in data:
                self._cfg.set_c(int(data["c"]))
            if "dmy" in data:
                self._cfg.set_dmy(int(data["dmy"]))
            if "com" in data:
                self._cfg.set_com(int(data["com"]))
            if "alg" in data:
                self._cfg.set_alg(int(data["alg"]))
            if "beg" in data:
                self._cfg.set_beg(int(data["beg"]))
            if "fix" in data:
                self._cfg.set_fix(int(data["fix"]))
            if "mode" in data:
                self._cfg.set_mode(int(data["mode"]))
            self._logger.debug(f"Configuration loaded successfully from {self._path}")
        except json.JSONDecodeError as e:
            self._logger.error(f"Invalid JSON in configuration file {self._path}: {e}")
            # Continue with default configuration
        except OSError as e:
            self._logger.error(f"IO error loading configuration from {self._path}: {e}")
            # Continue with default configuration
        except Exception as e:
            self._logger.error(f"Error loading configuration from {self._path}: {e}")
            # Continue with default configuration

    def save(self, conf: Configuration) -> None:
        """Save configuration to file."""
        data = {
            "version": Configuration.VERSION,
            "size": conf.get_size(),
            "xpos": conf.get_x_pos(),
            "ypos": conf.get_y_pos(),
            "skin": conf.get_skin(),
            "lang": conf.get_language(),
            "ui_framework": conf.get_ui_framework(),
            "stksize": conf.get_stack_size(),
            "memsize": conf.get_memory_size(),
            "prgsize": conf.get_program_size(),
            "c": conf.get_c(),
            "dmy": conf.get_dmy(),
            "com": conf.get_com(),
            "alg": conf.get_alg(),
            "beg": conf.get_beg(),
            "fix": conf.get_fix(),
            "mode": conf.get_mode(),
        }

        try:
            with open(self._path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            self._logger.debug(f"Configuration saved successfully to {self._path}")
        except OSError as e:
            self._logger.error(f"IO error saving configuration to {self._path}: {e}")
        except Exception as e:
            self._logger.error(f"Error saving configuration to {self._path}: {e}")
