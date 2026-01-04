"""
PyQt5 image button widget for HP12C calculator.
Equivalent to Tkinter ImageButton but using PyQt5.
"""

import io

from PIL import Image
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QPushButton

from hp12c.calculator.key import Key


class PyQt5ImageButton(QPushButton):
    """Custom button with image support using PyQt5."""

    # Signal emitted when button is clicked
    clicked_with_key = pyqtSignal(object)  # Emits Key object

    def __init__(
        self,
        parent=None,
        image_path: str | None = None,
        image: Image.Image | None = None,
        key: Key | None = None,
    ):
        """Initialize image button."""
        super().__init__(parent)
        self._image: Image.Image | None = None
        self._pixmap: QPixmap | None = None
        self._key: Key | None = key

        # Set button properties
        self.setFlat(True)  # No border
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)  # Don't take keyboard focus

        if image_path:
            self.set_image(image_path)
        elif image:
            self.set_image_obj(image)

        # Connect clicked signal
        self.clicked.connect(self._on_clicked)

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

    def _update_pixmap(self):
        """Update QPixmap from PIL Image."""
        if self._image:
            try:
                from PyQt5.QtGui import QImage

                # Convert PIL Image to bytes
                img_bytes = io.BytesIO()
                self._image.save(img_bytes, format="PNG")
                img_bytes.seek(0)

                # Create QImage from bytes
                qimage = QImage()
                qimage.loadFromData(img_bytes.getvalue())

                # Convert to QPixmap
                self._pixmap = QPixmap.fromImage(qimage)

                # Set as button icon
                icon = QIcon(self._pixmap)
                self.setIcon(icon)
                self.setIconSize(self._pixmap.size())
            except Exception as e:
                print(f"Error converting image to QPixmap: {e}")
                self._pixmap = None

    def set_key(self, key: Key):
        """Set associated key."""
        self._key = key

    def get_key(self) -> Key | None:
        """Get associated key."""
        return self._key

    def _on_clicked(self):
        """Handle button click."""
        if self._key:
            self.clicked_with_key.emit(self._key)

    def resizeEvent(self, event):
        """Handle resize event."""
        super().resizeEvent(event)
        if self._image:
            # Resize image to button size
            resized = self._image.resize((self.width(), self.height()), Image.Resampling.LANCZOS)
            self.set_image_obj(resized)
