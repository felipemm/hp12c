"""UI components for HP12C calculator."""

from hp12c.ui.base_main_window import BaseMainWindow

# Try to import Tkinter components (optional)
try:
    from hp12c.ui.image_button import ImageButton
    from hp12c.ui.image_panel import ImagePanel
    from hp12c.ui.text_field import TextField
    from hp12c.ui.tkinter_main_window import TkinterMainWindow
    _tkinter_available = True
except ImportError:
    ImageButton = None
    ImagePanel = None
    TextField = None
    TkinterMainWindow = None
    _tkinter_available = False

# Try to import PyQt5 components (optional)
try:
    from hp12c.ui.pyqt5_main_window import PyQt5MainWindow
    _pyqt5_available = True
except ImportError:
    PyQt5MainWindow = None
    _pyqt5_available = False

# Build __all__ based on what's available
__all__ = ['BaseMainWindow', 'create_main_window']
if _tkinter_available:
    __all__.extend(['ImageButton', 'ImagePanel', 'TextField', 'TkinterMainWindow'])
if _pyqt5_available:
    __all__.append('PyQt5MainWindow')


def create_main_window(framework: str, controller):
    """Factory function to create main window based on framework preference.

    Args:
        framework: UI framework name ("tkinter" or "pyqt5")
        controller: Controller instance

    Returns:
        BaseMainWindow instance

    Raises:
        ValueError: If framework is invalid
        ImportError: If requested framework is not available
    """
    if framework == "pyqt5":
        if not _pyqt5_available or PyQt5MainWindow is None:
            raise ImportError("PyQt5 is not installed. Install it with: pip install PyQt5")
        return PyQt5MainWindow(controller)
    elif framework == "tkinter":
        if not _tkinter_available or TkinterMainWindow is None:
            raise ImportError("Tkinter is not available. This Python installation may not have Tkinter support.")
        return TkinterMainWindow(controller)
    else:
        raise ValueError(f"Invalid framework: {framework}. Must be 'tkinter' or 'pyqt5'")
