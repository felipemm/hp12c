"""
PyQt5 implementation of main window for HP12C calculator.
Ported from Java MainWindow.java using PyQt5 for better font rendering.
"""

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtGui import QPainter, QFont, QFontDatabase, QColor, QPixmap, QIcon
from PyQt5.QtCore import Qt, QRect, pyqtSignal, QTimer
from pathlib import Path
from typing import Dict, Optional, Tuple
from PIL import Image, ImageFont
import xml.etree.ElementTree as ET
import io

from hp12c_python_java_port.calculator.key import Key
from hp12c_python_java_port.calculator.config import Configuration
from hp12c_python_java_port.ui.base_main_window import BaseMainWindow
from hp12c_python_java_port.ui.pyqt5_image_panel import PyQt5ImagePanel
from hp12c_python_java_port.ui.pyqt5_image_button import PyQt5ImageButton


class DisplayWidget(PyQt5ImagePanel):
    """Widget that displays calculator text over the background image."""

    def __init__(self, parent=None):
        """Initialize display widget."""
        super().__init__(parent)
        # Ensure widget can have child widgets and allows absolute positioning
        self.setAttribute(Qt.WA_StaticContents, False)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)
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
        self.update()

    def set_flag_text(self, text: str):
        """Set flag display text."""
        self._flag_text = text
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
            rect = QRect(self._display_x - self._display_width, self._display_y - self._display_font.pointSize() // 2,
                        self._display_width, self._display_font.pointSize() * 2)
            painter.drawText(rect, Qt.AlignRight | Qt.AlignVCenter, self._display_text)

        # Draw flag display text
        if self._flag_font and self._flag_text:
            painter.setFont(self._flag_font)
            painter.setPen(self._display_color)
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
            rect = QRect(self._flag_x - rect_width,
                        self._flag_y - self._flag_font.pointSize() // 2,
                        rect_width,
                        self._flag_font.pointSize() * 2)
            # Use elided text if it's too long to fit
            if text_width > rect_width - padding:
                elided_text = painter.fontMetrics().elidedText(
                    self._flag_text, Qt.ElideRight, rect_width - padding
                )
                painter.drawText(rect, Qt.AlignRight | Qt.AlignVCenter, elided_text)
            else:
                painter.drawText(rect, Qt.AlignRight | Qt.AlignVCenter, self._flag_text)
        elif self._flag_text:
            # Debug: flag text exists but font is missing
            print(f"Warning: Flag text exists ('{self._flag_text}') but flag font is not set")
        elif self._flag_font:
            # Debug: flag font exists but text is missing
            print(f"Warning: Flag font is set but flag text is empty (flag_x={self._flag_x}, flag_y={self._flag_y})")


