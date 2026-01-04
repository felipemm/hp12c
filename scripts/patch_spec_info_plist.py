#!/usr/bin/env python3
"""
Patch PyInstaller spec file with info_plist settings.
Reads version from pyproject.toml and injects macOS metadata.
"""

import re
import sys
from pathlib import Path


def get_version_from_pyproject() -> str:
    """Get version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")

    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")

    return match.group(1)


def patch_spec_file(spec_path: Path, version: str) -> None:
    """Patch spec file with info_plist."""
    content = spec_path.read_text(encoding="utf-8")

    # Define the info_plist dictionary
    info_plist = f"""    info_plist={{
        'CFBundleName': 'HP12C',
        'CFBundleDisplayName': 'HP12C Financial Calculator',
        'CFBundleShortVersionString': '{version}',
        'CFBundleVersion': '{version}',
        'CFBundleGetInfoString': 'HP12C Financial Calculator {version}',
        'NSHumanReadableCopyright': 'GPL-3.0-or-later',
    }}"""

    # Check if BUNDLE already has info_plist
    if "info_plist=" in content:
        # Update existing info_plist - match the entire info_plist dict
        # Match from info_plist={ to the closing }, including any trailing comma
        pattern = r"info_plist=\{.*?\},"
        content = re.sub(pattern, info_plist + ",", content, flags=re.DOTALL)
    else:
        # Add info_plist before the closing parenthesis of BUNDLE
        # Match the BUNDLE call: find the last parameter and its comma, then the closing paren
        # Pattern: match everything from BUNDLE( up to the last parameter's comma (inclusive)
        # Then replace the closing paren with info_plist + comma + closing paren
        bundle_pattern = r"(app\s*=\s*BUNDLE\(\s*coll,\s*(?:[^\n]+\n)*[^\n]+,\s*)(\))"

        def replace_func(match):
            params = match.group(1).rstrip()  # Everything up to and including the last comma
            closing = match.group(2)  # The closing paren
            # params already includes the trailing comma from the last parameter
            # Just add info_plist with its comma before the closing paren
            return f"{params}\n{info_plist},\n{closing}"

        content = re.sub(bundle_pattern, replace_func, content)

        # Clean up any stray commas on their own line (common issue)
        # Remove lines that contain only whitespace and a comma
        lines = content.split("\n")
        cleaned_lines = []
        for i, line in enumerate(lines):
            stripped = line.strip()
            # Skip lines that are just a comma, but only if the previous line already ends with a comma
            if stripped == "," and i > 0:
                prev_stripped = lines[i - 1].strip()
                if prev_stripped.endswith(","):
                    continue  # Skip this stray comma line
            cleaned_lines.append(line)
        content = "\n".join(cleaned_lines)

    spec_path.write_text(content, encoding="utf-8")
    print(f"✓ Patched {spec_path} with info_plist (version {version})")


def main():
    if len(sys.argv) < 2:
        print("Usage: python patch_spec_info_plist.py <spec_file>")
        sys.exit(1)

    spec_path = Path(sys.argv[1])
    if not spec_path.exists():
        print(f"Error: {spec_path} not found")
        sys.exit(1)

    try:
        version = get_version_from_pyproject()
        patch_spec_file(spec_path, version)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
