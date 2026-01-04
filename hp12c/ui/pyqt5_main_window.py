"""
PyQt5 implementation of main window for HP12C calculator.
Ported from Java MainWindow.java using PyQt5 for better font rendering.
"""

import contextlib
import xml.etree.ElementTree as ET
from abc import ABCMeta
from pathlib import Path

from PIL import Image, ImageFont
from PyQt5.QtCore import QRect, Qt, QTimer
from PyQt5.QtGui import (
    QColor,
    QFont,
    QFontDatabase,
    QFontMetrics,
    QIcon,
    QKeySequence,
    QPainter,
    QPixmap,
)
from PyQt5.QtWidgets import QAction, QActionGroup, QApplication, QMainWindow, QMessageBox

from hp12c.calculator.config import Configuration
from hp12c.calculator.key import Key
from hp12c.ui.base_main_window import BaseMainWindow
from hp12c.ui.pyqt5_image_button import PyQt5ImageButton
from hp12c.ui.pyqt5_image_panel import PyQt5ImagePanel
from hp12c.utils.language_loader import LanguageLoader
from hp12c.utils.logger import get_logger
from hp12c.utils.skin_loader import SkinLoader

# Create a combined metaclass for ABC + QMainWindow
# PyQt5 classes use a custom metaclass, so we need to combine ABCMeta with it
ABCQMainWindowMeta: type[type]
try:
    # Try to get QMainWindow's metaclass
    _qmainwindow_meta = type(QMainWindow)
    if _qmainwindow_meta is type:
        # If QMainWindow uses the default type metaclass, we can just use ABCMeta
        ABCQMainWindowMeta = ABCMeta
    else:
        # Combine both metaclasses
        class _ABCQMainWindowMetaImpl(ABCMeta, _qmainwindow_meta):  # type: ignore[misc, valid-type]
            """Metaclass that combines ABCMeta with QMainWindow's metaclass."""

            pass

        ABCQMainWindowMeta = _ABCQMainWindowMetaImpl

except Exception:
    # Fallback: just use ABCMeta
    ABCQMainWindowMeta = ABCMeta


class DisplayWidget(PyQt5ImagePanel):
    """Widget that displays calculator text over the background image."""

    def __init__(self, parent=None):
        """Initialize display widget."""
        super().__init__(parent)
        # Ensure widget can have child widgets and allows absolute positioning
        self.setAttribute(Qt.WidgetAttribute.WA_StaticContents, False)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, False)
        self._display_text = ""
        self._flag_text = ""
        self._display_font = None
        self._flag_font = None
        self._display_color = QColor("#00FF00")
        self._display_x = 0
        self._display_y = 0
        self._flag_x = 0
        self._flag_y = 0
        self._display_width = 300  # Default display width
        self._flag_width = 400  # Default flag width

    def set_display_text(self, text: str):
        """Set main display text."""
        self._display_text = text
        with contextlib.suppress(RuntimeError):
            # Widget has been deleted (can happen in test environments)
            self.update()

    def set_flag_text(self, text: str):
        """Set flag display text."""
        self._flag_text = text
        with contextlib.suppress(RuntimeError):
            # Widget has been deleted (can happen in test environments)
            self.update()

    def set_display_font(self, font: QFont):
        """Set display font."""
        self._display_font = font
        self.update()

    def set_flag_font(self, font: QFont):
        """Set flag font."""
        self._flag_font = font
        self.update()

    def set_display_color(self, color: QColor):
        """Set display text color."""
        self._display_color = color
        self.update()

    def set_display_position(self, x: int, y: int):
        """Set main display position."""
        self._display_x = x
        self._display_y = y

    def set_flag_position(self, x: int, y: int):
        """Set flag display position."""
        self._flag_x = x
        self._flag_y = y

    def set_display_width(self, width: int):
        """Set display width for text rectangle."""
        self._display_width = width

    def set_flag_width(self, width: int):
        """Set flag width for text rectangle."""
        self._flag_width = width

    def paintEvent(self, event):
        """Paint background and text."""
        # Paint background first
        super().paintEvent(event)

        # Then paint text with anti-aliasing
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.TextAntialiasing)

        # Draw main display text
        if self._display_font and self._display_text:
            painter.setFont(self._display_font)
            painter.setPen(self._display_color)
            # Right-aligned text
            rect = QRect(
                self._display_x - self._display_width,
                self._display_y - self._display_font.pointSize() // 2,
                self._display_width,
                self._display_font.pointSize() * 2,
            )
            painter.drawText(
                rect,
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                self._display_text,
            )

        # Draw flag display text
        # Use black color for flags
        if self._flag_font and self._flag_text:
            painter.setFont(self._flag_font)
            painter.setPen(QColor(0, 0, 0))  # Black color
            # Right-aligned text, constrained to fit within LCD display area
            # Calculate text width (use horizontalAdvance for newer PyQt5, fallback to width for older)
            try:
                text_width = painter.fontMetrics().horizontalAdvance(self._flag_text)
            except AttributeError:
                text_width = painter.fontMetrics().width(self._flag_text)
            # Constrain rectangle width to flag_width (LCD display width) to fit in LCD area
            # Use minimal padding to ensure text fits
            padding = max(10, int(self._flag_width * 0.05))  # 5% of flag width, minimum 10
            rect_width = min(self._flag_width, text_width + padding)  # Don't exceed LCD width
            rect = QRect(
                self._flag_x - rect_width,
                self._flag_y - self._flag_font.pointSize() // 2,
                rect_width,
                self._flag_font.pointSize() * 2,
            )
            # Use elided text if it's too long to fit
            if text_width > rect_width - padding:
                elided_text = painter.fontMetrics().elidedText(
                    self._flag_text, Qt.TextElideMode.ElideRight, rect_width - padding
                )
                painter.drawText(
                    rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter, elided_text
                )
            else:
                painter.drawText(
                    rect,
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                    self._flag_text,
                )
        elif self._flag_text:
            # Debug: flag text exists but font is missing
            self._logger.warning(f"Flag text exists ('{self._flag_text}') but flag font is not set")
        elif self._flag_font:
            # Debug: flag font exists but text is missing
            self._logger.warning(
                f"Flag font is set but flag text is empty (flag_x={self._flag_x}, flag_y={self._flag_y})"
            )


