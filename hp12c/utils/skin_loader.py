"""
Skin list loader utility.
Loads available skins from XML file.
"""

import xml.etree.ElementTree as ET
from pathlib import Path


class SkinLoader:
    """Loads skin list from XML file."""

    def __init__(self, base_path: Path | None = None):
        """Initialize skin loader.

        Args:
            base_path: Base path to resources directory. If None, will try to find it.
        """
        self._base_path = base_path
        self._skins: list[tuple[str, str]] = []  # List of (id, description) tuples
        self._load_skin_list()

    def _load_skin_list(self):
        """Load skin list from XML file."""
        if not self._base_path:
            # Try to find base path
            module_dir = Path(__file__).parent.parent.parent
            self._base_path = module_dir / "resources"

        skin_list_file = self._base_path / "skins" / "list.xml"

        if not skin_list_file.exists():
            print(f"Warning: Skin list file not found: {skin_list_file}")
            return

        try:
            tree = ET.parse(skin_list_file)
            root = tree.getroot()

            for item in root.findall("item"):
                skin_id = item.find("id")
                description = item.find("ds")

                if skin_id is not None and skin_id.text:
                    skin_id_text = skin_id.text
                    description_text = (
                        description.text
                        if description is not None and description.text
                        else skin_id_text
                    )
                    self._skins.append((skin_id_text, description_text))

        except Exception as e:
            print(f"Error loading skin list file {skin_list_file}: {e}")

    def get_skins(self) -> list[tuple[str, str]]:
        """Get list of available skins.

        Returns:
            List of (skin_id, description) tuples
        """
        return self._skins

    def get_skin_ids(self) -> list[str]:
        """Get list of skin IDs.

        Returns:
            List of skin IDs
        """
        return [skin_id for skin_id, _ in self._skins]
