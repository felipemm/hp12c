#!/usr/bin/env python3
"""
Coverage badge update script for HP12C Calculator.

This script:
1. Extracts the coverage percentage from pytest coverage output
2. Updates the coverage badge in README.md with the new percentage
3. Sets the appropriate badge color based on coverage percentage

Usage:
    python scripts/update_coverage_badge.py [coverage_percentage]

If coverage_percentage is not provided, the script will try to extract it
from the coverage report or pytest output.
"""

import argparse
import re
import sys
from pathlib import Path


def get_badge_color(percentage: float) -> str:
    """Get the badge color based on coverage percentage."""
    if percentage >= 80:
        return "brightgreen"
    elif percentage >= 60:
        return "green"
    elif percentage >= 40:
        return "yellow"
    elif percentage >= 20:
        return "orange"
    else:
        return "red"


def extract_coverage_from_report() -> float | None:
    """Try to extract coverage percentage from coverage report files."""
    # Try to read from htmlcov/index.html
    htmlcov_path = Path("htmlcov/index.html")
    if htmlcov_path.exists():
        content = htmlcov_path.read_text(encoding="utf-8")
        # Look for percentage in the HTML - multiple patterns to try
        patterns = [
            r"TOTAL.*?(\d+(?:\.\d+)?)%",  # In table format
            r"total.*?(\d+(?:\.\d+)?)%",  # Case insensitive
            r"(\d+(?:\.\d+)?)%</tfoot>",  # End of table
            r'<span class="pc_cov">(\d+(?:\.\d+)?)%</span>',  # Coverage badge format
        ]
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return float(match.group(1))

    return None


def update_readme_badge(percentage: float, readme_path: Path) -> None:
    """Update the coverage badge in README.md."""
    if not readme_path.exists():
        raise FileNotFoundError(f"README.md not found at {readme_path}")

    content = readme_path.read_text(encoding="utf-8")

    # Round to nearest integer for badge
    rounded_percentage = round(percentage)
    color = get_badge_color(percentage)

    # Pattern to match the coverage badge
    # Matches: ![Coverage](https://img.shields.io/badge/coverage-XX%25-COLOR)
    pattern = r"!\[Coverage\]\(https://img\.shields\.io/badge/coverage-\d+%25-\w+\)"
    replacement = (
        f"![Coverage](https://img.shields.io/badge/coverage-{rounded_percentage}%25-{color})"
    )

    new_content = re.sub(pattern, replacement, content)

    if new_content == content:
        # Badge not found, try to find where to insert it
        # Look for the line with other badges
        lines = content.split("\n")
        for i, line in enumerate(lines):
            if "![codecov]" in line or "![Coverage]" in line:
                lines[i] = replacement
                new_content = "\n".join(lines)
                break
        else:
            # Insert after the Version badge
            for i, line in enumerate(lines):
                if "![Version]" in line:
                    lines.insert(i + 1, replacement)
                    new_content = "\n".join(lines)
                    break

    readme_path.write_text(new_content, encoding="utf-8")
    print(f"Updated coverage badge in README.md: {rounded_percentage}% ({color})")


def main() -> int:
    """Main function."""
    parser = argparse.ArgumentParser(description="Update coverage badge in README.md")
    parser.add_argument(
        "coverage",
        type=float,
        nargs="?",
        help="Coverage percentage (0-100). If not provided, will try to extract from coverage report.",
    )
    parser.add_argument(
        "--readme",
        type=Path,
        default=Path("README.md"),
        help="Path to README.md file (default: README.md)",
    )

    args = parser.parse_args()

    # Get coverage percentage
    if args.coverage is not None:
        percentage = args.coverage
    else:
        percentage = extract_coverage_from_report()
        if percentage is None:
            print(
                "Error: Could not extract coverage percentage. "
                "Please provide it as an argument or ensure coverage report exists.",
                file=sys.stderr,
            )
            return 1

    # Validate percentage
    if not (0 <= percentage <= 100):
        print(
            f"Error: Coverage percentage must be between 0 and 100, got {percentage}",
            file=sys.stderr,
        )
        return 1

    # Update README
    try:
        update_readme_badge(percentage, args.readme)
        return 0
    except Exception as e:
        print(f"Error updating README: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
