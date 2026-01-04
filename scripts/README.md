# Scripts

This directory contains utility scripts for the HP12C Calculator project.

## bump_version.py

Automates the process of bumping the project version and creating a release.

### Features

- Bumps version in `pyproject.toml` and `hp12c/__init__.py`
- Updates `CHANGELOG.md` by moving the `[Unreleased]` section to a versioned section
- Creates a git commit with the version changes
- Creates a git tag for the release
- Optionally pushes to the remote repository

### Usage

#### Using the script directly:

```bash
# Bump patch version (0.1.0 -> 0.1.1)
python scripts/bump_version.py patch

# Bump minor version (0.1.0 -> 0.2.0)
python scripts/bump_version.py minor

# Bump major version (0.1.0 -> 1.0.0)
python scripts/bump_version.py major

# Bump without creating a commit
python scripts/bump_version.py patch --no-commit

# Bump without creating a tag
python scripts/bump_version.py patch --no-tag

# Bump without pushing to remote
python scripts/bump_version.py patch --no-push

# Combine options
python scripts/bump_version.py patch --no-commit --no-tag --no-push
```

#### Using the Makefile:

```bash
# Bump patch version
make bump-version TYPE=patch

# Bump minor version
make bump-version TYPE=minor

# Bump major version
make bump-version TYPE=major

# Bump without committing
make bump-version TYPE=patch NO_COMMIT=1

# Bump without tagging
make bump-version TYPE=patch NO_TAG=1

# Bump without pushing
make bump-version TYPE=patch NO_PUSH=1
```

### Workflow

1. **Update CHANGELOG.md**: Make sure your `[Unreleased]` section in `CHANGELOG.md` is up to date with all changes.

2. **Bump the version**:
   ```bash
   python scripts/bump_version.py patch
   ```
   This will:
   - Update version in `pyproject.toml` and `hp12c/__init__.py`
   - Move `[Unreleased]` section to a versioned section in `CHANGELOG.md`
   - Create a git commit
   - Create a git tag (e.g., `v0.1.1`)
   - Push to remote (which triggers the GitHub Actions release workflow)

3. **GitHub Actions**: When you push the tag, the `.github/workflows/release.yml` workflow will:
   - Build the application for macOS, Windows, and Linux
   - Create a GitHub release
   - Upload the build artifacts

### Requirements

- Python 3.10+
- Git
- All changes should be committed before bumping (except the version changes themselves)

### Notes

- The script follows [Semantic Versioning](https://semver.org/)
- Tags are created in the format `v<version>` (e.g., `v0.1.1`)
- The script will fail if there are uncommitted changes (except for the version files)
- Make sure your `CHANGELOG.md` follows the [Keep a Changelog](https://keepachangelog.com/) format
