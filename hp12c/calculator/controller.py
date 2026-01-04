"""
Controller to connect calculator, window, and persistence.
Ported from Java Controller.java.
"""

from hp12c.calculator.calculator import Calculator
from hp12c.calculator.config import Configuration
from hp12c.calculator.key import Key
from hp12c.persistence.config_dao import ConfigurationDAO
from hp12c.persistence.memory_dao import MemoryDAO
from hp12c.ui.base_main_window import BaseMainWindow
from hp12c.utils.logger import get_logger


class Controller:
    """Main controller connecting calculator, window, and persistence."""

    def __init__(self):
        """Initialize controller."""
        self._logger = get_logger(__name__)
        self._executor: Calculator | None = None
        self._window: BaseMainWindow | None = None
        self._memd: MemoryDAO | None = None
        self._cfgd: ConfigurationDAO | None = None
        self._cfg: Configuration | None = None
        self.init()

    def init(self) -> None:
        """Initialize controller."""
        self.load_configs()
        self.load_memory()
        self.init_window()
        self.init_executor()
        if self._window:
            try:
                self._window.update_display()
            except (RuntimeError, AttributeError) as e:
                # Handle cases where GUI widgets are deleted or unavailable
                # This can happen in test environments or when GUI framework fails
                self._logger.warning(f"Could not update display: {e}")
        self.welcome_message()

    def init_window(self) -> None:
        """Initialize window based on configuration."""
        ui_framework = self._cfg.get_ui_framework() if self._cfg else "tkinter"

        # Try requested framework first, with tkinter as fallback
        if ui_framework == "pyqt5":
            try:
                from hp12c.ui.pyqt5_main_window import PyQt5MainWindow

                self._window = PyQt5MainWindow(self)
                self._logger.info("Using PyQt5 UI framework")
                self.set_window_configs()
                return
            except ImportError as e:
                self._logger.warning(f"PyQt5 not available ({e}), falling back to Tkinter")
                ui_framework = "tkinter"
                if self._cfg:
                    self._cfg.set_ui_framework("tkinter")

        # Try Tkinter (either requested or as fallback from PyQt5)
        if ui_framework == "tkinter":
            try:
                from hp12c.ui.tkinter_main_window import TkinterMainWindow

                self._window = TkinterMainWindow(self)
                self._logger.info("Using Tkinter UI framework")
                self.set_window_configs()
                return
            except ImportError as e:
                self._logger.warning(f"Tkinter not available ({e}), trying PyQt5 as fallback")
                # Try PyQt5 as fallback when tkinter fails
                try:
                    from hp12c.ui.pyqt5_main_window import PyQt5MainWindow

                    self._window = PyQt5MainWindow(self)
                    self._logger.info("Using PyQt5 UI framework (fallback from Tkinter)")
                    if self._cfg:
                        self._cfg.set_ui_framework("pyqt5")
                    self.set_window_configs()
                    return
                except ImportError as e2:
                    raise ImportError(
                        "Neither Tkinter nor PyQt5 is available. "
                        "Please install PyQt5 with: pip install PyQt5"
                    ) from e2
            except Exception as e:
                # Catch TclError and other runtime errors when Tcl/Tk not properly installed
                error_type = type(e).__name__
                if error_type == "TclError":
                    self._logger.warning(f"Tcl/Tk not available ({e}), trying PyQt5 as fallback")
                else:
                    self._logger.warning(
                        f"Tkinter initialization failed ({e}), trying PyQt5 as fallback"
                    )
                # Try PyQt5 as fallback when tkinter fails
                try:
                    from hp12c.ui.pyqt5_main_window import PyQt5MainWindow

                    self._window = PyQt5MainWindow(self)
                    self._logger.info("Using PyQt5 UI framework (fallback from Tkinter)")
                    if self._cfg:
                        self._cfg.set_ui_framework("pyqt5")
                    self.set_window_configs()
                    return
                except ImportError as e2:
                    raise ImportError(
                        "Neither Tkinter nor PyQt5 is available. "
                        "Please install PyQt5 with: pip install PyQt5"
                    ) from e2

        # Should not reach here, but just in case
        raise ValueError(f"Invalid or unsupported UI framework: {ui_framework}")

    def init_executor(self) -> None:
        """Initialize calculator executor."""
        self._executor = Calculator()
        self._executor.set_controller(self)
        self.set_executor_configs()
        self.set_executor_memory()

    def load_configs(self) -> None:
        """Load configuration."""
        self._cfgd = ConfigurationDAO()
        self._cfg = self._cfgd.get_configuration()

    def save_configs(self) -> None:
        """Save configuration."""
        if self._window and self._executor and self._cfgd and self._cfg:
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

    def set_window_configs(self) -> None:
        """Set window configuration."""
        if self._window and self._cfg:
            self._window.set_configs(self._cfg)

    def set_executor_configs(self) -> None:
        """Set executor configuration."""
        if self._executor and self._cfg:
            self._executor.set_configs(self._cfg)

    def load_memory(self) -> None:
        """Load memory."""
        if self._cfg:
            self._memd = MemoryDAO(self._cfg)

    def save_memory(self) -> None:
        """Save memory."""
        if self._memd and self._executor:
            self._memd.set_stack(self._executor.get_stack())
            self._memd.set_finance_memory(self._executor.get_finance_memory())
            self._memd.set_general_memory(self._executor.get_general_memory())
            self._memd.set_program_memory(self._executor.get_program_memory())
            self._memd.save()

    def set_executor_memory(self) -> None:
        """Set executor memory."""
        if self._memd and self._executor:
            self._executor.set_stack(self._memd.get_stack())
            self._executor.set_finance_memory(self._memd.get_finance_memory())
            self._executor.set_general_memory(self._memd.get_general_memory())
            self._executor.set_program_memory(self._memd.get_program_memory())
            self._executor.update_display()

    def key_pressed(self, key: Key) -> None:
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

    def get_executor(self) -> Calculator | None:
        """Get calculator executor."""
        return self._executor

    def get_window(self) -> BaseMainWindow | None:
        """Get main window."""
        return self._window

    def get_configs(self) -> Configuration | None:
        """Get configuration."""
        return self._cfg

    def quit(self):
        """Quit application."""
        self.save_configs()
        self.save_memory()
        if self._window:
            self._window.close()

    def copy_from_display_value(self):
        """Copy current display value to clipboard."""
        if not self._executor:
            return

        # Get the value from stack register X (display)
        value = self._executor.get_stack().get(0)
        str_value = str(value)

        # Replace decimal point with comma if comma mode is enabled
        if self._executor.get_display().get_comma():
            str_value = str_value.replace(".", ",")

        # Copy to clipboard (implementation depends on UI framework)
        if self._window:
            self._window.copy_to_clipboard(str_value)

    def paste_to_display_value(self):
        """Paste value from clipboard to display."""
        if not self._executor:
            return

        # Get text from clipboard (implementation depends on UI framework)
        if not self._window:
            return

        clipboard_text = self._window.get_from_clipboard()
        if not clipboard_text:
            return

        try:
            # Process the text: remove commas, replace comma with dot if comma mode
            if self._executor.get_display().get_comma():
                # In comma mode: remove dots, replace commas with dots
                processed_text = clipboard_text.replace(".", "").replace(",", ".")
            else:
                # In dot mode: just remove commas
                processed_text = clipboard_text.replace(",", "")

            # Parse as double
            from hp12c.hp12c_math.number import Number

            val = Number.n(float(processed_text))

            # Set the value in the calculator
            self._executor.set_x(val)
            self._executor.get_display().set_value(val)
            self._executor.update_display()
            if self._window:
                self._window.update_display()
        except (ValueError, Exception):
            # Silently ignore invalid clipboard content
            pass

    def erase_display(self):
        """Erase display value."""
        if not self._executor:
            return
        from hp12c.hp12c_math.number import Number
        from hp12c.model.display import Display

        display = self._executor.get_display()
        display.set_value(Number.ZERO)
        display.set_status(Display.STATUS_READY)  # Reset status to ready
        self._executor.get_stack().set(0, Number.ZERO)
        self._executor.update_display()
        if self._window:
            self._window.update_display()
            # Update register view if open
            if hasattr(self._window, "_update_register_view"):
                self._window._update_register_view()

    def erase_stack(self):
        """Erase stack registers."""
        if not self._executor:
            return
        from hp12c.hp12c_math.number import Number
        from hp12c.model.display import Display

        display = self._executor.get_display()
        display.set_value(Number.ZERO)
        display.set_status(Display.STATUS_READY)  # Reset status to ready
        self._executor.get_stack().clear()
        self._executor.update_display()
        if self._window:
            self._window.update_display()
            # Update register view if open
            if hasattr(self._window, "_update_register_view"):
                self._window._update_register_view()

    def erase_finance(self):
        """Erase finance registers."""
        if not self._executor:
            return
        self._executor.get_finance_memory().clear()
        if self._window:
            self._window.update_display()
            # Update register view if open
            if hasattr(self._window, "_update_register_view"):
                self._window._update_register_view()

    def erase_statistic(self):
        """Erase statistic registers."""
        if not self._executor:
            return
        self._executor.get_general_memory().clear_stats()
        if self._window:
            self._window.update_display()
            # Update register view if open
            if hasattr(self._window, "_update_register_view"):
                self._window._update_register_view()

    def erase_all_registers(self):
        """Erase all general memory registers."""
        if not self._executor:
            return
        self._executor.get_general_memory().clear()
        if self._window:
            self._window.update_display()
            # Update register view if open
            if hasattr(self._window, "_update_register_view"):
                self._window._update_register_view()

    def erase_program(self):
        """Erase program steps."""
        if not self._executor:
            return
        self._executor.get_program_memory().clear()
        if self._window:
            self._window.update_display()
            # Note: Program memory changes don't affect register view

    def welcome_message(self) -> None:
        """Show welcome message."""
        self._logger.info(f"HP12C Calculator - Python Port (Version: {Configuration.VERSION})")
