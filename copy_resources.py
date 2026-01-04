"""
Script to copy resources from Java implementation.
Run this to copy skins and language files.
"""

import shutil
from pathlib import Path

def copy_resources():
    """Copy resources from Java implementation."""
    source = Path("../hp12c_java/hp12c_decompiled/resources")
    target = Path("resources")

    if not source.exists():
        print(f"Source directory not found: {source}")
        print("Please ensure the Java decompiled resources are available.")
        return

    # Copy skins
    if (source / "skins").exists():
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
        print(f"Resources copied to {target}")
    else:
        print("Skins directory not found in source")

if __name__ == "__main__":
    copy_resources()
