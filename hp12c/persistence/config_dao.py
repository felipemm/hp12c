"""
Configuration persistence using JSON.
Ported from Java ConfigurationDAO.java (using JSON instead of XML).
"""

import json
import os
from pathlib import Path
from hp12c.calculator.config import Configuration


class ConfigurationDAO:
    """Data access object for configuration persistence."""

    def __init__(self):
        """Initialize configuration DAO."""
        self._cfg = Configuration.create_configuration()
        self._path = Path("data") / "cfg.json"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self.load_configuration()

    def get_configuration(self) -> Configuration:
        """Get configuration."""
        return self._cfg

    def load_configuration(self):
        """Load configuration from file."""
        if not self._path.exists():
            return

        try:
            with open(self._path, 'r') as f:
                data = json.load(f)

            if 'version' in data:
                v = data['version']
                if v != Configuration.VERSION and v != "ALL":
                    raise IOError(f"[Version] Incompatible version: {v}")

            if 'size' in data:
                self._cfg.set_size(float(data['size']))
            if 'xpos' in data:
                self._cfg.set_x_pos(int(data['xpos']))
            if 'ypos' in data:
                self._cfg.set_y_pos(int(data['ypos']))
            if 'skin' in data:
                self._cfg.set_skin(data['skin'])
            if 'lang' in data:
                self._cfg.set_language(data['lang'])
            if 'ui_framework' in data:
                self._cfg.set_ui_framework(data['ui_framework'])
            if 'stksize' in data:
                self._cfg.set_stack_size(int(data['stksize']))
            if 'memsize' in data:
                self._cfg.set_memory_size(int(data['memsize']))
            if 'prgsize' in data:
                self._cfg.set_program_size(int(data['prgsize']))
            if 'c' in data:
                self._cfg.set_c(int(data['c']))
            if 'dmy' in data:
                self._cfg.set_dmy(int(data['dmy']))
            if 'com' in data:
                self._cfg.set_com(int(data['com']))
            if 'alg' in data:
                self._cfg.set_alg(int(data['alg']))
            if 'beg' in data:
                self._cfg.set_beg(int(data['beg']))
            if 'fix' in data:
                self._cfg.set_fix(int(data['fix']))
            if 'mode' in data:
                self._cfg.set_mode(int(data['mode']))
        except Exception as e:
            print(f"Error loading configuration: {e}")

    def save(self, conf: Configuration):
        """Save configuration to file."""
        data = {
            'version': Configuration.VERSION,
            'size': conf.get_size(),
            'xpos': conf.get_x_pos(),
            'ypos': conf.get_y_pos(),
            'skin': conf.get_skin(),
            'lang': conf.get_language(),
            'ui_framework': conf.get_ui_framework(),
            'stksize': conf.get_stack_size(),
            'memsize': conf.get_memory_size(),
            'prgsize': conf.get_program_size(),
            'c': conf.get_c(),
            'dmy': conf.get_dmy(),
            'com': conf.get_com(),
            'alg': conf.get_alg(),
            'beg': conf.get_beg(),
            'fix': conf.get_fix(),
            'mode': conf.get_mode(),
        }

        try:
            with open(self._path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving configuration: {e}")
