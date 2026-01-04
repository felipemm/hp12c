#!/usr/bin/env python3
"""
Version bumping script for HP12C Calculator.

This script automates the process of:
1. Bumping the version (major, minor, or patch)
2. Updating pyproject.toml
3. Updating hp12c/__init__.py
4. Updating CHANGELOG.md
5. Creating a git commit and tag
6. Optionally pushing to GitHub

Usage:
    python scripts/bump_version.py [major|minor|patch] [--no-commit] [--no-tag] [--no-push]
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def get_current_version() -> str:
    """Get the current version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise FileNotFoundError("pyproject.toml not found")

    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")

    return match.group(1)


def bump_version(version: str, bump_type: str) -> str:
    """Bump version according to semantic versioning."""
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")

    major, minor, patch = map(int, parts)

    if bump_type == "major":
        major += 1
        minor = 0
        patch = 0
    elif bump_type == "minor":
        minor += 1
        patch = 0
    elif bump_type == "patch":
        patch += 1
    else:
        raise ValueError(f"Invalid bump type: {bump_type}. Use major, minor, or patch")

    return f"{major}.{minor}.{patch}"


def update_pyproject_toml(new_version: str) -> None:
    """Update version in pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    content = pyproject_path.read_text(encoding="utf-8")
    content = re.sub(r'(version\s*=\s*")[^"]+(")', rf"\g<1>{new_version}\g<2>", content)
    pyproject_path.write_text(content, encoding="utf-8")
    print(f"✓ Updated pyproject.toml to version {new_version}")


def update_init_py(new_version: str) -> None:
    """Update version in hp12c/__init__.py."""
    init_path = Path("hp12c/__init__.py")
    if not init_path.exists():
        raise FileNotFoundError("hp12c/__init__.py not found")

    content = init_path.read_text(encoding="utf-8")
    content = re.sub(r'(__version__\s*=\s*")[^"]+(")', rf"\g<1>{new_version}\g<2>", content)
    init_path.write_text(content, encoding="utf-8")
    print(f"✓ Updated hp12c/__init__.py to version {new_version}")


def update_changelog(new_version: str) -> None:
    """Update CHANGELOG.md by moving Unreleased section to a version section."""
    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        print("⚠ Warning: CHANGELOG.md not found, skipping update")
        return

    content = changelog_path.read_text(encoding="utf-8")

    # Check if there's an Unreleased section
    if "## [Unreleased]" not in content:
        print("⚠ Warning: No [Unreleased] section found in CHANGELOG.md")
        return

    # Get today's date in YYYY-MM-DD format
    today = datetime.now().strftime("%Y-%m-%d")

    # Insert the new version section after [Unreleased]
    # Keep [Unreleased] and add the new version below it
    content = content.replace("## [Unreleased]", f"## [Unreleased]\n\n## [{new_version}] - {today}")

    # Update the links section at the bottom
    # Find the [Unreleased] link and add a new version link
    unreleased_link_pattern = r"\[Unreleased\]:\s*(https://[^\s]+)"
    match = re.search(unreleased_link_pattern, content)

    if match:
        base_url = match.group(1)
        # Extract the base URL (everything before the compare part)
        if "/compare/" in base_url:
            base_url = base_url.split("/compare/")[0]

        # Add the new version link
        version_link = f"[{new_version}]: {base_url}/releases/tag/v{new_version}\n"

        # Update the Unreleased link to compare from the new version
        new_unreleased_link = f"[Unreleased]: {base_url}/compare/v{new_version}...HEAD\n"

        # Replace the old Unreleased link
        content = re.sub(unreleased_link_pattern, new_unreleased_link, content)

        # Insert the new version link before the Unreleased link
        content = re.sub(r"(\[Unreleased\]:\s*https://[^\s]+\n)", version_link + r"\1", content)

    changelog_path.write_text(content, encoding="utf-8")
    print(f"✓ Updated CHANGELOG.md with version {new_version}")


def check_git_status() -> None:
    """Check if git is available and if there are uncommitted changes."""
    try:
        # Check if git is available
        subprocess.run(["git", "--version"], check=True, capture_output=True)

        # Check for uncommitted changes (excluding the files we'll modify)
        result = subprocess.run(
            ["git", "status", "--porcelain"], check=True, capture_output=True, text=True
        )

        uncommitted = [
            line
            for line in result.stdout.strip().split("\n")
            if line
            and not any(
                line.endswith(f) for f in ["pyproject.toml", "hp12c/__init__.py", "CHANGELOG.md"]
            )
        ]

        if uncommitted:
            print("⚠ Warning: You have uncommitted changes:")
            for line in uncommitted[:5]:  # Show first 5
                print(f"  {line}")
            if len(uncommitted) > 5:
                print(f"  ... and {len(uncommitted) - 5} more")
            response = input("\nContinue anyway? (y/N): ")
            if response.lower() != "y":
                raise SystemExit("Aborted by user")
    except subprocess.CalledProcessError as e:
        print(f"⚠ Warning: Could not check git status: {e.stderr.decode()}")
    except FileNotFoundError as err:
        raise SystemExit("✗ Error: git is not available. Please install git.") from err


def git_commit(version: str) -> None:
    """Create a git commit with the version changes."""
    try:
        subprocess.run(
            ["git", "add", "pyproject.toml", "hp12c/__init__.py", "CHANGELOG.md"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", f"chore: bump version to {version}"],
            check=True,
            capture_output=True,
        )
        print(f"✓ Created git commit for version {version}")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode() if e.stderr else "Unknown error"
        print(f"✗ Error creating git commit: {error_msg}")
        raise


def git_tag(version: str) -> None:
    """Create a git tag for the version."""
    tag_name = f"v{version}"
    try:
        subprocess.run(
            ["git", "tag", "-a", tag_name, "-m", f"Release {version}"],
            check=True,
            capture_output=True,
        )
        print(f"✓ Created git tag {tag_name}")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error creating git tag: {e.stderr.decode()}")
        raise


def git_push(push_commit: bool = True, push_tag: bool = True) -> None:
    """Push commits and tags to the remote repository."""
    try:
        if push_commit:
            subprocess.run(["git", "push"], check=True, capture_output=True)
            print("✓ Pushed commits to remote")

        if push_tag:
            subprocess.run(["git", "push", "--tags"], check=True, capture_output=True)
            print("✓ Pushed tags to remote")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error pushing to remote: {e.stderr.decode()}")
        raise


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Bump version and update related files")
    parser.add_argument(
        "bump_type",
        choices=["major", "minor", "patch"],
        help="Type of version bump (major, minor, or patch)",
    )
    parser.add_argument("--no-commit", action="store_true", help="Don't create a git commit")
    parser.add_argument("--no-tag", action="store_true", help="Don't create a git tag")
    parser.add_argument("--no-push", action="store_true", help="Don't push to remote repository")

    args = parser.parse_args()

    try:
        # Check git status if we're going to commit
        if not args.no_commit:
            check_git_status()

        # Get current version
        current_version = get_current_version()
        print(f"Current version: {current_version}")

        # Bump version
        new_version = bump_version(current_version, args.bump_type)
        print(f"New version: {new_version}\n")

        # Update files
        update_pyproject_toml(new_version)
        update_init_py(new_version)
        update_changelog(new_version)

        # Git operations
        if not args.no_commit:
            git_commit(new_version)

        if not args.no_tag:
            git_tag(new_version)

        if not args.no_push:
            git_push(push_tag=not args.no_tag)

        print(f"\n✓ Successfully bumped version to {new_version}")
        if args.no_push:
            print(
                "\n⚠ Note: Changes were not pushed. Run 'git push' and 'git push --tags' manually."
            )

    except KeyboardInterrupt:
        print("\n\n✗ Aborted by user", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
