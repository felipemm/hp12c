"""
Controller to connect calculator, window, and persistence.
Ported from Java Controller.java.
"""

from typing import Optional
from hp12c_python_java_port.calculator.calculator import Calculator
from hp12c_python_java_port.calculator.config import Configuration
from hp12c_python_java_port.calculator.key import Key
from hp12c_python_java_port.persistence.config_dao import ConfigurationDAO
from hp12c_python_java_port.persistence.memory_dao import MemoryDAO
from hp12c_python_java_port.ui.base_main_window import BaseMainWindow


class Controller:
    """Main controller connecting calculator, window, and persistence."""

    def __init__(self):
        """Initialize controller."""
        self._executor: Optional[Calculator] = None
        self._window: Optional[BaseMainWindow] = None
        self._memd: Optional[MemoryDAO] = None
        self._cfgd: Optional[ConfigurationDAO] = None
        self._cfg: Optional[Configuration] = None
        self.init()

    def init(self):
        """Initialize controller."""
        self.load_configs()
        self.load_memory()
        self.init_window()
        self.init_executor()
        if self._window:
            self._window.update_display()
        self.welcome_message()

    def init_window(self):
        """Initialize window based on configuration."""
        ui_framework = self._cfg.get_ui_framework() if self._cfg else "tkinter"

        if ui_framework == "pyqt5":
            try:
                from hp12c_python_java_port.ui.pyqt5_main_window import PyQt5MainWindow
                self._window = PyQt5MainWindow(self)
                print(f"Using PyQt5 UI framework")
            except ImportError as e:
                print(f"PyQt5 not available ({e}), falling back to Tkinter")
                from hp12c_python_java_port.ui.tkinter_main_window import TkinterMainWindow
                self._window = TkinterMainWindow(self)
                # Update config to use tkinter
                if self._cfg:
                    self._cfg.set_ui_framework("tkinter")
        else:
            # Default to Tkinter
            from hp12c_python_java_port.ui.tkinter_main_window import TkinterMainWindow
            self._window = TkinterMainWindow(self)

        self.set_window_configs()

    def init_executor(self):
        """Initialize calculator executor."""
        self._executor = Calculator()
        self._executor.set_controller(self)
        self.set_executor_configs()
        self.set_executor_memory()

    def load_configs(self):
        """Load configuration."""
        self._cfgd = ConfigurationDAO()
        self._cfg = self._cfgd.get_configuration()

    def save_configs(self):
        """Save configuration."""
        if self._window and self._executor and self._cfgd:
            x, y = self._window.get_window_location()
            self._cfg.set_x_pos(x)
            self._cfg.set_y_pos(y)
            self._cfg.set_alg(self._executor.get_flags().get_alg())
            self._cfg.set_beg(self._executor.get_flags().get_begin())
            self._cfg.set_c(self._executor.get_flags().get_c())
            self._cfg.set_com(1 if self._executor.get_display().get_comma() else 0)
            self._cfg.set_dmy(self._executor.get_flags().get_dmy())
            self._cfg.set_fix(self._executor.get_display().get_precision())
            self._cfg.set_mode(self._executor.get_display().get_mode())
            self._cfgd.save(self._cfg)

    def set_window_configs(self):
        """Set window configuration."""
        if self._window and self._cfg:
            self._window.set_configs(self._cfg)

    def set_executor_configs(self):
        """Set executor configuration."""
        if self._executor and self._cfg:
            self._executor.set_configs(self._cfg)

    def load_memory(self):
        """Load memory."""
        if self._cfg:
            self._memd = MemoryDAO(self._cfg)

    def save_memory(self):
        """Save memory."""
        if self._memd and self._executor:
            self._memd.set_stack(self._executor.get_stack())
            self._memd.set_finance_memory(self._executor.get_finance_memory())
            self._memd.set_general_memory(self._executor.get_general_memory())
            self._memd.set_program_memory(self._executor.get_program_memory())
            self._memd.save()

    def set_executor_memory(self):
        """Set executor memory."""
        if self._memd and self._executor:
            self._executor.set_stack(self._memd.get_stack())
            self._executor.set_finance_memory(self._memd.get_finance_memory())
            self._executor.set_general_memory(self._memd.get_general_memory())
            self._executor.set_program_memory(self._memd.get_program_memory())
            self._executor.update_display()

    def key_pressed(self, key: Key):
        """Handle key press."""
        if self._executor:
            self._executor.key_pressed(key)
        if self._window:
            self._window.key_pressed(key)

    def key_released(self, key: Key):
        """Handle key release."""
        if self._executor:
            self._executor.key_released(key)
        if self._window:
            self._window.key_released(key)

    def get_executor(self) -> Optional[Calculator]:
        """Get calculator executor."""
        return self._executor

    def get_window(self) -> Optional[BaseMainWindow]:
        """Get main window."""
        return self._window

    def get_configs(self) -> Optional[Configuration]:
        """Get configuration."""
        return self._cfg

    def quit(self):
        """Quit application."""
        self.save_configs()
        self.save_memory()
        if self._window:
            self._window.hide()

    def welcome_message(self):
        """Show welcome message."""
        print("HP12C Calculator - Python Port")
        print("Version:", Configuration.VERSION)