class PyQt5MainWindow(BaseMainWindow, QMainWindow, metaclass=ABCQMainWindowMeta):  # type: ignore[misc]
    """PyQt5 implementation of main calculator window."""

    def __init__(self, controller):
        """Initialize main window."""
        # Ensure QApplication exists before creating QMainWindow
        app = QApplication.instance()
        if app is None:
            import sys

            app = QApplication(sys.argv)

        BaseMainWindow.__init__(self, controller)
        QMainWindow.__init__(self)
        self._logger = get_logger(__name__)
        self._controller = controller
        self._frame = None  # QMainWindow
        self._main_panel = None  # DisplayWidget
        self._display_widget = None  # DisplayWidget for text rendering
        self._base_path = Path("resources")
        self._skin_path = None
        self._skin_font_path = None
        self._buttons: dict[str, PyQt5ImageButton] = {}
        self._image_map: dict[str, Image.Image] = {}
        self._image_map_pressed: dict[str, Image.Image] = {}
        self._bg_image = None
        self._font = None  # PIL ImageFont
        self._qt_font = None  # QFont
        self._flag_font = None  # QFont for flags
        self._cfg = None
        self._skin = None
        self._language_loader = None  # Language string loader
        self._skin_loader = None  # Skin list loader
        self._menu_bar = None  # Menu bar
        self._register_view_window = None  # Register view window

        # Size variables (defaults, will be scaled)
        self._hbot = 40
        self._wbot = 45
        self._hebot = 106
        self._webot = 45
        self._hmainpan = 400
        self._wmainpan = 640
        self._hdispan = 110
        self._wdispan = 300
        self._xpad = 6
        self._ypad = 11
        self._hdis = 40
        self._wdis = 300
        self._hfdis = 15
        self._wfdis = 300
        self._font_size = 29
        # Display padding (insets) for positioning
        self._tdis = 0
        self._ldis = 0
        self._bdis = 0
        self._rdis = 100
        self._tfdis = 0
        self._lfdis = 0
        self._bfdis = 30
        self._rfdis = 100
        # LCD position on background image
        self._lcd_x = 200
        self._lcd_y = 18

        # Colors
        self._face_color = None
        self._display_bg_color = None
        self._display_face_color = None
        self._button_bg_color = None
        self._button_face_color = None

        self.init()

    def init(self):
        """Initialize window."""
        if self._controller:
            self._cfg = self._controller.get_configs()
        if not self._cfg:
            self._cfg = Configuration()

        if self._cfg:
            self.set_size(self._cfg.get_size())
        # Find paths before loading skin so we know where to look
        self.find_paths()
        self.load_skin()
        self.load_language()
        self.load_skin_list()
        self.build()

    def build(self):
        """Build the window."""
        # Ensure QApplication exists before creating any widgets
        from PyQt5.QtWidgets import QApplication

        app = QApplication.instance()
        if app is None:
            import sys

            app = QApplication(sys.argv)
            self._logger.debug("QApplication created in PyQt5MainWindow.build()")

        # Paths already found in init(), just build image maps
        self.build_image_maps()

        window_title = f"HP12C Calculator - v{Configuration.VERSION}"
        # Use self as the QMainWindow instead of creating a separate _frame
        self.setWindowTitle(window_title)
        self.setFixedSize(self._wmainpan, self._hmainpan)
        self._frame = self  # Keep _frame reference for compatibility

        # Set icon if available
        self.set_icon()

        # Build menu bar (after frame is created)
        self.build_menu_bar()

        # Build layout (after frame is created)
        self.build_layout()
        self.fix_window_location()

    def find_paths(self):
        """Find resource paths."""
        # Get the directory where this module is located
        module_dir = Path(__file__).parent.parent
        self._base_path = module_dir / "resources"

        # Raise exception if resources directory doesn't exist
        if not self._base_path.exists():
            raise FileNotFoundError(
                f"Resources directory not found at: {self._base_path}\n"
                f"Module directory: {module_dir}\n"
                f"Expected resources at: {self._base_path}"
            )

        skin_name = (
            self._cfg.get_skin()
            if self._cfg and self._cfg.get_skin()
            else Configuration.DEFAULT_SKIN
        )
        self._skin_path = self._base_path / "skins" / skin_name
        self._skin_font_path = self._skin_path / "font.ttf"

        self._logger.debug(f"Base path: {self._base_path}")
        self._logger.debug(f"Skin path: {self._skin_path}")
        self._logger.debug(f"Skin path exists: {self._skin_path.exists()}")

    def load_skin(self):
        """Load skin configuration."""
        skin_name = (
            self._cfg.get_skin()
            if self._cfg and self._cfg.get_skin()
            else Configuration.DEFAULT_SKIN
        )
        skin_file = self._base_path / "skins" / skin_name / "skn.xml"

        self._logger.debug(f"Loading skin from: {skin_file}")
        self._logger.debug(f"Skin file exists: {skin_file.exists()}")

        if skin_file.exists():
            try:
                tree = ET.parse(skin_file)
                root = tree.getroot()
                self._skin = {}
                for child in root:
                    self._skin[child.tag] = child.text
                self._logger.debug(
                    f"Successfully loaded skin XML with {len(self._skin)} properties"
                )
            except Exception as e:
                self._logger.error(f"Error loading skin: {e}")
                self._skin = {}
        else:
            self._logger.warning(f"Skin file not found at: {skin_file}")
            self._skin = {}

        # Set default colors if not in skin
        # XML uses hyphenated tag names (e.g., "display-face-color"), not camelCase
        self._face_color = self._hex_to_color(
            self._skin.get("face-color", self._skin.get("bgColor", "#000000"))
        )
        self._display_bg_color = self._hex_to_color(
            self._skin.get("display-bg-color", self._skin.get("displayBgColor", "#000000"))
        )
        self._display_face_color = self._hex_to_color(
            self._skin.get("display-face-color", self._skin.get("displayFaceColor", "#00FF00"))
        )
        self._button_bg_color = self._hex_to_color(
            self._skin.get("button-bg-color", self._skin.get("buttonBgColor", "#000000"))
        )
        self._button_face_color = self._hex_to_color(
            self._skin.get("button-face-color", self._skin.get("buttonFaceColor", "#FFFFFF"))
        )

        # Debug: print loaded colors
        self._logger.debug("Loaded skin colors:")
        self._logger.debug(
            f"  display-face-color: {self._skin.get('display-face-color', 'NOT FOUND')}"
        )
        self._logger.debug(f"  display_face_color: {self._display_face_color}")

    def _hex_to_color(self, hex_str: str) -> str:
        """Convert hex color string to QColor-compatible format."""
        if hex_str.startswith("#"):
            return hex_str
        return f"#{hex_str}"

    def _set_default_size(self):
        """Reset all size variables to default values (same as Java setDefaultSize)."""
        self._hbot = 40
        self._wbot = 45
        self._hebot = 106
        self._webot = 45
        self._hmainpan = 400
        self._wmainpan = 640
        self._hdispan = 69
        self._wdispan = 300
        self._xpad = 6
        self._ypad = 11
        self._hdis = 40
        self._wdis = 300
        self._hfdis = 15
        self._wfdis = 300
        self._font_size = 29
        # Display padding (insets) for positioning
        self._tdis = 0
        self._ldis = 0
        self._bdis = 0
        self._rdis = 100
        self._tfdis = 0
        self._lfdis = 0
        self._bfdis = 10
        self._rfdis = 100
        # LCD position on background image
        self._lcd_x = 200
        self._lcd_y = 18

    def set_size(self, size: float):
        """Set window size multiplier (same as Java setSize - resets to defaults first, then scales)."""
        # Reset to defaults first (prevents compounding if called multiple times)
        self._set_default_size()
        self._size = size
        # Now scale all values
        self._hbot = int(self._hbot * size)
        self._wbot = int(self._wbot * size)
        self._hebot = int(self._hebot * size)
        self._webot = int(self._webot * size)
        self._hmainpan = int(self._hmainpan * size)
        self._wmainpan = int(self._wmainpan * size)
        self._hdispan = int(self._hdispan * size)
        self._wdispan = int(self._wdispan * size)
        self._xpad = int(round(self._xpad * size))
        self._ypad = int(round(self._ypad * size))
        self._hdis = int(self._hdis * size)
        self._wdis = int(self._wdis * size)
        self._hfdis = int(self._hfdis * size)
        self._wfdis = int(self._wfdis * size)
        self._font_size = int(self._font_size * size)
        # Scale display padding
        self._tdis = int(self._tdis * size)
        self._ldis = int(self._ldis * size)
        self._bdis = int(self._bdis * size)
        self._rdis = int(self._rdis * size)
        self._tfdis = int(self._tfdis * size)
        self._lfdis = int(self._lfdis * size)
        self._bfdis = int(self._bfdis * size)
        self._rfdis = int(self._rfdis * size)
        # Scale LCD position
        self._lcd_x = int(self._lcd_x * size)
        self._lcd_y = int(self._lcd_y * size)

        # If window is already built, reload fonts with new size
        if self._main_panel is not None:
            self.load_font()
            # Update display widget with new fonts
            if self._qt_font:
                self._main_panel.set_display_font(self._qt_font)
            if self._flag_font:
                self._main_panel.set_flag_font(self._flag_font)

    def create_image_icon(self, w: int, h: int, path: str) -> Image.Image | None:
        """Create scaled image icon."""
        try:
            # Try base_path first (should be set correctly in find_paths)
            full_path = self._base_path / path
            if not full_path.exists():
                # Try relative to module directory
                module_dir = Path(__file__).parent.parent
                full_path = module_dir / "resources" / path
            if not full_path.exists():
                # Try relative to current working directory
                full_path = Path("hp12c") / "resources" / path
            if not full_path.exists():
                # Try as resource path relative to current directory
                full_path = Path("resources") / path

            if full_path.exists():
                img = Image.open(full_path)
                return img.resize((w, h), Image.Resampling.LANCZOS)
            else:
                # Only print if it's a critical image (background or button)
                if "background" in path or "buttons" in path:
                    self._logger.debug(f"Image not found: {path} (tried: {full_path})")
        except Exception as e:
            self._logger.error(f"Error loading image {path}: {e}")
        return None

    def build_image_maps(self):
        """Build image maps for buttons."""
        # Construct relative path from base_path
        skin_name = self._skin_path.name if self._skin_path else Configuration.DEFAULT_SKIN
        skin_path_str = f"skins/{skin_name}/"

        # Background image
        bg_img = self.create_image_icon(
            self._wmainpan, self._hmainpan, f"{skin_path_str}background.png"
        )
        if bg_img:
            self._bg_image = bg_img
            self._logger.debug(f"Background image loaded: {skin_path_str}background.png")
        else:
            self._logger.warning(f"Failed to load background image: {skin_path_str}background.png")

        # Button images - normal and pressed
        button_codes = [
            (0, Key.KEY_0),
            (1, Key.KEY_1),
            (2, Key.KEY_2),
            (3, Key.KEY_3),
            (4, Key.KEY_4),
            (5, Key.KEY_5),
            (6, Key.KEY_6),
            (7, Key.KEY_7),
            (8, Key.KEY_8),
            (9, Key.KEY_9),
            (10, Key.KEY_DIV),
            (11, Key.KEY_N),
            (12, Key.KEY_I),
            (13, Key.KEY_PV),
            (14, Key.KEY_PMT),
            (15, Key.KEY_FV),
            (16, Key.KEY_CHS),
            (20, Key.KEY_MUL),
            (21, Key.KEY_POW),
            (22, Key.KEY_RECIPROCAL),
            (23, Key.KEY_PERC_TOT),
            (24, Key.KEY_PERC_DELTA),
            (25, Key.KEY_PERC),
            (26, Key.KEY_EEX),
            (30, Key.KEY_SUB),
            (31, Key.KEY_RS),
            (32, Key.KEY_SST),
            (33, Key.KEY_ROLL),
            (34, Key.KEY_XY),
            (35, Key.KEY_CLX),
            (36, Key.KEY_ENTER),
            (40, Key.KEY_SUM),
            (41, Key.KEY_ON),
            (42, Key.KEY_F),
            (43, Key.KEY_G),
            (44, Key.KEY_STO),
            (45, Key.KEY_RCL),
            (48, Key.KEY_DOT),
            (49, Key.KEY_TOT),
        ]

        loaded_count = 0
        for code, key in button_codes:
            # Normal button
            btn_size = (self._webot, self._hebot) if code == 36 else (self._wbot, self._hbot)
            img_path = f"{skin_path_str}buttons/b{code:02d}.png"
            img = self.create_image_icon(btn_size[0], btn_size[1], img_path)
            if img:
                self._image_map[key.name] = img
                loaded_count += 1
            else:
                self._logger.warning(f"Failed to load button image: {img_path}")

            # Pressed button
            img_pressed_path = f"{skin_path_str}buttons/b{code:02d}p.png"
            img_pressed = self.create_image_icon(btn_size[0], btn_size[1], img_pressed_path)
            if img_pressed:
                self._image_map_pressed[key.name] = img_pressed

        self._logger.debug(f"Loaded {loaded_count}/{len(button_codes)} button images")

    def load_font(self):
        """Load font from skin using PyQt5."""
        try:
            if self._skin_font_path and self._skin_font_path.exists():
                # Load PIL font for image rendering (if needed)
                self._font = ImageFont.truetype(str(self._skin_font_path), self._font_size)

                # Load PyQt5 font - can load directly from file
                font_id = QFontDatabase.addApplicationFont(str(self._skin_font_path))
                if font_id != -1:
                    font_families = QFontDatabase.applicationFontFamilies(font_id)
                    if font_families:
                        font_family = font_families[0]
                        self._qt_font = QFont(font_family, self._font_size)
                        self._qt_font.setHintingPreference(QFont.PreferFullHinting)
                        self._logger.debug(
                            f"Loaded skin font: {font_family} (size: {self._font_size})"
                        )
                    else:
                        self._logger.warning(
                            "Could not get font family from loaded font, using Courier"
                        )
                        self._qt_font = QFont("Courier", self._font_size)
                else:
                    self._logger.warning("Could not load font from file, using Courier")
                    self._qt_font = QFont("Courier", self._font_size)

                # Create flag font - matches Java code: new Font("monospaced", 0, this.fontSize / 3)
                flag_font_size = int(self._font_size / 3)
                # Use monospace font (matches Java's "monospaced" logical font)
                monospace_families = [
                    "Courier",
                    "Courier New",
                    "Monaco",
                    "Consolas",
                    "Liberation Mono",
                    "DejaVu Sans Mono",
                ]
                flag_font_created = False
                for family in monospace_families:
                    font = QFont(family, flag_font_size)
                    font.setHintingPreference(QFont.PreferFullHinting)
                    # Check if font is available by creating a font metrics
                    fm = QFontMetrics(font)
                    if fm.averageCharWidth() > 0:  # Valid font if it has character width
                        self._flag_font = font
                        self._logger.debug(
                            f"Created flag font (monospace): {family}, size: {flag_font_size}"
                        )
                        flag_font_created = True
                        break

                if not flag_font_created:
                    # Fallback to Courier (most common monospace font)
                    self._flag_font = QFont("Courier", flag_font_size)
                    self._flag_font.setHintingPreference(QFont.PreferFullHinting)
                    self._logger.debug(
                        f"Created flag font (monospace fallback): Courier, size: {flag_font_size}"
                    )
            else:
                # Font file not found, use default
                self._logger.warning(f"Font file not found: {self._skin_font_path}, using Courier")
                self._font = ("Courier", self._font_size)
                self._qt_font = QFont("Courier", self._font_size)
                # Create flag font - matches Java code: new Font("monospaced", 0, this.fontSize / 3)
                flag_font_size = int(self._font_size / 3)
                # Use monospace font (matches Java's "monospaced" logical font)
                monospace_families = [
                    "Courier",
                    "Courier New",
                    "Monaco",
                    "Consolas",
                    "Liberation Mono",
                    "DejaVu Sans Mono",
                ]
                flag_font_created = False
                for family in monospace_families:
                    font = QFont(family, flag_font_size)
                    font.setHintingPreference(QFont.PreferFullHinting)
                    fm = QFontMetrics(font)
                    if fm.averageCharWidth() > 0:
                        self._flag_font = font
                        print(
                            f"Created flag font (monospace fallback): {family}, size: {flag_font_size}"
                        )
                        flag_font_created = True
                        break

                if not flag_font_created:
                    self._flag_font = QFont("Courier", flag_font_size)
                    self._flag_font.setHintingPreference(QFont.PreferFullHinting)
                    self._logger.debug(
                        f"Created flag font (monospace fallback): Courier, size: {flag_font_size}"
                    )
        except Exception as e:
            self._logger.error(f"Error loading font: {e}")
            import traceback

            traceback.print_exc()
            self._font = ("Courier", self._font_size)
            self._qt_font = QFont("Courier", self._font_size)
            # Create flag font - matches Java code: new Font("monospaced", 0, this.fontSize / 3)
            flag_font_size = int(self._font_size / 3)
            # Use monospace font (matches Java's "monospaced" logical font)
            monospace_families = [
                "Courier",
                "Courier New",
                "Monaco",
                "Consolas",
                "Liberation Mono",
                "DejaVu Sans Mono",
            ]
            flag_font_created = False
            for family in monospace_families:
                font = QFont(family, flag_font_size)
                font.setHintingPreference(QFont.PreferFullHinting)
                fm = QFontMetrics(font)
                if fm.averageCharWidth() > 0:
                    self._flag_font = font
                    self._logger.debug(
                        f"Created flag font (monospace error fallback): {family}, size: {flag_font_size}"
                    )
                    flag_font_created = True
                    break

            if not flag_font_created:
                self._flag_font = QFont("Courier", flag_font_size)
                self._flag_font.setHintingPreference(QFont.PreferFullHinting)
                print(
                    f"Created flag font (monospace error fallback): Courier, size: {flag_font_size}"
                )

    def build_layout(self):
        """Build the window layout."""
        # Load font (must be after QApplication is created)
        self.load_font()

        # Create main panel with background
        if self._bg_image:
            self._main_panel = DisplayWidget(self._frame)
            self._main_panel.set_image_obj(self._bg_image)
        else:
            self._main_panel = DisplayWidget(self._frame)
            self._main_panel.setStyleSheet("background-color: #000000;")

        self._main_panel.setFixedSize(self._wmainpan, self._hmainpan)
        # Ensure no layout manager so absolute positioning works
        # Also ensure no margins/padding that could affect child widget positioning
        # _main_panel is always assigned above (either in if or else branch), so it's never None
        self._main_panel.setContentsMargins(0, 0, 0, 0)
        # Explicitly disable auto-fill background which might interfere
        self._main_panel.setAutoFillBackground(False)
        # QMainWindow's central widget area might have margins - set them to 0
        self.setCentralWidget(self._main_panel)
        # Ensure the central widget area has no margins
        central_widget = self.centralWidget()
        if central_widget:
            central_widget.setContentsMargins(0, 0, 0, 0)
        # Force update to ensure widget is properly sized before positioning children
        self._main_panel.update()
        # Ensure the main panel is at position (0,0) within its parent
        self._main_panel.move(0, 0)
        # Force the main panel to update its geometry
        self._main_panel.updateGeometry()

        # Set display properties
        display_x = self._lcd_x + self._wdis - self._rdis
        display_y = self._lcd_y + self._hdis // 2
        # Flag position: relative to LCD position
        flag_x = self._lcd_x + self._wfdis - self._rfdis
        flag_y = self._lcd_y + self._hdis + self._bfdis + self._hfdis // 2

        # Set display widget properties
        if self._qt_font:
            self._main_panel.set_display_font(self._qt_font)
        if self._flag_font:
            self._main_panel.set_flag_font(self._flag_font)

        display_color = QColor(self._display_face_color)
        self._main_panel.set_display_color(display_color)
        self._main_panel.set_display_position(display_x, display_y)
        self._main_panel.set_flag_position(flag_x, flag_y)
        # Set scaled widths for text rectangles
        # Flag width should match display width to fit within LCD area
        self._main_panel.set_display_width(self._wdis)
        self._main_panel.set_flag_width(self._wdis)  # Use same width as display to fit in LCD area

        # Debug: print color and position info
        self._logger.debug(f"Display color: {self._display_face_color}")
        self._logger.debug(f"LCD position on image: x={self._lcd_x}, y={self._lcd_y}")
        self._logger.debug(f"Display text position: x={display_x}, y={display_y}")
        self._logger.debug(f"Flag text position: x={flag_x}, y={flag_y}")
        self._logger.debug(
            f"Flag font: {self._flag_font.family() if self._flag_font else 'None'}, size: {self._flag_font.pointSize() if self._flag_font else 'None'}"
        )
        self._logger.debug(f"Flag width: {self._wfdis}, Flag height: {self._hfdis}")
        self._logger.debug(
            f"Flag display width: {self._main_panel._flag_width if hasattr(self._main_panel, '_flag_width') else 'N/A'}"
        )

        # Build buttons with exact layout from Java
        self._build_buttons()

    def _build_buttons(self):
        """Build buttons matching Java layout exactly."""
        # Button layout: (gridx, gridy, key, rowspan)
        button_layout = [
            # Row 1 (gridy=1)
            (0, 1, Key.KEY_N, 1),
            (1, 1, Key.KEY_I, 1),
            (2, 1, Key.KEY_PV, 1),
            (3, 1, Key.KEY_PMT, 1),
            (4, 1, Key.KEY_FV, 1),
            (5, 1, Key.KEY_CHS, 1),
            (6, 1, Key.KEY_7, 1),
            (7, 1, Key.KEY_8, 1),
            (8, 1, Key.KEY_9, 1),
            (9, 1, Key.KEY_DIV, 1),
            # Row 2 (gridy=2)
            (0, 2, Key.KEY_POW, 1),
            (1, 2, Key.KEY_RECIPROCAL, 1),
            (2, 2, Key.KEY_PERC_TOT, 1),
            (3, 2, Key.KEY_PERC_DELTA, 1),
            (4, 2, Key.KEY_PERC, 1),
            (5, 2, Key.KEY_EEX, 1),
            (6, 2, Key.KEY_4, 1),
            (7, 2, Key.KEY_5, 1),
            (8, 2, Key.KEY_6, 1),
            (9, 2, Key.KEY_MUL, 1),
            # Row 3 (gridy=3)
            (0, 3, Key.KEY_RS, 1),
            (1, 3, Key.KEY_SST, 1),
            (2, 3, Key.KEY_ROLL, 1),
            (3, 3, Key.KEY_XY, 1),
            (4, 3, Key.KEY_CLX, 1),
            (5, 3, Key.KEY_ENTER, 2),  # ENTER spans 2 rows
            (6, 3, Key.KEY_1, 1),
            (7, 3, Key.KEY_2, 1),
            (8, 3, Key.KEY_3, 1),
            (9, 3, Key.KEY_SUB, 1),
            # Row 4 (gridy=4)
            (0, 4, Key.KEY_ON, 1),
            (1, 4, Key.KEY_F, 1),
            (2, 4, Key.KEY_G, 1),
            (3, 4, Key.KEY_STO, 1),
            (4, 4, Key.KEY_RCL, 1),
            # ENTER button continues from row 3 (no button at 5,4)
            (6, 4, Key.KEY_0, 1),
            (7, 4, Key.KEY_DOT, 1),
            (8, 4, Key.KEY_TOT, 1),
            (9, 4, Key.KEY_SUM, 1),
        ]

        for gridx, gridy, key, _rowspan in button_layout:
            if key == Key.KEY_NULL:
                continue

            key_name = key.name

            # Get button size
            if key == Key.KEY_ENTER:
                btn_width = self._webot
                btn_height = self._hebot
            else:
                btn_width = self._wbot
                btn_height = self._hbot

            # Create button with explicit parent
            if key_name in self._image_map:
                img = self._image_map[key_name]
                # Create button with image
                btn = PyQt5ImageButton(self._main_panel, image=img, key=key)
            else:
                # Fallback: create text button if image not available
                btn_text = self._get_button_text(key)
                btn = PyQt5ImageButton(self._main_panel, key=key)
                btn.setText(btn_text)
                btn.setStyleSheet(
                    f"background-color: {self._button_bg_color}; color: {self._button_face_color};"
                )

            # Explicitly set parent to ensure proper parent-child relationship
            btn.setParent(self._main_panel)
            # Ensure button allows absolute positioning
            btn.setAutoFillBackground(False)

            # Calculate position (same as Tkinter/Java)
            x = gridx * (self._wbot + 2 * self._xpad) + self._xpad + int(35 * self._size)
            y = self._hdispan + gridy * (self._hbot + 2 * self._ypad) + self._ypad

            # Debug: print first few button positions to verify calculation
            if len(self._buttons) < 3:
                self._logger.debug(
                    f"Button {key_name}: gridx={gridx}, gridy={gridy}, x={x}, y={y}, size=({btn_width}, {btn_height})"
                )
                self._logger.debug(
                    f"  hdispan={self._hdispan}, hbot={self._hbot}, ypad={self._ypad}"
                )
                if self._main_panel:
                    self._logger.debug(
                        f"  Parent widget size: {self._main_panel.width()}x{self._main_panel.height()}"
                    )
                    self._logger.debug(f"  Parent widget pos: {self._main_panel.pos()}")

            # Position button - ensure it's visible first, then position
            btn.show()  # Make button visible first
            # Position button using setGeometry (position + size) for reliability
            # This ensures the button is positioned correctly relative to parent's (0,0)
            btn.setGeometry(x, y, btn_width, btn_height)
            # Verify the geometry was set correctly
            if len(self._buttons) < 3:
                actual_geom = btn.geometry()
                actual_pos = btn.pos()
                self._logger.debug(
                    f"  Button actual geometry: x={actual_geom.x()}, y={actual_geom.y()}, w={actual_geom.width()}, h={actual_geom.height()}"
                )
                self._logger.debug(f"  Button actual pos: x={actual_pos.x()}, y={actual_pos.y()}")
                if self._main_panel is not None:
                    self._logger.debug(f"  Parent widget rect: {self._main_panel.rect()}")
            btn.raise_()  # Bring button to front
            btn.update()  # Force repaint
            # Force the parent to update as well
            if self._main_panel is not None:
                self._main_panel.update()

            # Connect click handler
            btn.clicked_with_key.connect(lambda k=key: self._on_button_click(k))

            # Store button
            self._buttons[key_name] = btn

    def _get_button_text(self, key: Key) -> str:
        """Get text label for button (fallback when image not available)."""
        text_map = {
            Key.KEY_0: "0",
            Key.KEY_1: "1",
            Key.KEY_2: "2",
            Key.KEY_3: "3",
            Key.KEY_4: "4",
            Key.KEY_5: "5",
            Key.KEY_6: "6",
            Key.KEY_7: "7",
            Key.KEY_8: "8",
            Key.KEY_9: "9",
            Key.KEY_DIV: "/",
            Key.KEY_MUL: "*",
            Key.KEY_SUB: "-",
            Key.KEY_SUM: "+",
            Key.KEY_N: "N",
            Key.KEY_I: "I",
            Key.KEY_PV: "PV",
            Key.KEY_PMT: "PMT",
            Key.KEY_FV: "FV",
            Key.KEY_CHS: "CHS",
            Key.KEY_POW: "y^x",
            Key.KEY_RECIPROCAL: "1/x",
            Key.KEY_PERC_TOT: "%T",
            Key.KEY_PERC_DELTA: "Δ%",
            Key.KEY_PERC: "%",
            Key.KEY_EEX: "EEX",
            Key.KEY_RS: "R/S",
            Key.KEY_SST: "SST",
            Key.KEY_ROLL: "R↓",
            Key.KEY_XY: "x↔y",
            Key.KEY_CLX: "CLX",
            Key.KEY_ENTER: "ENTER",
            Key.KEY_ON: "ON",
            Key.KEY_F: "f",
            Key.KEY_G: "g",
            Key.KEY_STO: "STO",
            Key.KEY_RCL: "RCL",
            Key.KEY_DOT: ".",
            Key.KEY_TOT: "Σ+",
        }
        return text_map.get(key, key.name.replace("KEY_", ""))

    def _on_button_click(self, key: Key):
        """Handle button click."""
        if self._controller:
            # Show pressed state first
            self._controller.key_pressed(key)
            # Then release after a short delay to show the visual effect
            QTimer.singleShot(50, lambda: self._controller.key_released(key))

    def update_display(self):
        """Update display from calculator."""
        if self._controller and self._main_panel:
            executor = self._controller.get_executor()
            if executor:
                display_str = executor.get_display().get_string()
                self._main_panel.set_display_text(display_str)

                flag_str = executor.get_flags().get_display_str()
                # Remove extra spaces to make it more compact
                # flag_str = ' '.join(flag_str.split())  # Collapse multiple spaces to single space
                self._logger.debug(
                    f"Flag display string: '{flag_str}' (length: {len(flag_str) if flag_str else 0})"
                )
                if flag_str:
                    self._main_panel.set_flag_text(flag_str)
                else:
                    # Set empty string explicitly to clear previous flags
                    self._main_panel.set_flag_text("")

    def show(self):
        """Show window."""
        if self._frame:
            self._frame.show()
            # Reposition buttons after window is shown (sometimes needed for QMainWindow)
            self._reposition_buttons()
            self._frame.raise_()
            self._frame.activateWindow()

    def _reposition_buttons(self):
        """Reposition all buttons - sometimes needed after window is shown."""
        for _key_name, btn in self._buttons.items():
            # Get the stored position from button's current geometry
            geom = btn.geometry()
            # Force reposition to ensure it's correct
            btn.setGeometry(geom.x(), geom.y(), geom.width(), geom.height())
            btn.update()

    def hide(self):
        """Hide window."""
        if self._frame:
            self._frame.hide()

    def close(self):
        """Close window and exit application."""
        if self._frame:
            self._frame.close()
        # Exit QApplication if it exists
        from PyQt5.QtWidgets import QApplication

        app = QApplication.instance()
        if app:
            app.quit()

    def get_window_location(self) -> tuple[int, int]:
        """Get window location."""
        if self._frame:
            pos = self._frame.pos()
            return (pos.x(), pos.y())
        return (0, 0)

    def set_configs(self, cfg: Configuration):
        """Set configuration."""
        self._cfg = cfg

    def key_pressed(self, key: Key):
        """Handle key press (visual feedback)."""
        if key and key.name in self._buttons:
            btn = self._buttons[key.name]
            key_name = key.name
            if key_name in self._image_map_pressed:
                pressed_img = self._image_map_pressed[key_name]
                btn.set_image_obj(pressed_img)

    def key_released(self, key: Key):
        """Handle key release."""
        # Check if window still exists (might have been closed)
        if not self._frame:
            return

        if key and key.name in self._buttons:
            btn = self._buttons[key.name]
            key_name = key.name
            if key_name in self._image_map:
                normal_img = self._image_map[key_name]
                btn.set_image_obj(normal_img)
            self.update_display()
            # Auto-refresh register view if open
            self._update_register_view()

    def get_frame(self):
        """Get QMainWindow."""
        return self._frame

    def set_icon(self):
        """Set window icon."""
        try:
            if self._skin_path is None or self._frame is None:
                return
            icon_path = self._skin_path / "icon.png"
            if icon_path.exists():
                icon_pixmap = QPixmap(str(icon_path))
                if not icon_pixmap.isNull():
                    icon = QIcon(icon_pixmap)
                    self._frame.setWindowIcon(icon)
        except Exception as e:
            self._logger.error(f"Error setting icon: {e}")

    def load_language(self):
        """Load language strings."""
        lang = self._cfg.get_language() if self._cfg else "en"
        self._language_loader = LanguageLoader(lang, self._base_path)

    def load_skin_list(self):
        """Load skin list."""
        self._skin_loader = SkinLoader(self._base_path)

    def build_menu_bar(self):
        """Build menu bar with File, Edit, View, Options, Tools, About menus."""
        if not self._language_loader:
            self.load_language()
        if not self._language_loader:
            return  # Cannot build menu without language loader
        # Type assertion: _language_loader is now guaranteed to be non-None
        assert self._language_loader is not None

        self._menu_bar = self.menuBar()
        assert self._menu_bar is not None  # menuBar() always returns a QMenuBar

        # File menu
        file_menu = self._menu_bar.addMenu(self._language_loader.get_value("FILE_MENU", "File"))

        import_action = QAction(
            self._language_loader.get_value("FILE_IMPORT", "Import"), self._frame
        )
        import_action.setShortcut(
            QKeySequence(f"Ctrl+{self._language_loader.get_shortcut('FILE_IMPORT', 'I').upper()}")
        )
        import_action.triggered.connect(self._on_file_import)
        file_menu.addAction(import_action)

        export_action = QAction(
            self._language_loader.get_value("FILE_EXPORT", "Export"), self._frame
        )
        export_action.setShortcut(
            QKeySequence(f"Ctrl+{self._language_loader.get_shortcut('FILE_EXPORT', 'E').upper()}")
        )
        export_action.triggered.connect(self._on_file_export)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction(self._language_loader.get_value("FILE_QUIT", "Quit"), self._frame)
        quit_action.setShortcut(
            QKeySequence(f"Ctrl+{self._language_loader.get_shortcut('FILE_QUIT', 'Q').upper()}")
        )
        quit_action.triggered.connect(self._on_file_quit)
        file_menu.addAction(quit_action)

        # Edit menu
        edit_menu = self._menu_bar.addMenu(self._language_loader.get_value("EDIT_MENU", "Edit"))

        copy_action = QAction(self._language_loader.get_value("EDIT_COPY", "Copy"), self._frame)
        copy_action.setShortcut(
            QKeySequence(f"Ctrl+{self._language_loader.get_shortcut('EDIT_COPY', 'C').upper()}")
        )
        copy_action.triggered.connect(self._on_edit_copy)
        edit_menu.addAction(copy_action)

        paste_action = QAction(self._language_loader.get_value("EDIT_PASTE", "Paste"), self._frame)
        paste_action.setShortcut(
            QKeySequence(f"Ctrl+{self._language_loader.get_shortcut('EDIT_PASTE', 'P').upper()}")
        )
        paste_action.triggered.connect(self._on_edit_paste)
        edit_menu.addAction(paste_action)

        # Erase submenu
        erase_menu = edit_menu.addMenu(self._language_loader.get_value("EDIT_ERASE", "Erase"))

        erase_display_action = QAction(
            self._language_loader.get_value("EDIT_ERASE_DSP", "Display"), self._frame
        )
        erase_display_action.triggered.connect(self._on_edit_erase_display)
        erase_menu.addAction(erase_display_action)

        erase_stack_action = QAction(
            self._language_loader.get_value("EDIT_ERASE_STK", "Stack Registers"), self._frame
        )
        erase_stack_action.triggered.connect(self._on_edit_erase_stack)
        erase_menu.addAction(erase_stack_action)

        erase_finance_action = QAction(
            self._language_loader.get_value("EDIT_ERASE_FIN", "Finance Registers"), self._frame
        )
        erase_finance_action.triggered.connect(self._on_edit_erase_finance)
        erase_menu.addAction(erase_finance_action)

        erase_statistic_action = QAction(
            self._language_loader.get_value("EDIT_ERASE_STA", "Statistic Registers"), self._frame
        )
        erase_statistic_action.triggered.connect(self._on_edit_erase_statistic)
        erase_menu.addAction(erase_statistic_action)

        erase_all_action = QAction(
            self._language_loader.get_value("EDIT_ERASE_REG", "All Registers"), self._frame
        )
        erase_all_action.triggered.connect(self._on_edit_erase_all)
        erase_menu.addAction(erase_all_action)

        erase_program_action = QAction(
            self._language_loader.get_value("EDIT_ERASE_PRG", "Program Steps"), self._frame
        )
        erase_program_action.triggered.connect(self._on_edit_erase_program)
        erase_menu.addAction(erase_program_action)

        # View menu
        view_menu = self._menu_bar.addMenu(self._language_loader.get_value("VIEW_MENU", "View"))

        # Size submenu
        size_menu = view_menu.addMenu(self._language_loader.get_value("VIEW_SIZE", "Size"))
        size_group = QActionGroup(self._frame)

        size_actions = [
            ("0.5", self._language_loader.get_value("VIEW_SIZE_VERY_SMALL", "Very Small")),
            ("0.75", self._language_loader.get_value("VIEW_SIZE_SMALL", "Small")),
            ("1.0", self._language_loader.get_value("VIEW_SIZE_MEDIUM", "Medium")),
            ("1.25", self._language_loader.get_value("VIEW_SIZE_LARGE", "Large")),
            ("1.5", self._language_loader.get_value("VIEW_SIZE_HUGE", "Very Large")),
        ]

        current_size = str(self._cfg.get_size() if self._cfg else 1.0)
        for size_val, label in size_actions:
            size_action = QAction(label, self._frame)
            size_action.setCheckable(True)
            size_action.setChecked(size_val == current_size)
            size_action.setData(size_val)
            size_action.triggered.connect(self._on_view_size)
            size_group.addAction(size_action)
            size_menu.addAction(size_action)

        # Skin submenu
        skin_menu = view_menu.addMenu(
            self._language_loader.get_value("VIEW_SKIN", "Calculator skin")
        )
        skin_group = QActionGroup(self._frame)
        current_skin = self._cfg.get_skin() if self._cfg else Configuration.DEFAULT_SKIN
        if self._skin_loader:
            for skin_id, skin_description in self._skin_loader.get_skins():
                skin_action = QAction(skin_description, self._frame)
                skin_action.setCheckable(True)
                skin_action.setChecked(skin_id == current_skin)
                skin_action.setData(skin_id)
                skin_action.triggered.connect(self._on_view_skin)
                skin_group.addAction(skin_action)
                skin_menu.addAction(skin_action)

        # Options menu
        options_menu = self._menu_bar.addMenu(
            self._language_loader.get_value("OPTIONS_MENU", "Options")
        )

        # Number format submenu
        num_format_menu = options_menu.addMenu(
            self._language_loader.get_value("OPTIONS_NUMBER_FORMAT", "Number Format")
        )
        num_format_group = QActionGroup(self._frame)

        dot_action = QAction(
            self._language_loader.get_value("OPTIONS_NUMBER_FORMAT_DOT", "Dot (.)"), self._frame
        )
        dot_action.setCheckable(True)
        dot_action.setChecked(not self._cfg or self._cfg.get_com() == 0)
        dot_action.setData("dot")
        dot_action.triggered.connect(self._on_options_number_format)
        num_format_group.addAction(dot_action)
        num_format_menu.addAction(dot_action)

        comma_action = QAction(
            self._language_loader.get_value("OPTIONS_NUMBER_FORMAT_COMMA", "Comma (,)"), self._frame
        )
        comma_action.setCheckable(True)
        comma_action.setChecked(bool(self._cfg and self._cfg.get_com() == 1))
        comma_action.setData("comma")
        comma_action.triggered.connect(self._on_options_number_format)
        num_format_group.addAction(comma_action)
        num_format_menu.addAction(comma_action)

        # Date format submenu
        date_format_menu = options_menu.addMenu(
            self._language_loader.get_value("OPTIONS_DATE_FORMAT", "Date Format")
        )
        date_format_group = QActionGroup(self._frame)

        mdy_action = QAction(
            self._language_loader.get_value("OPTIONS_DATE_FORMAT_MONTH", "MM.DDYYYY"), self._frame
        )
        mdy_action.setCheckable(True)
        mdy_action.setChecked(not self._cfg or self._cfg.get_dmy() == 0)
        mdy_action.setData("mdy")
        mdy_action.triggered.connect(self._on_options_date_format)
        date_format_group.addAction(mdy_action)
        date_format_menu.addAction(mdy_action)

        dmy_action = QAction(
            self._language_loader.get_value("OPTIONS_DATE_FORMAT_DAY", "DD.MMYYYY"), self._frame
        )
        dmy_action.setCheckable(True)
        dmy_action.setChecked(bool(self._cfg and self._cfg.get_dmy() == 1))
        dmy_action.setData("dmy")
        dmy_action.triggered.connect(self._on_options_date_format)
        date_format_group.addAction(dmy_action)
        date_format_menu.addAction(dmy_action)

        # Payment mode submenu
        payment_menu = options_menu.addMenu(
            self._language_loader.get_value("OPTIONS_PAYMENT_MODE", "Payment mode")
        )
        payment_group = QActionGroup(self._frame)

        begin_action = QAction(
            self._language_loader.get_value("OPTIONS_PAYMENT_MODE_BEGIN", "Begin"), self._frame
        )
        begin_action.setCheckable(True)
        begin_action.setChecked(bool(self._cfg and self._cfg.get_beg() == 1))
        begin_action.setData("begin")
        begin_action.triggered.connect(self._on_options_payment_mode)
        payment_group.addAction(begin_action)
        payment_menu.addAction(begin_action)

        end_action = QAction(
            self._language_loader.get_value("OPTIONS_PAYMENT_MODE_END", "End"), self._frame
        )
        end_action.setCheckable(True)
        end_action.setChecked(not self._cfg or self._cfg.get_beg() == 0)
        end_action.setData("end")
        end_action.triggered.connect(self._on_options_payment_mode)
        payment_group.addAction(end_action)
        payment_menu.addAction(end_action)

        # Tools menu
        tools_menu = self._menu_bar.addMenu(self._language_loader.get_value("TOOLS_MENU", "Tools"))

        registers_action = QAction(
            self._language_loader.get_value("TOOLS_REGISTERS_VIEW", "Registers view"), self._frame
        )
        registers_action.triggered.connect(self._on_tools_registers_view)
        tools_menu.addAction(registers_action)

        history_action = QAction(
            self._language_loader.get_value("TOOLS_HISTORY", "Instructions history"), self._frame
        )
        history_action.triggered.connect(self._on_tools_history)
        tools_menu.addAction(history_action)

        # About menu
        about_menu = self._menu_bar.addMenu(self._language_loader.get_value("ABOUT_MENU", "About"))

        author_action = QAction(
            self._language_loader.get_value("ABOUT_AUTHOR", "Author"), self._frame
        )
        author_action.triggered.connect(self._on_about_author)
        about_menu.addAction(author_action)

        contributors_action = QAction(
            self._language_loader.get_value("ABOUT_CONTRIBUTORS", "Contributors"), self._frame
        )
        contributors_action.triggered.connect(self._on_about_contributors)
        about_menu.addAction(contributors_action)

        software_action = QAction(
            self._language_loader.get_value("ABOUT_SOFTWARE", "This Software"), self._frame
        )
        software_action.triggered.connect(self._on_about_software)
        about_menu.addAction(software_action)

    def _on_file_import(self):
        """Handle File > Import menu action."""
        self._logger.debug("File > Import (not implemented)")

    def _on_file_export(self):
        """Handle File > Export menu action."""
        self._logger.debug("File > Export (not implemented)")

    def _on_file_quit(self):
        """Handle File > Quit menu action."""
        if self._controller:
            self._controller.quit()
        if self._frame:
            self._frame.close()

    def _on_edit_copy(self):
        """Handle Edit > Copy menu action."""
        if self._controller:
            self._controller.copy_from_display_value()

    def _on_edit_paste(self):
        """Handle Edit > Paste menu action."""
        if self._controller:
            self._controller.paste_to_display_value()

    def _on_edit_erase_display(self):
        """Handle Edit > Erase > Display menu action."""
        if self._controller:
            self._controller.erase_display()

    def _on_edit_erase_stack(self):
        """Handle Edit > Erase > Stack Registers menu action."""
        if self._controller:
            self._controller.erase_stack()

    def _on_edit_erase_finance(self):
        """Handle Edit > Erase > Finance Registers menu action."""
        if self._controller:
            self._controller.erase_finance()

    def _on_edit_erase_statistic(self):
        """Handle Edit > Erase > Statistic Registers menu action."""
        if self._controller:
            self._controller.erase_statistic()

    def _on_edit_erase_all(self):
        """Handle Edit > Erase > All Registers menu action."""
        if self._controller:
            self._controller.erase_all_registers()

    def _on_edit_erase_program(self):
        """Handle Edit > Erase > Program Steps menu action."""
        if self._controller:
            self._controller.erase_program()

    def _on_view_size(self):
        """Handle View > Size menu action."""
        action = self.sender()
        if action and isinstance(action, QAction):
            size = float(action.data())
            if self._cfg:
                self._cfg.set_size(size)
            self.set_size(size)
            # Reload fonts with new size
            self.load_font()
            # Rebuild image maps with new size
            self.build_image_maps()
            # Update background image
            if self._bg_image and self._main_panel:
                self._main_panel.set_image_obj(self._bg_image)
            # Rebuild buttons with new images
            # Clear existing buttons
            for btn in self._buttons.values():
                btn.deleteLater()
            self._buttons.clear()
            # Rebuild buttons
            self._build_buttons()
            # Update display fonts
            if self._main_panel:
                if self._qt_font:
                    self._main_panel.set_display_font(self._qt_font)
                if self._flag_font:
                    self._main_panel.set_flag_font(self._flag_font)
                if self._display_face_color:
                    display_color = QColor(self._display_face_color)
                    self._main_panel.set_display_color(display_color)
            # Update display
            self.update_display()
            # Update window geometry
            self.setFixedSize(self._wmainpan, self._hmainpan)

    def _on_view_skin(self):
        """Handle View > Skin menu action."""
        action = self.sender()
        if action and isinstance(action, QAction):
            skin_id = action.data()
            if self._cfg:
                self._cfg.set_skin(skin_id)
            # Reload skin and rebuild UI
            self.find_paths()
            self.load_skin()
            self.load_font()
            # Rebuild image maps with new skin
            self.build_image_maps()
            # Update background image
            if self._bg_image and self._main_panel:
                self._main_panel.set_image_obj(self._bg_image)
            # Rebuild buttons with new images
            # Clear existing buttons
            for btn in self._buttons.values():
                btn.deleteLater()
            self._buttons.clear()
            # Rebuild buttons
            self._build_buttons()
            # Update display fonts
            if self._main_panel:
                if self._qt_font:
                    self._main_panel.set_display_font(self._qt_font)
                if self._flag_font:
                    self._main_panel.set_flag_font(self._flag_font)
                if self._display_face_color:
                    display_color = QColor(self._display_face_color)
                    self._main_panel.set_display_color(display_color)
            # Update display
            self.update_display()

    def _on_options_number_format(self):
        """Handle Options > Number format menu action."""
        action = self.sender()
        if action and isinstance(action, QAction) and self._cfg and self._controller:
            com = 0 if action.data() == "dot" else 1
            self._cfg.set_com(com)
            executor = self._controller.get_executor()
            if executor:
                executor.get_display().set_comma(com == 1)
                executor.update_display()
                self.update_display()

    def _on_options_date_format(self):
        """Handle Options > Date format menu action."""
        action = self.sender()
        if action and isinstance(action, QAction) and self._cfg and self._controller:
            dmy = 0 if action.data() == "mdy" else 1
            self._cfg.set_dmy(dmy)
            executor = self._controller.get_executor()
            if executor:
                executor.get_flags().set_dmy(dmy)
                executor.update_display()
                self.update_display()

    def _on_options_payment_mode(self):
        """Handle Options > Payment mode menu action."""
        action = self.sender()
        if action and isinstance(action, QAction) and self._cfg and self._controller:
            beg = 0 if action.data() == "end" else 1
            self._cfg.set_beg(beg)
            executor = self._controller.get_executor()
            if executor:
                executor.get_flags().set_begin(beg)
                executor.update_display()
                self.update_display()

    def _update_register_view(self):
        """Update register view window if it's open."""
        if self._register_view_window is not None and self._register_view_window.isVisible():
            self._register_view_window.update()

    def _on_tools_registers_view(self):
        """Handle Tools > Registers view menu action."""
        from hp12c.ui.register_view_pyqt5 import RegisterViewWindow

        executor = self._controller.get_executor() if self._controller else None
        if self._register_view_window is None:
            self._register_view_window = RegisterViewWindow(self._frame, executor, main_window=self)
        if self._register_view_window.isVisible():
            self._register_view_window.raise_()
            self._register_view_window.activateWindow()
        else:
            self._register_view_window.show()
        self._register_view_window.update()

    def _on_tools_history(self):
        """Handle Tools > Instructions history menu action."""
        self._logger.debug("Tools > Instructions history (not implemented)")

    def _on_about_author(self):
        """Handle About > Author menu action."""
        self._logger.debug("About > Author (not implemented)")

    def _on_about_contributors(self):
        """Handle About > Contributors menu action."""
        self._logger.debug("About > Contributors (not implemented)")

    def _on_about_software(self):
        """Handle About > This Software menu action."""
        QMessageBox.information(
            self._frame,
            "About HP12C Calculator",
            f"HP12C Calculator - Python Port\nVersion: {Configuration.VERSION}\n\n"
            "This program is free software: you can redistribute it and/or modify\n"
            "it under the terms of the GNU General Public License as published by\n"
            "the Free Software Foundation, either version 3 of the License, or\n"
            "(at your option) any later version.",
        )

    def fix_window_location(self):
        """Fix window location if out of bounds."""
        # This would be called after window is created
        pass

    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        clipboard = QApplication.clipboard()
        if clipboard:
            clipboard.setText(text)

    def get_from_clipboard(self) -> str:
        """Get text from clipboard."""
        clipboard = QApplication.clipboard()
        if clipboard:
            return clipboard.text()
        return ""
