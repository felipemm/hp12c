"""
Tkinter implementation of main window for HP12C calculator.
Ported from Java MainWindow.java using Tkinter.
"""

import contextlib
import platform
import tkinter as tk
import tkinter.font as tkfont
import xml.etree.ElementTree as ET
from collections.abc import Callable
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageTk

from hp12c.calculator.config import Configuration
from hp12c.calculator.key import Key
from hp12c.ui.base_main_window import BaseMainWindow
from hp12c.ui.image_button import ImageButton
from hp12c.ui.image_panel import ImagePanel
from hp12c.utils.language_loader import LanguageLoader
from hp12c.utils.logger import get_logger
from hp12c.utils.skin_loader import SkinLoader


class TkinterMainWindow(BaseMainWindow):
    """Tkinter implementation of main calculator window."""

    def __init__(self, controller):
        """Initialize main window."""
        self._logger = get_logger(__name__)
        self._controller = controller
        self._frame = None
        self._main_panel = None
        self._display_panel = None
        self._display = None
        self._flag_display = None
        self._base_path = Path("resources")
        self._skin_path = None
        self._skin_font_path = None
        self._buttons: dict[str, ImageButton | tk.Button] = {}
        self._image_map: dict[str, Image.Image] = {}
        self._image_map_pressed: dict[str, Image.Image] = {}
        self._bg_image = None
        self._font = None  # PIL ImageFont (for image rendering if needed)
        self._flag_pil_font = None  # PIL ImageFont for flags
        self._tk_font = None  # Tkinter font (for Canvas text items - kept for compatibility)
        self._flag_font = None  # Tkinter font for flags (kept for compatibility)
        self._cfg = None
        self._skin = None
        self._size = 1.0  # Size multiplier
        self._display_text = ""  # Current display text
        self._flag_text = ""  # Current flag text
        self._composite_image = None  # Background image with text rendered
        self._language_loader = None  # Language string loader
        self._skin_loader = None  # Skin list loader
        self._menu_bar = None  # Menu bar
        self._register_view_window = None  # Register view window
        self._history_view_window = None  # History view window

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
        # Paths already found in init(), just build image maps
        self.build_image_maps()

        window_title = f"HP12C Calculator - v{Configuration.VERSION}"
        self._frame = tk.Tk()
        self._frame.title(window_title)
        self._frame.resizable(False, False)
        self._frame.config(bg="#000000")

        # Set window size to match panel size
        self._frame.geometry(f"{self._wmainpan}x{self._hmainpan}")

        # Set icon if available
        self.set_icon()

        # Set up event handlers
        self._frame.protocol("WM_DELETE_WINDOW", self._on_closing)

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

        # Debug: log loaded colors
        self._logger.debug("Loaded skin colors:")
        self._logger.debug(
            f"  display-face-color: {self._skin.get('display-face-color', 'NOT FOUND')}"
        )
        self._logger.debug(f"  display_face_color: {self._display_face_color}")

    def _hex_to_color(self, hex_str: str) -> str:
        """Convert hex color string to tkinter color."""
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
        self._hfdis = -10
        self._wfdis = 300
        self._font_size = 29
        # Display padding (insets) for positioning
        self._tdis = 0
        self._ldis = 0
        self._bdis = 0
        self._rdis = 100
        self._tfdis = 0
        self._lfdis = 0
        self._bfdis = 0
        self._rfdis = 100
        # LCD position on background image
        self._lcd_x = 200
        self._lcd_y = 35

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
            # Re-render display with new fonts
            self._render_display()

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
        """Load font from skin."""
        try:
            if self._skin_font_path and self._skin_font_path.exists():
                # Load PIL font for image rendering (if needed)
                self._font = ImageFont.truetype(str(self._skin_font_path), self._font_size)

                # Load Tkinter font for Canvas text items
                # First, try to extract font family name from the TTF file
                font_family = self._get_font_family_from_file(self._skin_font_path)

                if font_family:
                    try:
                        # Try to create font with the family name
                        # Note: The font must be installed/available to Tkinter
                        self._tk_font = tkfont.Font(family=font_family, size=self._font_size)
                        # Verify the font was actually loaded by checking if it's different from default
                        actual_family = self._tk_font.cget("family")
                        if (
                            actual_family.lower() == font_family.lower()
                            or actual_family != "Courier"
                        ):
                            self._logger.debug(
                                f"Loaded skin font by family name: {font_family} (actual: {actual_family})"
                            )
                        else:
                            self._logger.warning(
                                f"Font family '{font_family}' not found, using '{actual_family}'"
                            )
                            # Font family not available, fallback to Courier
                            # Note: Tkinter Font doesn't support file parameter
                            self._logger.warning(
                                f"Font family '{font_family}' not available, using Courier"
                            )
                            self._tk_font = tkfont.Font(family="Courier", size=self._font_size)
                    except Exception as e2:
                        self._logger.warning(f"Could not load font family '{font_family}': {e2}")
                        # Fallback to Courier
                        self._logger.debug("Using Courier as fallback font")
                        self._tk_font = tkfont.Font(family="Courier", size=self._font_size)
                else:
                    # Could not extract family name, use Courier
                    self._logger.debug("Could not extract font family name, using Courier")
                    self._tk_font = tkfont.Font(family="Courier", size=self._font_size)

                # Create flag font - matches Java code: new Font("monospaced", 0, this.fontSize / 3)
                flag_font_size = int(self._font_size / 3)
                # Create PIL font for flag display - use monospace font (matches Java's "monospaced")
                try:
                    # Try to load monospace font from system (equivalent to Java's "monospaced" logical font)
                    system = platform.system()
                    monospace_paths = []
                    if system == "Darwin":  # macOS
                        monospace_paths = [
                            "/System/Library/Fonts/Supplemental/Courier New.ttf",
                            "/System/Library/Fonts/Courier.dfont",
                            "/Library/Fonts/Courier New.ttf",
                            "/System/Library/Fonts/Monaco.dfont",
                        ]
                    elif system == "Windows":
                        monospace_paths = [
                            "C:/Windows/Fonts/cour.ttf",
                            "C:/Windows/Fonts/courbd.ttf",
                            "C:/Windows/Fonts/consola.ttf",  # Consolas (Windows monospace)
                        ]
                    else:  # Linux
                        monospace_paths = [
                            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
                            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                            "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
                        ]

                    flag_font_loaded = False
                    for path in monospace_paths:
                        try:
                            if Path(path).exists():
                                self._flag_pil_font = ImageFont.truetype(path, flag_font_size)
                                self._logger.debug(
                                    f"Created PIL flag font (monospace): {path}, size: {flag_font_size}"
                                )
                                flag_font_loaded = True
                                break
                        except OSError:
                            continue

                    if not flag_font_loaded:
                        # Fallback: try to load by name (may work on some systems)
                        for font_name in [
                            "Courier",
                            "Courier New",
                            "Monaco",
                            "Consolas",
                            "Liberation Mono",
                        ]:
                            try:
                                self._flag_pil_font = ImageFont.truetype(font_name, flag_font_size)
                                self._logger.debug(
                                    f"Created PIL flag font (monospace by name): {font_name}, size: {flag_font_size}"
                                )
                                flag_font_loaded = True
                                break
                            except OSError:
                                continue

                    if not flag_font_loaded:
                        # Final fallback: use default monospace font
                        self._flag_pil_font = ImageFont.load_default()
                        self._logger.debug(
                            f"Created PIL flag font (fallback to default monospace), size: {flag_font_size}"
                        )
                except Exception as e:
                    self._flag_pil_font = ImageFont.load_default()
                    self._logger.warning(
                        f"Created PIL flag font (error fallback): default monospace font, size: {flag_font_size}, error: {e}"
                    )

                # Also create Tkinter font for compatibility (use monospace font - matches Java's "monospaced")
                # Try common monospace font names
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
                    try:
                        self._flag_font = tkfont.Font(family=family, size=flag_font_size)
                        # Verify it's actually monospace by checking if it exists
                        if family in tkfont.families():
                            self._logger.debug(
                                f"Created flag font (monospace): {family}, size: {flag_font_size}"
                            )
                            flag_font_created = True
                            break
                    except (tk.TclError, ValueError):
                        continue

                if not flag_font_created:
                    # Fallback to Courier (most common monospace font)
                    self._flag_font = tkfont.Font(family="Courier", size=flag_font_size)
                    self._logger.debug(
                        f"Created flag font (monospace fallback): Courier, size: {flag_font_size}"
                    )
            else:
                # Font file not found, use default
                self._logger.warning(f"Font file not found: {self._skin_font_path}, using Courier")
                self._font = ("Courier", self._font_size)
                self._tk_font = tkfont.Font(family="Courier", size=self._font_size)
                # Create flag font - matches Java code: new Font("monospaced", 0, this.fontSize / 3)
                flag_font_size = int(self._font_size / 3)
                # Create PIL font for flag display - use monospace font (matches Java's "monospaced")
                try:
                    # Try to load monospace font from system (equivalent to Java's "monospaced" logical font)
                    system = platform.system()
                    monospace_paths = []
                    if system == "Darwin":  # macOS
                        monospace_paths = [
                            "/System/Library/Fonts/Supplemental/Courier New.ttf",
                            "/System/Library/Fonts/Courier.dfont",
                            "/Library/Fonts/Courier New.ttf",
                            "/System/Library/Fonts/Monaco.dfont",
                        ]
                    elif system == "Windows":
                        monospace_paths = [
                            "C:/Windows/Fonts/cour.ttf",
                            "C:/Windows/Fonts/courbd.ttf",
                            "C:/Windows/Fonts/consola.ttf",  # Consolas (Windows monospace)
                        ]
                    else:  # Linux
                        monospace_paths = [
                            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
                            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                            "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
                        ]

                    flag_font_loaded = False
                    for path in monospace_paths:
                        try:
                            if Path(path).exists():
                                self._flag_pil_font = ImageFont.truetype(path, flag_font_size)
                                self._logger.debug(
                                    f"Created PIL flag font (monospace): {path}, size: {flag_font_size}"
                                )
                                flag_font_loaded = True
                                break
                        except OSError:
                            continue

                    if not flag_font_loaded:
                        # Fallback: try to load by name (may work on some systems)
                        for font_name in [
                            "Courier",
                            "Courier New",
                            "Monaco",
                            "Consolas",
                            "Liberation Mono",
                        ]:
                            try:
                                self._flag_pil_font = ImageFont.truetype(font_name, flag_font_size)
                                self._logger.debug(
                                    f"Created PIL flag font (monospace by name): {font_name}, size: {flag_font_size}"
                                )
                                flag_font_loaded = True
                                break
                            except OSError:
                                continue

                    if not flag_font_loaded:
                        # Final fallback: use default monospace font
                        self._flag_pil_font = ImageFont.load_default()
                        self._logger.debug(
                            f"Created PIL flag font (fallback to default monospace), size: {flag_font_size}"
                        )
                except Exception as e:
                    self._flag_pil_font = ImageFont.load_default()
                    self._logger.warning(
                        f"Created PIL flag font (error fallback): default monospace font, size: {flag_font_size}, error: {e}"
                    )

                # Also create Tkinter font for compatibility (use monospace font - matches Java's "monospaced")
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
                    try:
                        self._flag_font = tkfont.Font(family=family, size=flag_font_size)
                        if family in tkfont.families():
                            self._logger.debug(
                                f"Created flag font (monospace fallback): {family}, size: {flag_font_size}"
                            )
                            flag_font_created = True
                            break
                    except (tk.TclError, ValueError):
                        continue

                if not flag_font_created:
                    self._flag_font = tkfont.Font(family="Courier", size=flag_font_size)
                    self._logger.debug(
                        f"Created flag font (monospace fallback): Courier, size: {flag_font_size}"
                    )
        except Exception as e:
            self._logger.error(f"Error loading font: {e}")
            import traceback

            traceback.print_exc()
            self._font = ("Courier", self._font_size)
            self._tk_font = tkfont.Font(family="Courier", size=self._font_size)
            # Create flag font - matches Java code: new Font("monospaced", 0, this.fontSize / 3)
            flag_font_size = int(self._font_size / 3)
            # Create PIL font for flag display - use monospace font (matches Java's "monospaced")
            try:
                # Try to load monospace font from system (equivalent to Java's "monospaced" logical font)
                system = platform.system()
                monospace_paths = []
                if system == "Darwin":  # macOS
                    monospace_paths = [
                        "/System/Library/Fonts/Supplemental/Courier New.ttf",
                        "/System/Library/Fonts/Courier.dfont",
                        "/Library/Fonts/Courier New.ttf",
                        "/System/Library/Fonts/Monaco.dfont",
                    ]
                elif system == "Windows":
                    monospace_paths = [
                        "C:/Windows/Fonts/cour.ttf",
                        "C:/Windows/Fonts/courbd.ttf",
                        "C:/Windows/Fonts/consola.ttf",  # Consolas (Windows monospace)
                    ]
                else:  # Linux
                    monospace_paths = [
                        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
                        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
                        "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
                    ]

                flag_font_loaded = False
                for path in monospace_paths:
                    try:
                        if Path(path).exists():
                            self._flag_pil_font = ImageFont.truetype(path, flag_font_size)
                            self._logger.debug(
                                f"Created PIL flag font (monospace): {path}, size: {flag_font_size}"
                            )
                            flag_font_loaded = True
                            break
                    except OSError:
                        continue

                if not flag_font_loaded:
                    # Fallback: try to load by name (may work on some systems)
                    for font_name in [
                        "Courier",
                        "Courier New",
                        "Monaco",
                        "Consolas",
                        "Liberation Mono",
                    ]:
                        try:
                            self._flag_pil_font = ImageFont.truetype(font_name, flag_font_size)
                            self._logger.debug(
                                f"Created PIL flag font (monospace by name): {font_name}, size: {flag_font_size}"
                            )
                            flag_font_loaded = True
                            break
                        except OSError:
                            continue

                if not flag_font_loaded:
                    # Final fallback: use default monospace font
                    self._flag_pil_font = ImageFont.load_default()
                    self._logger.debug(
                        f"Created PIL flag font (fallback to default monospace), size: {flag_font_size}"
                    )
            except Exception as e:
                self._flag_pil_font = ImageFont.load_default()
                self._logger.warning(
                    f"Created PIL flag font (error fallback): default monospace font, size: {flag_font_size}, error: {e}"
                )

            # Also create Tkinter font for compatibility (use monospace font - matches Java's "monospaced")
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
                try:
                    self._flag_font = tkfont.Font(family=family, size=flag_font_size)
                    if family in tkfont.families():
                        self._logger.debug(
                            f"Created flag font (monospace error fallback): {family}, size: {flag_font_size}"
                        )
                        flag_font_created = True
                        break
                except (tk.TclError, ValueError):
                    continue

            if not flag_font_created:
                self._flag_font = tkfont.Font(family="Courier", size=flag_font_size)
                self._logger.debug(
                    f"Created flag font (monospace error fallback): Courier, size: {flag_font_size}"
                )

    def _get_font_family_from_file(self, font_path: Path) -> str | None:
        """Try to extract font family name from TTF file."""
        try:
            # Method 1: Try using fontTools if available (most reliable)
            try:
                from fontTools.ttLib import TTFont

                ttf = TTFont(str(font_path))
                name_table = ttf["name"]
                # Look for family name (nameID 1)
                # Prefer Windows platform (platformID 3) as it's most common
                family_name = None
                for record in name_table.names:
                    if record.nameID == 1:  # Family name
                        if record.platformID == 3:  # Windows/Unicode - prefer this
                            if isinstance(record.string, bytes):
                                try:
                                    family_name = record.string.decode("utf-16-be")
                                    break  # Found preferred platform, use it
                                except UnicodeDecodeError:
                                    pass
                        elif not family_name:  # Fallback to other platforms if not found yet
                            if isinstance(record.string, bytes):
                                try:
                                    family_name = record.string.decode("utf-16-be")
                                except UnicodeDecodeError:
                                    try:
                                        family_name = record.string.decode("utf-8")
                                    except UnicodeDecodeError:
                                        with contextlib.suppress(UnicodeDecodeError):
                                            family_name = record.string.decode("latin-1")
                            else:
                                family_name = str(record.string)

                if family_name:
                    self._logger.debug(f"Extracted font family name (fontTools): '{family_name}'")
                    return family_name
            except ImportError:
                # fontTools not available, try manual parsing
                pass
            except Exception as e:
                self._logger.warning(f"Error reading TTF file with fontTools: {e}")

            # Method 2: Manual TTF parsing (simplified - reads name table)
            try:
                with open(font_path, "rb") as f:
                    data = f.read()

                # TTF file structure: offset table at start
                # Read numTables (2 bytes at offset 4)
                num_tables = int.from_bytes(data[4:6], byteorder="big")

                # Find 'name' table
                name_table_offset = None
                name_table_length = None
                for i in range(num_tables):
                    table_offset = 12 + i * 16
                    tag = data[table_offset : table_offset + 4].decode("ascii", errors="ignore")
                    if tag == "name":
                        name_table_offset = int.from_bytes(
                            data[table_offset + 8 : table_offset + 12], byteorder="big"
                        )
                        name_table_length = int.from_bytes(
                            data[table_offset + 12 : table_offset + 16], byteorder="big"
                        )
                        break

                if name_table_offset and name_table_length is not None:
                    # Read name table
                    name_data = data[name_table_offset : name_table_offset + name_table_length]
                    # Format: format (2), count (2), stringOffset (2)
                    _format = int.from_bytes(name_data[0:2], byteorder="big")
                    count = int.from_bytes(name_data[2:4], byteorder="big")
                    string_offset = int.from_bytes(name_data[4:6], byteorder="big")

                    # Read name records
                    family_name = None
                    for i in range(count):
                        record_offset = 6 + i * 12
                        platform_id = int.from_bytes(
                            name_data[record_offset : record_offset + 2], byteorder="big"
                        )
                        name_id = int.from_bytes(
                            name_data[record_offset + 6 : record_offset + 8], byteorder="big"
                        )
                        length = int.from_bytes(
                            name_data[record_offset + 8 : record_offset + 10], byteorder="big"
                        )
                        offset = int.from_bytes(
                            name_data[record_offset + 10 : record_offset + 12], byteorder="big"
                        )

                        if name_id == 1:  # Family name
                            string_data = name_data[
                                string_offset + offset : string_offset + offset + length
                            ]
                            if platform_id == 3:  # Windows/Unicode
                                try:
                                    family_name = string_data.decode("utf-16-be")
                                    break
                                except UnicodeDecodeError:
                                    pass
                            elif not family_name:  # Fallback
                                try:
                                    family_name = string_data.decode("utf-16-be")
                                except UnicodeDecodeError:
                                    with contextlib.suppress(UnicodeDecodeError):
                                        family_name = string_data.decode("latin-1")

                    if family_name:
                        self._logger.debug(
                            f"Extracted font family name (manual parse): '{family_name}'"
                        )
                        return family_name
            except Exception as e:
                self._logger.warning(f"Error manually parsing TTF file: {e}")
                import traceback

                traceback.print_exc()

            self._logger.warning("Could not extract font family name from TTF file")
            return None
        except Exception as e:
            self._logger.error(f"Error extracting font family: {e}")
            import traceback

            traceback.print_exc()
            return None

    def build_layout(self):
        """Build the window layout."""
        # Load font (must be after Tkinter root window is created)
        # The frame is created in build(), so we can load fonts now
        self.load_font()

        # Create main panel with background
        if self._bg_image:
            self._main_panel = ImagePanel(self._frame, image=self._bg_image)
        else:
            self._main_panel = ImagePanel(self._frame)
            self._main_panel.config(bg="#000000")

        self._main_panel.pack(fill=tk.BOTH, expand=True)
        self._main_panel.config(width=self._wmainpan, height=self._hmainpan)

        # Initialize display text
        self._display_text = ""
        self._flag_text = ""

        # Create composite image with text rendered using PIL
        # We'll render text onto the background image and update it when text changes
        if self._bg_image:
            self._render_display()

        # Build buttons with exact layout from Java
        self._build_buttons()

    def _render_display(self):
        """Render display text onto background image using PIL."""
        if not self._bg_image:
            return

        # Create a copy of the background image to draw on
        self._composite_image = self._bg_image.copy()
        draw = ImageDraw.Draw(self._composite_image)

        # Convert color string to RGB tuple
        def hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
            hex_str = hex_str.lstrip("#")
            if len(hex_str) == 6:
                r = int(hex_str[0:2], 16)
                g = int(hex_str[2:4], 16)
                b = int(hex_str[4:6], 16)
                return (r, g, b)
            return (0, 255, 0)  # Default green

        display_color_str = self._display_face_color or "#00FF00"
        display_color_rgb = hex_to_rgb(display_color_str)

        # Calculate text positions
        # Main display text - right-aligned, vertically centered
        display_x = self._lcd_x + self._wdis - self._rdis
        display_y = self._lcd_y + self._hdis // 2

        # Flag display text - right-aligned, positioned below main display
        flag_y = self._lcd_y + self._hdis + self._bfdis + self._hfdis // 2
        flag_x = self._lcd_x + self._wfdis - self._rfdis

        # Draw main display text (right-aligned)
        if self._font and self._display_text:
            # Get text bounding box to calculate right alignment
            bbox = draw.textbbox((0, 0), self._display_text, font=self._font)
            if len(bbox) >= 4:
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            else:
                # Fallback if bbox doesn't have expected format
                # Note: textbbox always returns 4-tuple, but kept for type safety
                text_width = 0
                text_height = 0
                bbox = (0, 0, 0, 0)  # Ensure bbox is defined
            # Calculate right-aligned position (x is the right edge, subtract text width)
            if len(bbox) >= 4:
                text_x = display_x - text_width
                text_y = display_y - text_height // 2
                # Draw text
                draw.text(
                    (text_x, text_y), self._display_text, fill=display_color_rgb, font=self._font
                )

        # Draw flag display text (right-aligned)
        # Use black color for flags
        if self._flag_pil_font and self._flag_text:
            # Get text bounding box to calculate right alignment
            bbox = draw.textbbox((0, 0), self._flag_text, font=self._flag_pil_font)
            text_width = bbox[2] - bbox[0]
            # Calculate right-aligned position (x is the right edge, subtract text width)
            text_x = flag_x - text_width
            # Use a reference character without descenders ('A') to determine baseline position
            # This ensures consistent vertical alignment regardless of descenders in the text
            # PIL's draw.text() uses y coordinate as the baseline, not the top
            ref_bbox = draw.textbbox((0, 0), "A", font=self._flag_pil_font)
            ref_top = ref_bbox[1]  # Top of capital letter
            ref_bottom = ref_bbox[3]  # Bottom of capital letter (baseline)
            ref_height = ref_bottom - ref_top
            # Center the text at flag_y: baseline should be ref_height/2 below the center
            # So: text_y (baseline) = flag_y + ref_height / 2
            text_y = int(flag_y + ref_height / 2)
            # Draw text using black color
            draw.text(
                (text_x, text_y),
                self._flag_text,
                fill=(0, 0, 0),  # Black color
                font=self._flag_pil_font,
            )

        # Update the display with the composite image
        if self._main_panel:
            self._main_panel.set_image_obj(self._composite_image)

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

            # Create button
            btn: ImageButton | tk.Button
            if key_name in self._image_map:
                img = self._image_map[key_name]
                # Create button with image (ImageButton will create PhotoImage internally)
                btn = ImageButton(self._main_panel, image=img, key=key)
                # Ensure bg colors are strings
                bg_color = str(self._button_bg_color) if self._button_bg_color else "#000000"
                btn.config(
                    borderwidth=0,
                    highlightthickness=0,
                    relief=tk.FLAT,
                    bg=bg_color,
                    activebackground=bg_color,
                    compound=tk.CENTER,
                )
            else:
                # Fallback: create text button if image not available
                btn_text = self._get_button_text(key)
                # Ensure bg and fg are strings (not None)
                bg_color = str(self._button_bg_color) if self._button_bg_color else "#000000"
                fg_color = str(self._button_face_color) if self._button_face_color else "#FFFFFF"
                text_btn = tk.Button(
                    self._main_panel,
                    text=btn_text,
                    borderwidth=1,
                    highlightthickness=1,
                    relief=tk.RAISED,
                    bg=bg_color,
                    fg=fg_color,
                    font=("Arial", max(8, self._font_size // 4)),
                )
                text_btn._key = key
                btn = text_btn

            # Calculate position (same as Tkinter/Java)
            x = gridx * (self._wbot + 2 * self._xpad) + self._xpad + int(35 * self._size)
            y = self._hdispan + gridy * (self._hbot + 2 * self._ypad) + self._ypad

            # Place button using place() on Canvas
            btn.place(x=x, y=y, width=btn_width, height=btn_height)

            # Bind click handler
            def make_handler(k: Key) -> Callable[[], None]:
                return lambda: self._on_button_click(k)

            btn.config(command=make_handler(key))

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
        if self._controller and self._frame:
            # Show pressed state first
            self._controller.key_pressed(key)
            # Then release after a short delay to show the visual effect
            self._frame.after(
                50, lambda: self._controller.key_released(key) if self._controller else None
            )

    def _on_closing(self):
        """Handle window closing."""
        if self._controller:
            self._controller.quit()
        if self._frame:
            try:
                # Check if window still exists before destroying
                if self._frame.winfo_exists():
                    self._frame.destroy()
            except (RuntimeError, tk.TclError):
                # Window is already being destroyed or has been destroyed
                pass

    def update_display(self):
        """Update display from calculator."""
        if self._controller:
            executor = self._controller.get_executor()
            if executor:
                display_str = executor.get_display().get_string()
                flag_str = executor.get_flags().get_display_str()

                # Remove extra spaces to make it more compact
                # flag_str = ' '.join(flag_str.split())  # Collapse multiple spaces to single space
                self._logger.debug(
                    f"Flag display string: '{flag_str}' (length: {len(flag_str) if flag_str else 0})"
                )

                # Update text strings
                self._display_text = display_str
                self._flag_text = flag_str if flag_str else ""

                # Re-render the display with PIL
                self._render_display()

    def show(self):
        """Show window."""
        if self._frame:
            self._frame.deiconify()
            self._frame.lift()

    def hide(self):
        """Hide window."""
        if self._frame:
            self._frame.withdraw()

    def close(self):
        """Close window and exit application."""
        if self._frame:
            self._frame.destroy()

    def get_window_location(self) -> tuple[int, int]:
        """Get window location."""
        if self._frame:
            return (self._frame.winfo_x(), self._frame.winfo_y())
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
                pressed_photo = ImageTk.PhotoImage(pressed_img)
                btn.config(image=pressed_photo)
                if isinstance(btn, ImageButton):
                    btn._photo = pressed_photo  # Keep reference in ImageButton

    def key_released(self, key: Key):
        """Handle key release."""
        # Check if window still exists (might have been closed)
        try:
            if not self._frame:
                return
            # Try to check if window exists - this may raise TclError if destroyed
            if not self._frame.winfo_exists():
                return
        except (RuntimeError, tk.TclError):
            # Window is being destroyed
            return

        if key and key.name in self._buttons:
            try:
                btn = self._buttons[key.name]
                # Check if button widget still exists - may fail if root is gone
                try:
                    if not btn.winfo_exists():
                        return
                except (RuntimeError, tk.TclError):
                    return
                key_name = key.name
                if key_name in self._image_map:
                    normal_img = self._image_map[key_name]
                    # PhotoImage creation may fail if root window is destroyed
                    normal_photo = ImageTk.PhotoImage(normal_img)
                    btn.config(image=normal_photo)
                    if isinstance(btn, ImageButton):
                        btn._photo = normal_photo  # Keep reference in ImageButton
                self.update_display()
                # Auto-refresh register view if open
                self._update_register_view()
                # Auto-refresh history view if open
                self._update_history_view()
            except (RuntimeError, tk.TclError):
                # Window or widgets are being destroyed, ignore
                return

    def get_frame(self):
        """Get Tk frame."""
        return self._frame

    def set_icon(self):
        """Set window icon."""
        try:
            if self._skin_path is None:
                return
            icon_path = self._skin_path / "icon.png"
            if icon_path.exists():
                _icon_img = Image.open(icon_path)
                # Tkinter doesn't directly support setting icon from PIL Image
                # This would need platform-specific handling
                pass
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

        if self._frame is None:
            return
        self._menu_bar = tk.Menu(self._frame)
        self._frame.config(menu=self._menu_bar)

        # File menu
        file_menu = tk.Menu(self._menu_bar, tearoff=0)
        self._menu_bar.add_cascade(
            label=self._language_loader.get_value("FILE_MENU", "File"), menu=file_menu
        )
        file_menu.add_command(
            label=self._language_loader.get_value("FILE_IMPORT", "Import"),
            command=self._on_file_import,
            accelerator=f"Ctrl+{self._language_loader.get_shortcut('FILE_IMPORT', 'I').upper()}",
        )
        file_menu.add_command(
            label=self._language_loader.get_value("FILE_EXPORT", "Export"),
            command=self._on_file_export,
            accelerator=f"Ctrl+{self._language_loader.get_shortcut('FILE_EXPORT', 'E').upper()}",
        )
        file_menu.add_separator()
        file_menu.add_command(
            label=self._language_loader.get_value("FILE_QUIT", "Quit"),
            command=self._on_file_quit,
            accelerator=f"Ctrl+{self._language_loader.get_shortcut('FILE_QUIT', 'Q').upper()}",
        )

        # Edit menu
        edit_menu = tk.Menu(self._menu_bar, tearoff=0)
        self._menu_bar.add_cascade(
            label=self._language_loader.get_value("EDIT_MENU", "Edit"), menu=edit_menu
        )
        edit_menu.add_command(
            label=self._language_loader.get_value("EDIT_COPY", "Copy"),
            command=self._on_edit_copy,
            accelerator=f"Ctrl+{self._language_loader.get_shortcut('EDIT_COPY', 'C').upper()}",
        )
        edit_menu.add_command(
            label=self._language_loader.get_value("EDIT_PASTE", "Paste"),
            command=self._on_edit_paste,
            accelerator=f"Ctrl+{self._language_loader.get_shortcut('EDIT_PASTE', 'P').upper()}",
        )

        # Erase submenu
        erase_menu = tk.Menu(edit_menu, tearoff=0)
        edit_menu.add_cascade(
            label=self._language_loader.get_value("EDIT_ERASE", "Erase"), menu=erase_menu
        )
        erase_menu.add_command(
            label=self._language_loader.get_value("EDIT_ERASE_DSP", "Display"),
            command=self._on_edit_erase_display,
        )
        erase_menu.add_command(
            label=self._language_loader.get_value("EDIT_ERASE_STK", "Stack Registers"),
            command=self._on_edit_erase_stack,
        )
        erase_menu.add_command(
            label=self._language_loader.get_value("EDIT_ERASE_FIN", "Finance Registers"),
            command=self._on_edit_erase_finance,
        )
        erase_menu.add_command(
            label=self._language_loader.get_value("EDIT_ERASE_STA", "Statistic Registers"),
            command=self._on_edit_erase_statistic,
        )
        erase_menu.add_command(
            label=self._language_loader.get_value("EDIT_ERASE_REG", "All Registers"),
            command=self._on_edit_erase_all,
        )
        erase_menu.add_command(
            label=self._language_loader.get_value("EDIT_ERASE_PRG", "Program Steps"),
            command=self._on_edit_erase_program,
        )

        # View menu
        view_menu = tk.Menu(self._menu_bar, tearoff=0)
        self._menu_bar.add_cascade(
            label=self._language_loader.get_value("VIEW_MENU", "View"), menu=view_menu
        )

        # Size submenu
        size_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(
            label=self._language_loader.get_value("VIEW_SIZE", "Size"), menu=size_menu
        )
        self._size_var = tk.StringVar(value=str(self._cfg.get_size() if self._cfg else 1.0))
        size_menu.add_radiobutton(
            label=self._language_loader.get_value("VIEW_SIZE_VERY_SMALL", "Very Small"),
            variable=self._size_var,
            value="0.5",
            command=self._on_view_size,
        )
        size_menu.add_radiobutton(
            label=self._language_loader.get_value("VIEW_SIZE_SMALL", "Small"),
            variable=self._size_var,
            value="0.75",
            command=self._on_view_size,
        )
        size_menu.add_radiobutton(
            label=self._language_loader.get_value("VIEW_SIZE_MEDIUM", "Medium"),
            variable=self._size_var,
            value="1.0",
            command=self._on_view_size,
        )
        size_menu.add_radiobutton(
            label=self._language_loader.get_value("VIEW_SIZE_LARGE", "Large"),
            variable=self._size_var,
            value="1.25",
            command=self._on_view_size,
        )
        size_menu.add_radiobutton(
            label=self._language_loader.get_value("VIEW_SIZE_HUGE", "Huge"),
            variable=self._size_var,
            value="1.5",
            command=self._on_view_size,
        )

        # Skin submenu
        skin_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(
            label=self._language_loader.get_value("VIEW_SKIN", "Calculator skin"), menu=skin_menu
        )
        self._skin_var = tk.StringVar(
            value=self._cfg.get_skin() if self._cfg else Configuration.DEFAULT_SKIN
        )
        if self._skin_loader:
            for skin_id, skin_description in self._skin_loader.get_skins():
                skin_menu.add_radiobutton(
                    label=skin_description,
                    variable=self._skin_var,
                    value=skin_id,
                    command=self._on_view_skin,
                )

        # Options menu
        options_menu = tk.Menu(self._menu_bar, tearoff=0)
        self._menu_bar.add_cascade(
            label=self._language_loader.get_value("OPTIONS_MENU", "Options"), menu=options_menu
        )

        # Number format submenu
        num_format_menu = tk.Menu(options_menu, tearoff=0)
        options_menu.add_cascade(
            label=self._language_loader.get_value("OPTIONS_NUMBER_FORMAT", "Number format"),
            menu=num_format_menu,
        )
        self._num_format_var = tk.StringVar(
            value="dot" if not self._cfg or self._cfg.get_com() == 0 else "comma"
        )
        num_format_menu.add_radiobutton(
            label=self._language_loader.get_value("OPTIONS_NUMBER_FORMAT_DOT", "Dot (.)"),
            variable=self._num_format_var,
            value="dot",
            command=self._on_options_number_format,
        )
        num_format_menu.add_radiobutton(
            label=self._language_loader.get_value("OPTIONS_NUMBER_FORMAT_COMMA", "Comma (,)"),
            variable=self._num_format_var,
            value="comma",
            command=self._on_options_number_format,
        )

        # Date format submenu
        date_format_menu = tk.Menu(options_menu, tearoff=0)
        options_menu.add_cascade(
            label=self._language_loader.get_value("OPTIONS_DATE_FORMAT", "Date format"),
            menu=date_format_menu,
        )
        self._date_format_var = tk.StringVar(
            value="mdy" if not self._cfg or self._cfg.get_dmy() == 0 else "dmy"
        )
        date_format_menu.add_radiobutton(
            label=self._language_loader.get_value("OPTIONS_DATE_FORMAT_MONTH", "MM.DDYYYY"),
            variable=self._date_format_var,
            value="mdy",
            command=self._on_options_date_format,
        )
        date_format_menu.add_radiobutton(
            label=self._language_loader.get_value("OPTIONS_DATE_FORMAT_DAY", "DD.MMYYYY"),
            variable=self._date_format_var,
            value="dmy",
            command=self._on_options_date_format,
        )

        # Payment mode submenu
        payment_menu = tk.Menu(options_menu, tearoff=0)
        options_menu.add_cascade(
            label=self._language_loader.get_value("OPTIONS_PAYMENT_MODE", "Payment mode"),
            menu=payment_menu,
        )
        self._payment_var = tk.StringVar(
            value="end" if not self._cfg or self._cfg.get_beg() == 0 else "begin"
        )
        payment_menu.add_radiobutton(
            label=self._language_loader.get_value("OPTIONS_PAYMENT_MODE_BEGIN", "Begin"),
            variable=self._payment_var,
            value="begin",
            command=self._on_options_payment_mode,
        )
        payment_menu.add_radiobutton(
            label=self._language_loader.get_value("OPTIONS_PAYMENT_MODE_END", "End"),
            variable=self._payment_var,
            value="end",
            command=self._on_options_payment_mode,
        )

        # Tools menu
        tools_menu = tk.Menu(self._menu_bar, tearoff=0)
        self._menu_bar.add_cascade(
            label=self._language_loader.get_value("TOOLS_MENU", "Tools"), menu=tools_menu
        )
        tools_menu.add_command(
            label=self._language_loader.get_value("TOOLS_REGISTERS_VIEW", "Registers view"),
            command=self._on_tools_registers_view,
        )
        tools_menu.add_command(
            label=self._language_loader.get_value("TOOLS_HISTORY", "Instructions history"),
            command=self._on_tools_history,
        )

        # About menu
        about_menu = tk.Menu(self._menu_bar, tearoff=0)
        self._menu_bar.add_cascade(
            label=self._language_loader.get_value("ABOUT_MENU", "About"), menu=about_menu
        )
        about_menu.add_command(
            label=self._language_loader.get_value("ABOUT_AUTHOR", "Author"),
            command=self._on_about_author,
        )
        about_menu.add_command(
            label=self._language_loader.get_value("ABOUT_CONTRIBUTORS", "Contributors"),
            command=self._on_about_contributors,
        )
        about_menu.add_command(
            label=self._language_loader.get_value("ABOUT_SOFTWARE", "This Software"),
            command=self._on_about_software,
        )

    def _on_file_import(self):
        """Handle File > Import menu action."""
        self._logger.debug("File > Import (not implemented)")

    def _on_file_export(self):
        """Handle File > Export menu action."""
        self._logger.debug("File > Export (not implemented)")

    def _on_file_quit(self):
        """Handle File > Quit menu action."""
        self._on_closing()

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
        size = float(self._size_var.get())
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
            btn.destroy()
        self._buttons.clear()
        # Rebuild buttons
        self._build_buttons()
        # Re-render display
        self._render_display()
        # Update window geometry
        if self._frame:
            self._frame.geometry(f"{self._wmainpan}x{self._hmainpan}")

    def _on_view_skin(self):
        """Handle View > Skin menu action."""
        skin_id = self._skin_var.get()
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
            btn.destroy()
        self._buttons.clear()
        # Rebuild buttons
        self._build_buttons()
        # Re-render display
        self._render_display()

    def _on_options_number_format(self):
        """Handle Options > Number format menu action."""
        if self._cfg and self._controller:
            com = 0 if self._num_format_var.get() == "dot" else 1
            self._cfg.set_com(com)
            executor = self._controller.get_executor()
            if executor:
                executor.get_display().set_comma(com == 1)
                executor.update_display()
                self.update_display()

    def _on_options_date_format(self):
        """Handle Options > Date format menu action."""
        if self._cfg and self._controller:
            dmy = 0 if self._date_format_var.get() == "mdy" else 1
            self._cfg.set_dmy(dmy)
            executor = self._controller.get_executor()
            if executor:
                executor.get_flags().set_dmy(dmy)
                executor.update_display()
                self.update_display()

    def _on_options_payment_mode(self):
        """Handle Options > Payment mode menu action."""
        if self._cfg and self._controller:
            beg = 0 if self._payment_var.get() == "end" else 1
            self._cfg.set_beg(beg)
            executor = self._controller.get_executor()
            if executor:
                executor.get_flags().set_begin(beg)
                executor.update_display()
                self.update_display()

    def _update_register_view(self):
        """Update register view window if it's open."""
        if self._register_view_window is not None:
            try:
                # Check if window still exists
                if self._register_view_window._window.winfo_exists():
                    self._register_view_window.update()
            except (tk.TclError, AttributeError):
                # Window was destroyed
                self._register_view_window = None

    def _on_tools_registers_view(self):
        """Handle Tools > Registers view menu action."""
        from hp12c.ui.register_view_tkinter import RegisterViewWindow

        executor = self._controller.get_executor() if self._controller else None
        try:
            if self._register_view_window is None:
                self._register_view_window = RegisterViewWindow(
                    self._frame, executor, main_window=self
                )
            else:
                # Check if window still exists
                try:
                    self._register_view_window._window.winfo_exists()
                except tk.TclError:
                    # Window was destroyed, create new one
                    self._register_view_window = RegisterViewWindow(
                        self._frame, executor, main_window=self
                    )
                else:
                    self._register_view_window.show()
                    self._register_view_window.update()
        except Exception as e:
            self._logger.error(f"Error opening register view: {e}")
            # Create new window on error
            self._register_view_window = RegisterViewWindow(self._frame, executor, main_window=self)

    def _on_tools_history(self):
        """Handle Tools > Instructions history menu action."""
        from hp12c.ui.history_view_tkinter import HistoryViewWindow

        executor = self._controller.get_executor() if self._controller else None
        try:
            if self._history_view_window is None:
                self._history_view_window = HistoryViewWindow(
                    self._frame, executor, main_window=self
                )
            else:
                # Check if window still exists
                try:
                    self._history_view_window._window.winfo_exists()
                except tk.TclError:
                    # Window was destroyed, create new one
                    self._history_view_window = HistoryViewWindow(
                        self._frame, executor, main_window=self
                    )
                else:
                    self._history_view_window.show()
                    self._history_view_window.update()
        except Exception as e:
            self._logger.error(f"Error opening history view: {e}")
            # Create new window on error
            self._history_view_window = HistoryViewWindow(self._frame, executor, main_window=self)

    def _update_history_view(self):
        """Update history view window if it's open."""
        if self._history_view_window is not None:
            try:
                # Check if window still exists
                if self._history_view_window._window.winfo_exists():
                    self._history_view_window.update()
            except (tk.TclError, AttributeError):
                # Window was destroyed
                self._history_view_window = None

    def _on_about_author(self):
        """Handle About > Author menu action."""
        self._logger.debug("About > Author (not implemented)")

    def _on_about_contributors(self):
        """Handle About > Contributors menu action."""
        self._logger.debug("About > Contributors (not implemented)")

    def _on_about_software(self):
        """Handle About > This Software menu action."""
        import tkinter.messagebox as messagebox

        messagebox.showinfo(
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
        if self._frame:
            self._frame.clipboard_clear()
            self._frame.clipboard_append(text)

    def get_from_clipboard(self) -> str:
        """Get text from clipboard."""
        if self._frame:
            try:
                result = self._frame.clipboard_get()
                return str(result) if result is not None else ""
            except tk.TclError:
                return ""
        return ""
