"""
Text field for display.
Ported from Java TextField.java using Tkinter Entry.
"""

import tkinter as tk


class TextField(tk.Entry):
    """Custom text field with anti-aliasing support."""

    def __init__(self, parent=None, text: str = "", **kwargs):
        """Initialize text field."""
        self._anti_alias = False
        super().__init__(parent, **kwargs)
        if text:
            self.insert(0, text)
        self.init()

    def init(self):
        """Initialize text field."""
        self._anti_alias = False

    def set_anti_alias(self, aa: bool):
        """Set anti-aliasing (not directly supported in Tkinter, but kept for API compatibility)."""
        self._anti_alias = aa
