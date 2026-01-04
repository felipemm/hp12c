"""
Image button for HP12C calculator.
Ported from Java ImageButton.java using Tkinter.
"""

import tkinter as tk
from PIL import Image, ImageTk
from typing import Optional
from hp12c.calculator.key import Key


class ImageButton(tk.Button):
    """Custom button with image support."""

    def __init__(self, parent=None, image_path: Optional[str] = None, image: Optional[Image.Image] = None, key: Optional[Key] = None, **kwargs):
        """Initialize image button."""
        self._image = None
        self._photo = None
        self._key = key

        # Initialize parent first
        super().__init__(parent, **kwargs)
        self.init()

        # Set image after widget is initialized
        if image_path:
            self.set_image(image_path)
        elif image:
            self.set_image_obj(image)

    def init(self):
        """Initialize button (no-op)."""
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
            self._photo = ImageTk.PhotoImage(img)
            self.config(image=self._photo)
            # Keep reference to prevent garbage collection
            if not hasattr(self, '_image_refs'):
                self._image_refs = []
            self._image_refs.append(self._photo)

    def set_key(self, key: Key):
        """Set associated key."""
        self._key = key

    def get_key(self) -> Optional[Key]:
        """Get associated key."""
        return self._key

    def fit_image(self):
        """Fit image to button size."""
        if self._image:
            width = self.winfo_width()
            height = self.winfo_height()
            if width > 1 and height > 1:
                resized = self._image.resize((width, height), Image.Resampling.LANCZOS)
                self.set_image_obj(resized)
