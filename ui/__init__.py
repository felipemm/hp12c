"""UI components for HP12C calculator."""

from hp12c_python_java_port.ui.image_button import ImageButton
from hp12c_python_java_port.ui.image_panel import ImagePanel
from hp12c_python_java_port.ui.text_field import TextField
from hp12c_python_java_port.ui.base_main_window import BaseMainWindow
from hp12c_python_java_port.ui.tkinter_main_window import TkinterMainWindow

# Try to import PyQt5 components (optional)
try:
    from hp12c_python_java_port.ui.pyqt5_main_window import PyQt5MainWindow
    __all__ = ['ImageButton', 'ImagePanel', 'TextField', 'BaseMainWindow',
                'TkinterMainWindow', 'PyQt5MainWindow', 'create_main_window']
except ImportError:
    PyQt5MainWindow = None
    __all__ = ['ImageButton', 'ImagePanel', 'TextField', 'BaseMainWindow',
                'TkinterMainWindow', 'create_main_window']


def create_main_window(framework: str, controller):
    """Factory function to create main window based on framework preference.

    Args:
        framework: UI framework name ("tkinter" or "pyqt5")
        controller: Controller instance

    Returns:
        BaseMainWindow instance

    Raises:
        ValueError: If framework is invalid
        ImportError: If PyQt5 is requested but not available
    """
    if framework == "pyqt5":
        if PyQt5MainWindow is None:
            raise ImportError("PyQt5 is not installed. Install it with: pip install PyQt5")
        return PyQt5MainWindow(controller)
    elif framework == "tkinter":
        return TkinterMainWindow(controller)
    else:
        raise ValueError(f"Invalid framework: {framework}. Must be 'tkinter' or 'pyqt5'")
