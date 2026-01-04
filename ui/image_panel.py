"""
Image panel for HP12C calculator.
Ported from Java ImagePanel.java using Tkinter Canvas.
"""

import tkinter as tk
from PIL import Image, ImageTk
from typing import Optional


class ImagePanel(tk.Canvas):
    """Custom panel with background image support."""

    def __init__(self, parent=None, image_path: Optional[str] = None, image: Optional[Image.Image] = None, **kwargs):
        """Initialize image panel."""
        self._image = None
        self._photo = None

        # Initialize parent first
        super().__init__(parent, **kwargs)
        self.init()
        self.bind('<Configure>', self._on_configure)

        # Set image after widget is initialized
        if image_path:
            self.set_image(image_path)
        elif image:
            self.set_image_obj(image)

    def init(self):
        """Initialize panel (no-op)."""
        pass

    def set_image(self, url: str):
        """Set image from file path."""
        if url:
            try:
                img = Image.open(url)
                self.set_image_obj(img)
            except Exception as e:
                print(f"Error loading image {url}: {e}")

    def set_image_obj(self, img: Image.Image):
        """Set image from PIL Image."""
        if img:
            self._image = img
            self._update_display()

    def _on_configure(self, event):
        """Handle resize event."""
        if self._image:
            self._update_display()

    def _update_display(self):
        """Update displayed image."""
        if self._image:
            try:
                width = self.winfo_width()
                height = self.winfo_height()
                if width > 1 and height > 1:
                    resized = self._image.resize((width, height), Image.Resampling.LANCZOS)
                    self._photo = ImageTk.PhotoImage(resized)
                    self.delete("all")
                    self.create_image(0, 0, anchor=tk.NW, image=self._photo)
                else:
                    # Initial size or not yet configured, use original image
                    self._photo = ImageTk.PhotoImage(self._image)
                    self.delete("all")
                    self.create_image(0, 0, anchor=tk.NW, image=self._photo)
            except (AttributeError, tk.TclError):
                # Widget not yet fully initialized, just store the image
                # It will be displayed when the widget is configured
                self._photo = ImageTk.PhotoImage(self._image)
                self.delete("all")
                self.create_image(0, 0, anchor=tk.NW, image=self._photo)

    def fit_image(self):
        """Fit image to panel size."""
        self._update_display()
