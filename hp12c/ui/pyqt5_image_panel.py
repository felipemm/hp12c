"""
PyQt5 image panel widget for HP12C calculator.
Equivalent to Tkinter ImagePanel but using PyQt5.
"""

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtCore import Qt
from PIL import Image
from typing import Optional
from pathlib import Path


class PyQt5ImagePanel(QWidget):
    """Custom widget with background image support using PyQt5."""

    def __init__(self, parent=None, image_path: Optional[str] = None, image: Optional[Image.Image] = None):
        """Initialize image panel."""
        super().__init__(parent)
        self._pixmap = None
        self._image = None

        if image_path:
            self.set_image(image_path)
        elif image:
            self.set_image_obj(image)

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
            self._update_pixmap()
            self.update()  # Trigger repaint

    def _update_pixmap(self):
        """Update QPixmap from PIL Image."""
        if self._image:
            try:
                # Convert PIL Image to QPixmap
                # PIL Image to bytes, then to QPixmap
                from PyQt5.QtGui import QImage
                import io

                # Convert PIL Image to bytes
                img_bytes = io.BytesIO()
                self._image.save(img_bytes, format='PNG')
                img_bytes.seek(0)

                # Create QImage from bytes
                qimage = QImage()
                qimage.loadFromData(img_bytes.getvalue())

                # Convert to QPixmap
                self._pixmap = QPixmap.fromImage(qimage)
            except Exception as e:
                print(f"Error converting image to QPixmap: {e}")
                self._pixmap = None

    def paintEvent(self, event):
        """Paint background image.

        Matches Java ImagePanel.paintComponent behavior:
        - Scales image to exact widget dimensions (no aspect ratio preservation)
        - Draws at (0, 0) to align with button positions
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self._pixmap:
            # Scale pixmap to exact widget size (ignore aspect ratio, like Java fitImage)
            # This ensures buttons align with background image buttons
            scaled_pixmap = self._pixmap.scaled(
                self.width(),
                self.height(),
                Qt.IgnoreAspectRatio,
                Qt.SmoothTransformation
            )
            # Draw at (0, 0) to match Java/Tkinter behavior (not centered)
            painter.drawPixmap(0, 0, scaled_pixmap)
        else:
            # Fill with black if no image
            painter.fillRect(self.rect(), Qt.black)

    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)
        if self._image:
            self._update_pixmap()
            self.update()
