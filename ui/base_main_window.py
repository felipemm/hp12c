"""
Base abstract interface for MainWindow implementations.
Defines the common interface that both Tkinter and PyQt5 implementations must provide.
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
from hp12c_python_java_port.calculator.key import Key
from hp12c_python_java_port.calculator.config import Configuration


class BaseMainWindow(ABC):
    """Abstract base class for main calculator window implementations."""

    @abstractmethod
    def __init__(self, controller):
        """Initialize main window."""
        pass

    @abstractmethod
    def update_display(self):
        """Update display from calculator."""
        pass

    @abstractmethod
    def key_pressed(self, key: Key):
        """Handle key press (visual feedback)."""
        pass

    @abstractmethod
    def key_released(self, key: Key):
        """Handle key release."""
        pass

    @abstractmethod
    def show(self):
        """Show window."""
        pass

    @abstractmethod
    def hide(self):
        """Hide window."""
        pass

    @abstractmethod
    def get_window_location(self) -> Tuple[int, int]:
        """Get window location."""
        pass

    @abstractmethod
    def set_configs(self, cfg: Configuration):
        """Set configuration."""
        pass

    @abstractmethod
    def get_frame(self):
        """Get the main window widget/frame (tk.Tk or QMainWindow)."""
        pass