class PyQt5MainWindow(BaseMainWindow):
    """PyQt5 implementation of main calculator window."""

    def __init__(self, controller):
        """Initialize main window."""
        super().__init__(controller)
        self._controller = controller
        self._frame = None  # QMainWindow
        self._main_panel = None  # DisplayWidget
        self._display_widget = None  # DisplayWidget for text rendering
        self._base_path = Path("resources")
        self._skin_path = None
        self._skin_font_path = None
        self._buttons: Dict[str, PyQt5ImageButton] = {}
        self._image_map: Dict[str, Image.Image] = {}
        self._image_map_pressed: Dict[str, Image.Image] = {}
        self._bg_image = None
        self._font = None  # PIL ImageFont
        self._qt_font = None  # QFont
        self._flag_font = None  # QFont for flags
        self._cfg = None
        self._skin = None

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
        self.build()

    def build(self):
        """Build the window."""
        # Paths already found in init(), just build image maps
        self.build_image_maps()

        window_title = f"HP12C Calculator - v{Configuration.VERSION}"
        self._frame = QMainWindow()
        self._frame.setWindowTitle(window_title)
        self._frame.setFixedSize(self._wmainpan, self._hmainpan)

        # Set icon if available
        self.set_icon()

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

        skin_name = self._cfg.get_skin() if self._cfg.get_skin() else Configuration.DEFAULT_SKIN
        self._skin_path = self._base_path / "skins" / skin_name
        self._skin_font_path = self._skin_path / "font.ttf"

        print(f"Base path: {self._base_path}")
        print(f"Skin path: {self._skin_path}")
        print(f"Skin path exists: {self._skin_path.exists()}")

    def load_skin(self):
        """Load skin configuration."""
        skin_name = self._cfg.get_skin() if self._cfg.get_skin() else Configuration.DEFAULT_SKIN
        skin_file = self._base_path / "skins" / skin_name / "skn.xml"

        print(f"Loading skin from: {skin_file}")
        print(f"Skin file exists: {skin_file.exists()}")

        if skin_file.exists():
            try:
                tree = ET.parse(skin_file)
                root = tree.getroot()
                self._skin = {}
                for child in root:
                    self._skin[child.tag] = child.text
                print(f"Successfully loaded skin XML with {len(self._skin)} properties")
            except Exception as e:
                print(f"Error loading skin: {e}")
                self._skin = {}
        else:
            print(f"Skin file not found at: {skin_file}")
            self._skin = {}

        # Set default colors if not in skin
        # XML uses hyphenated tag names (e.g., "display-face-color"), not camelCase
        self._face_color = self._hex_to_color(self._skin.get('face-color', self._skin.get('bgColor', '#000000')))
        self._display_bg_color = self._hex_to_color(self._skin.get('display-bg-color', self._skin.get('displayBgColor', '#000000')))
        self._display_face_color = self._hex_to_color(self._skin.get('display-face-color', self._skin.get('displayFaceColor', '#00FF00')))
        self._button_bg_color = self._hex_to_color(self._skin.get('button-bg-color', self._skin.get('buttonBgColor', '#000000')))
        self._button_face_color = self._hex_to_color(self._skin.get('button-face-color', self._skin.get('buttonFaceColor', '#FFFFFF')))

        # Debug: print loaded colors
        print(f"Loaded skin colors:")
        print(f"  display-face-color: {self._skin.get('display-face-color', 'NOT FOUND')}")
        print(f"  display_face_color: {self._display_face_color}")

    def _hex_to_color(self, hex_str: str) -> str:
        """Convert hex color string to QColor-compatible format."""
        if hex_str.startswith('#'):
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

    def create_image_icon(self, w: int, h: int, path: str) -> Optional[Image.Image]:
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
                full_path = Path("hp12c_python_java_port") / "resources" / path
            if not full_path.exists():
                # Try as resource path relative to current directory
                full_path = Path("resources") / path

            if full_path.exists():
                img = Image.open(full_path)
                return img.resize((w, h), Image.Resampling.LANCZOS)
            else:
                # Only print if it's a critical image (background or button)
                if "background" in path or "buttons" in path:
                    print(f"Image not found: {path} (tried: {full_path})")
        except Exception as e:
            print(f"Error loading image {path}: {e}")
        return None

    def build_image_maps(self):
        """Build image maps for buttons."""
        # Construct relative path from base_path
        skin_name = self._skin_path.name if self._skin_path else Configuration.DEFAULT_SKIN
        skin_path_str = f"skins/{skin_name}/"

        # Background image
        bg_img = self.create_image_icon(self._wmainpan, self._hmainpan, f"{skin_path_str}background.png")
        if bg_img:
            self._bg_image = bg_img
            print(f"Background image loaded: {skin_path_str}background.png")
        else:
            print(f"Failed to load background image: {skin_path_str}background.png")

        # Button images - normal and pressed
        button_codes = [
            (0, Key.KEY_0), (1, Key.KEY_1), (2, Key.KEY_2), (3, Key.KEY_3),
            (4, Key.KEY_4), (5, Key.KEY_5), (6, Key.KEY_6), (7, Key.KEY_7),
            (8, Key.KEY_8), (9, Key.KEY_9), (10, Key.KEY_DIV), (11, Key.KEY_N),
            (12, Key.KEY_I), (13, Key.KEY_PV), (14, Key.KEY_PMT), (15, Key.KEY_FV),
            (16, Key.KEY_CHS), (20, Key.KEY_MUL), (21, Key.KEY_POW), (22, Key.KEY_RECIPROCAL),
            (23, Key.KEY_PERC_TOT), (24, Key.KEY_PERC_DELTA), (25, Key.KEY_PERC), (26, Key.KEY_EEX),
            (30, Key.KEY_SUB), (31, Key.KEY_RS), (32, Key.KEY_SST), (33, Key.KEY_ROLL),
            (34, Key.KEY_XY), (35, Key.KEY_CLX), (36, Key.KEY_ENTER), (40, Key.KEY_SUM),
            (41, Key.KEY_ON), (42, Key.KEY_F), (43, Key.KEY_G), (44, Key.KEY_STO),
            (45, Key.KEY_RCL), (48, Key.KEY_DOT), (49, Key.KEY_TOT)
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
                print(f"Failed to load button image: {img_path}")

            # Pressed button
            img_pressed_path = f"{skin_path_str}buttons/b{code:02d}p.png"
            img_pressed = self.create_image_icon(btn_size[0], btn_size[1], img_pressed_path)
            if img_pressed:
                self._image_map_pressed[key.name] = img_pressed

        print(f"Loaded {loaded_count}/{len(button_codes)} button images")

    def load_font(self):
        """Load font from skin using PyQt5."""
        try:
            if self._skin_font_path.exists():
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
                        print(f"Loaded skin font: {font_family} (size: {self._font_size})")
                    else:
                        print(f"Could not get font family from loaded font, using Courier")
                        self._qt_font = QFont("Courier", self._font_size)
                else:
                    print(f"Could not load font from file, using Courier")
                    self._qt_font = QFont("Courier", self._font_size)

                # Create flag font (smaller, but ensure minimum readable size)
                flag_font_size = max(7, int(self._font_size / 4.0))  # Reduced from /3.0 to /4.0 for smaller size
                if flag_font_size < 7:
                    flag_font_size = 7
                if self._qt_font:
                    self._flag_font = QFont(self._qt_font.family(), flag_font_size)
                    self._flag_font.setHintingPreference(QFont.PreferFullHinting)
                    print(f"Created flag font: {self._qt_font.family()}, size: {flag_font_size}")
                else:
                    self._flag_font = QFont("Courier", flag_font_size)
                    print(f"Created flag font: Courier, size: {flag_font_size}")
            else:
                # Font file not found, use default
                print(f"Font file not found: {self._skin_font_path}, using Courier")
                self._font = ('Courier', self._font_size)
                self._qt_font = QFont("Courier", self._font_size)
                flag_font_size = max(7, int(self._font_size / 4.0))  # Reduced from /3.0 to /4.0 for smaller size
                if flag_font_size < 7:
                    flag_font_size = 7
                self._flag_font = QFont("Courier", flag_font_size)
                print(f"Created flag font (fallback): Courier, size: {flag_font_size}")
        except Exception as e:
            print(f"Error loading font: {e}")
            import traceback
            traceback.print_exc()
            self._font = ('Courier', self._font_size)
            self._qt_font = QFont("Courier", self._font_size)
            flag_font_size = max(7, int(self._font_size / 4.0))  # Reduced from /3.0 to /4.0 for smaller size
            if flag_font_size < 7:
                flag_font_size = 7
            self._flag_font = QFont("Courier", flag_font_size)
            print(f"Created flag font (error fallback): Courier, size: {flag_font_size}")

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
        self._main_panel.setContentsMargins(0, 0, 0, 0)
        # Explicitly disable auto-fill background which might interfere
        self._main_panel.setAutoFillBackground(False)
        # QMainWindow's central widget area might have margins - set them to 0
        self._frame.setCentralWidget(self._main_panel)
        # Ensure the central widget area has no margins
        central_widget = self._frame.centralWidget()
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
        print(f"Display color: {self._display_face_color}")
        print(f"LCD position on image: x={self._lcd_x}, y={self._lcd_y}")
        print(f"Display text position: x={display_x}, y={display_y}")
        print(f"Flag text position: x={flag_x}, y={flag_y}")
        print(f"Flag font: {self._flag_font.family() if self._flag_font else 'None'}, size: {self._flag_font.pointSize() if self._flag_font else 'None'}")
        print(f"Flag width: {self._wfdis}, Flag height: {self._hfdis}")
        print(f"Flag display width: {self._main_panel._flag_width if hasattr(self._main_panel, '_flag_width') else 'N/A'}")

        # Build buttons with exact layout from Java
        self._build_buttons()

    def _build_buttons(self):
        """Build buttons matching Java layout exactly."""
        # Button layout: (gridx, gridy, key, rowspan)
        button_layout = [
            # Row 1 (gridy=1)
            (0, 1, Key.KEY_N, 1), (1, 1, Key.KEY_I, 1), (2, 1, Key.KEY_PV, 1),
            (3, 1, Key.KEY_PMT, 1), (4, 1, Key.KEY_FV, 1), (5, 1, Key.KEY_CHS, 1),
            (6, 1, Key.KEY_7, 1), (7, 1, Key.KEY_8, 1), (8, 1, Key.KEY_9, 1),
            (9, 1, Key.KEY_DIV, 1),
            # Row 2 (gridy=2)
            (0, 2, Key.KEY_POW, 1), (1, 2, Key.KEY_RECIPROCAL, 1), (2, 2, Key.KEY_PERC_TOT, 1),
            (3, 2, Key.KEY_PERC_DELTA, 1), (4, 2, Key.KEY_PERC, 1), (5, 2, Key.KEY_EEX, 1),
            (6, 2, Key.KEY_4, 1), (7, 2, Key.KEY_5, 1), (8, 2, Key.KEY_6, 1),
            (9, 2, Key.KEY_MUL, 1),
            # Row 3 (gridy=3)
            (0, 3, Key.KEY_RS, 1), (1, 3, Key.KEY_SST, 1), (2, 3, Key.KEY_ROLL, 1),
            (3, 3, Key.KEY_XY, 1), (4, 3, Key.KEY_CLX, 1), (5, 3, Key.KEY_ENTER, 2),  # ENTER spans 2 rows
            (6, 3, Key.KEY_1, 1), (7, 3, Key.KEY_2, 1), (8, 3, Key.KEY_3, 1),
            (9, 3, Key.KEY_SUB, 1),
            # Row 4 (gridy=4)
            (0, 4, Key.KEY_ON, 1), (1, 4, Key.KEY_F, 1), (2, 4, Key.KEY_G, 1),
            (3, 4, Key.KEY_STO, 1), (4, 4, Key.KEY_RCL, 1),
            # ENTER button continues from row 3 (no button at 5,4)
            (6, 4, Key.KEY_0, 1), (7, 4, Key.KEY_DOT, 1), (8, 4, Key.KEY_TOT, 1),
            (9, 4, Key.KEY_SUM, 1),
        ]

        for gridx, gridy, key, rowspan in button_layout:
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
                btn.setStyleSheet(f"background-color: {self._button_bg_color}; color: {self._button_face_color};")

            # Explicitly set parent to ensure proper parent-child relationship
            btn.setParent(self._main_panel)
            # Ensure button allows absolute positioning
            btn.setAutoFillBackground(False)

            # Calculate position (same as Tkinter/Java)
            x = gridx * (self._wbot + 2 * self._xpad) + self._xpad + int((35 * self._size))
            y = self._hdispan + gridy * (self._hbot + 2 * self._ypad) + self._ypad

            # Debug: print first few button positions to verify calculation
            if len(self._buttons) < 3:
                print(f"Button {key_name}: gridx={gridx}, gridy={gridy}, x={x}, y={y}, size=({btn_width}, {btn_height})")
                print(f"  hdispan={self._hdispan}, hbot={self._hbot}, ypad={self._ypad}")
                print(f"  Parent widget size: {self._main_panel.width()}x{self._main_panel.height()}")
                print(f"  Parent widget pos: {self._main_panel.pos()}")

            # Position button - ensure it's visible first, then position
            btn.show()  # Make button visible first
            # Position button using setGeometry (position + size) for reliability
            # This ensures the button is positioned correctly relative to parent's (0,0)
            btn.setGeometry(x, y, btn_width, btn_height)
            # Verify the geometry was set correctly
            if len(self._buttons) < 3:
                actual_geom = btn.geometry()
                actual_pos = btn.pos()
                print(f"  Button actual geometry: x={actual_geom.x()}, y={actual_geom.y()}, w={actual_geom.width()}, h={actual_geom.height()}")
                print(f"  Button actual pos: x={actual_pos.x()}, y={actual_pos.y()}")
                print(f"  Parent widget rect: {self._main_panel.rect()}")
            btn.raise_()  # Bring button to front
            btn.update()  # Force repaint
            # Force the parent to update as well
            self._main_panel.update()

            # Connect click handler
            btn.clicked_with_key.connect(lambda k=key: self._on_button_click(k))

            # Store button
            self._buttons[key_name] = btn

    def _get_button_text(self, key: Key) -> str:
        """Get text label for button (fallback when image not available)."""
        text_map = {
            Key.KEY_0: '0', Key.KEY_1: '1', Key.KEY_2: '2', Key.KEY_3: '3',
            Key.KEY_4: '4', Key.KEY_5: '5', Key.KEY_6: '6', Key.KEY_7: '7',
            Key.KEY_8: '8', Key.KEY_9: '9', Key.KEY_DIV: '/', Key.KEY_MUL: '*',
            Key.KEY_SUB: '-', Key.KEY_SUM: '+', Key.KEY_N: 'N', Key.KEY_I: 'I',
            Key.KEY_PV: 'PV', Key.KEY_PMT: 'PMT', Key.KEY_FV: 'FV', Key.KEY_CHS: 'CHS',
            Key.KEY_POW: 'y^x', Key.KEY_RECIPROCAL: '1/x', Key.KEY_PERC_TOT: '%T',
            Key.KEY_PERC_DELTA: 'Δ%', Key.KEY_PERC: '%', Key.KEY_EEX: 'EEX',
            Key.KEY_RS: 'R/S', Key.KEY_SST: 'SST', Key.KEY_ROLL: 'R↓',
            Key.KEY_XY: 'x↔y', Key.KEY_CLX: 'CLX', Key.KEY_ENTER: 'ENTER',
            Key.KEY_ON: 'ON', Key.KEY_F: 'f', Key.KEY_G: 'g',
            Key.KEY_STO: 'STO', Key.KEY_RCL: 'RCL', Key.KEY_DOT: '.', Key.KEY_TOT: 'Σ+'
        }
        return text_map.get(key, key.name.replace('KEY_', ''))

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
                print(f"Flag display string: '{flag_str}' (length: {len(flag_str) if flag_str else 0})")  # Debug output
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
        for key_name, btn in self._buttons.items():
            # Get the stored position from button's current geometry
            geom = btn.geometry()
            # Force reposition to ensure it's correct
            btn.setGeometry(geom.x(), geom.y(), geom.width(), geom.height())
            btn.update()

    def hide(self):
        """Hide window."""
        if self._frame:
            self._frame.hide()

    def get_window_location(self) -> Tuple[int, int]:
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
        if key and key.name in self._buttons:
            btn = self._buttons[key.name]
            key_name = key.name
            if key_name in self._image_map:
                normal_img = self._image_map[key_name]
                btn.set_image_obj(normal_img)
            self.update_display()

    def get_frame(self):
        """Get QMainWindow."""
        return self._frame

    def set_icon(self):
        """Set window icon."""
        try:
            icon_path = self._skin_path / "icon.png"
            if icon_path.exists():
                icon_pixmap = QPixmap(str(icon_path))
                if not icon_pixmap.isNull():
                    icon = QIcon(icon_pixmap)
                    self._frame.setWindowIcon(icon)
        except Exception as e:
            print(f"Error setting icon: {e}")

    def fix_window_location(self):
        """Fix window location if out of bounds."""
        # This would be called after window is created
        pass
