"""
Language string loader utility.
Loads language strings from XML files similar to Java StringList.
"""

import xml.etree.ElementTree as ET
from pathlib import Path


class LanguageLoader:
    """Loads language strings from XML files."""

    def __init__(self, language: str = "en", base_path: Path | None = None):
        """Initialize language loader.

        Args:
            language: Language code (e.g., "en", "es", "pt", "fr")
            base_path: Base path to resources directory. If None, will try to find it.
        """
        self._language = language
        self._base_path = base_path
        self._strings: dict[str, str] = {}
        self._shortcuts: dict[str, str] = {}
        self._descriptions: dict[str, str] = {}
        self._load_language()

    def _load_language(self):
        """Load language strings from XML file."""
        if not self._base_path:
            # Try to find base path
            module_dir = Path(__file__).parent.parent.parent
            self._base_path = module_dir / "resources"

        lang_file = self._base_path / "langs" / f"{self._language}.xml"

        if not lang_file.exists():
            # Fallback to English if language file not found
            if self._language != "en":
                lang_file = self._base_path / "langs" / "en.xml"
            if not lang_file.exists():
                print(f"Warning: Language file not found: {lang_file}")
                return

        try:
            tree = ET.parse(lang_file)
            root = tree.getroot()

            for lng in root.findall("lng"):
                lang_id = lng.find("id")
                value = lng.find("vl")
                description = lng.find("ds")
                shortcut = lng.find("sc")

                if lang_id is not None and lang_id.text:
                    lang_id_text = lang_id.text
                    if value is not None and value.text:
                        self._strings[lang_id_text] = value.text
                    if shortcut is not None and shortcut.text:
                        self._shortcuts[lang_id_text] = shortcut.text
                    if description is not None and description.text:
                        self._descriptions[lang_id_text] = description.text

        except Exception as e:
            print(f"Error loading language file {lang_file}: {e}")

    def get_value(self, key: str, default: str = "") -> str:
        """Get language string value.

        Args:
            key: Language key (e.g., "FILE_MENU")
            default: Default value if key not found

        Returns:
            Language string value
        """
        return self._strings.get(key, default)

    def get_shortcut(self, key: str, default: str = "") -> str:
        """Get keyboard shortcut for a menu item.

        Args:
            key: Language key
            default: Default value if key not found

        Returns:
            Shortcut character
        """
        return self._shortcuts.get(key, default)

    def get_description(self, key: str, default: str = "") -> str:
        """Get description/tooltip for a menu item.

        Args:
            key: Language key
            default: Default value if key not found

        Returns:
            Description string
        """
        return self._descriptions.get(key, default)
