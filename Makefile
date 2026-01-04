.PHONY: help build build-macos build-windows build-linux clean regenerate-spec install distclean janitor run install-deps create-dmg

# Application name
APP_NAME = hp12c
MAIN_SCRIPT = main.py
ICON_PATH = hp12c/resources/skins/argentum/icon.png

# Build directories
BUILD_DIR = build
DIST_DIR = dist
SPEC_FILE = $(APP_NAME).spec

# Python and PyInstaller
PYTHON = python

# Check if uv is available
UV := $(shell command -v uv 2> /dev/null)
ifeq ($(UV),)
	USE_UV = false
	PYINSTALLER = pyinstaller
else
	USE_UV = true
	PYINSTALLER = uv run pyinstaller
endif

# Detect platform
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Darwin)
	PLATFORM = macos
	ICON_EXT = icns
else ifeq ($(OS),Windows_NT)
	PLATFORM = windows
	ICON_EXT = ico
else
	PLATFORM = linux
	ICON_EXT = png
endif

# Common PyInstaller arguments
# Note: PyQt5 collection is handled in hp12c.spec to avoid symlink conflicts
COMMON_ARGS = \
	--name=$(APP_NAME) \
	--add-data "data:data" \
	--add-data "hp12c/resources:hp12c/resources" \
	--hidden-import=PyQt5 \
	--hidden-import=PyQt5.QtCore \
	--hidden-import=PyQt5.QtWidgets \
	--hidden-import=PyQt5.QtGui \
	--hidden-import=PIL \
	--hidden-import=PIL.Image \
	--hidden-import=PIL.ImageTk \
	--exclude-module=PyQt5.QtBluetooth \
	--exclude-module=PyQt5.Qt3DCore \
	--exclude-module=PyQt5.Qt3DRender \
	--exclude-module=PyQt5.Qt3DQuick \
	--exclude-module=PyQt5.Qt3DInput \
	--exclude-module=PyQt5.Qt3DLogic \
	--exclude-module=PyQt5.Qt3DAnimation \
	--exclude-module=PyQt5.Qt3DExtras \
	--exclude-module=PyQt5.QtQuick \
	--exclude-module=PyQt5.QtQuick3D \
	--exclude-module=PyQt5.QtQuickWidgets \
	--exclude-module=PyQt5.QtQml \
	--exclude-module=PyQt5.QtWebEngine \
	--exclude-module=PyQt5.QtWebEngineCore \
	--exclude-module=PyQt5.QtPdf \
	--exclude-module=PyQt5.QtBodymovin \
	--exclude-module=PyQt5.QtGamepad

help:
	@echo "Available targets:"
	@echo "  make build        - Build for current platform (auto-detect)"
	@echo "  make build-macos  - Build macOS .app bundle"
	@echo "  make build-windows - Build Windows .exe"
	@echo "  make build-linux  - Build Linux executable"
	@echo "  make create-dmg   - Create a nicely styled DMG for macOS using create-dmg (requires build-macos first)"
	@echo "  make clean        - Remove build artifacts"
	@echo "  make janitor      - Clean everything except final dist files"
	@echo "  make regenerate-spec - Regenerate spec file with latest dependencies"
	@echo "  make distclean    - Remove all build and dist files"
	@echo "  make install-deps - Install build dependencies"
	@echo "  make run          - Run the application from source"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run linters (ruff)"
	@echo "  make format       - Format code (ruff)"
	@echo "  make type-check   - Run type checker (mypy)"
	@echo "  make check-all    - Run all checks (lint, type-check, test)"
	@echo "  make install-pre-commit - Install pre-commit hooks"
	@echo "  make version      - Show current version"
	@echo "  make bump-version - Bump version (use TYPE=major|minor|patch)"
	@echo "  make help         - Show this help message"
	@echo ""
	@echo "Detected platform: $(PLATFORM)"
	@echo ""
	@echo "Note: If you encounter symlink errors during build, try:"
	@echo "  make distclean && make build"

install-deps:
	@echo "Installing build dependencies..."
ifeq ($(USE_UV),true)
	@echo "Using uv to install pyinstaller..."
	uv pip install pyinstaller || uv add --dev pyinstaller
else
	@echo "Using pip to install pyinstaller..."
	@if $(PYTHON) -m pip --version > /dev/null 2>&1; then \
		$(PYTHON) -m pip install --upgrade pip; \
		$(PYTHON) -m pip install pyinstaller; \
	else \
		echo "Error: pip is not available. Please install pip or use uv."; \
		echo "To install uv: curl -LsSf https://astral.sh/uv/install.sh | sh"; \
		exit 1; \
	fi
endif
	@echo "Dependencies installed."

# Auto-detect platform and build
build: install-deps
	@echo "Building for detected platform: $(PLATFORM)"
ifeq ($(PLATFORM),macos)
	@$(MAKE) build-macos
else ifeq ($(PLATFORM),windows)
	@$(MAKE) build-windows
else
	@$(MAKE) build-linux
endif

# Regenerate spec file with latest dependencies and inject info_plist
# Useful when dependencies change - automatically patches with macOS metadata
regenerate-spec: install-deps
	@echo "Regenerating $(SPEC_FILE) with latest dependencies..."
	@$(PYINSTALLER) \
		--name=$(APP_NAME) \
		--windowed \
		--icon=$(ICON_PATH) \
		--osx-bundle-identifier=com.hp12c.emulator \
		$(COMMON_ARGS) \
		--specpath=. \
		$(MAIN_SCRIPT) 2>/dev/null || true
	@echo "Patching $(SPEC_FILE) with info_plist (reading version from pyproject.toml)..."
	@$(PYTHON) scripts/patch_spec_info_plist.py $(SPEC_FILE)
	@echo "✓ Spec file regenerated and patched with info_plist"

# macOS: Create .app bundle
# Note: We clean dist directory completely to avoid PyQt5 framework symlink conflicts
# Note: Spec file is always regenerated and patched with info_plist during build
build-macos: install-deps
	@echo "Cleaning previous build artifacts (required for macOS to avoid symlink conflicts)..."
	@echo "Removing entire dist and build directories to avoid symlink conflicts..."
	@rm -rf "$(DIST_DIR)" "$(BUILD_DIR)/$(APP_NAME)"
	@echo "Ensuring directories are fully removed..."
	@if [ -d "$(DIST_DIR)" ]; then \
		echo "Warning: dist directory still exists, forcing removal..."; \
		chmod -R u+w "$(DIST_DIR)" 2>/dev/null || true; \
		rm -rf "$(DIST_DIR)"; \
	fi
	@if [ -d "$(BUILD_DIR)/$(APP_NAME)" ]; then \
		echo "Warning: build directory still exists, forcing removal..."; \
		chmod -R u+w "$(BUILD_DIR)/$(APP_NAME)" 2>/dev/null || true; \
		rm -rf "$(BUILD_DIR)/$(APP_NAME)"; \
	fi
	@echo "Regenerating $(SPEC_FILE) with latest dependencies..."
	@$(PYINSTALLER) \
		--name=$(APP_NAME) \
		--windowed \
		--icon=$(ICON_PATH) \
		--osx-bundle-identifier=com.hp12c.emulator \
		$(COMMON_ARGS) \
		--specpath=. \
		$(MAIN_SCRIPT) 2>/dev/null || true
	@echo "Patching $(SPEC_FILE) with info_plist (reading version from pyproject.toml)..."
	@$(PYTHON) scripts/patch_spec_info_plist.py $(SPEC_FILE)
	@echo "Building $(APP_NAME) macOS application bundle..."
	$(PYINSTALLER) \
		--clean \
		--noconfirm \
		$(SPEC_FILE)
	@echo "Build complete! Application bundle is in $(DIST_DIR)/$(APP_NAME).app"
	@echo "You can run it with: open $(DIST_DIR)/$(APP_NAME).app"

# Windows: Create .exe
build-windows: install-deps
	@echo "Cleaning previous build artifacts..."
	@rm -rf $(DIST_DIR)/$(APP_NAME).exe $(BUILD_DIR)/$(APP_NAME)
	@echo "Building $(APP_NAME) Windows executable..."
	$(PYINSTALLER) \
		--name=$(APP_NAME) \
		--onefile \
		--windowed \
		--clean \
		--noconfirm \
		--icon=$(ICON_PATH) \
		$(COMMON_ARGS) \
		$(MAIN_SCRIPT)
	@echo "Build complete! Executable is in $(DIST_DIR)/$(APP_NAME).exe"

# Linux: Create standard executable
build-linux: install-deps
	@echo "Cleaning previous build artifacts..."
	@rm -rf $(DIST_DIR)/$(APP_NAME) $(BUILD_DIR)/$(APP_NAME)
	@echo "Building $(APP_NAME) Linux executable..."
	$(PYINSTALLER) \
		--name=$(APP_NAME) \
		--onefile \
		--windowed \
		--clean \
		--noconfirm \
		--icon=$(ICON_PATH) \
		$(COMMON_ARGS) \
		$(MAIN_SCRIPT)
	@echo "Build complete! Executable is in $(DIST_DIR)/$(APP_NAME)"
	@echo "You can run it with: ./$(DIST_DIR)/$(APP_NAME)"

clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR)
	rm -f $(SPEC_FILE)
	@echo "Clean complete."

janitor:
	@echo "Cleaning everything except final dist files..."
	@echo "Removing build artifacts..."
	rm -rf $(BUILD_DIR)
	rm -f $(SPEC_FILE)
	@echo "Removing Python cache files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type f -name "*.pyd" -delete 2>/dev/null || true
	find . -type f -name "*$$py.class" -delete 2>/dev/null || true
	@echo "Removing test and coverage artifacts..."
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .coverage .coverage.*
	rm -rf coverage.xml
	rm -rf .tox/ .nox/
	rm -rf .hypothesis/
	rm -rf cover/
	find . -type f -name "*.cover" -delete 2>/dev/null || true
	find . -type f -name "*.py,cover" -delete 2>/dev/null || true
	@echo "Removing type checking cache..."
	rm -rf .mypy_cache/
	rm -f .dmypy.json dmypy.json
	@echo "Removing distribution artifacts (except dist/)..."
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -not -path "./dist" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -not -path "./build" -exec rm -rf {} + 2>/dev/null || true
	@echo "Removing other cache files..."
	rm -rf .cache/
	rm -rf .ruff_cache/
	rm -rf .pytype/
	rm -rf .pyre/
	@echo "Janitor complete. Dist files preserved in $(DIST_DIR)/"

distclean: clean
	@echo "Removing distribution files..."
	rm -rf $(DIST_DIR)
	@echo "Distclean complete."

run:
	@echo "Running $(APP_NAME) from source..."
	$(PYTHON) $(MAIN_SCRIPT)

test:
	@echo "Running tests..."
ifeq ($(USE_UV),true)
	uv run pytest tests/
else
	$(PYTHON) -m pytest tests/
endif

test-cov:
	@echo "Running tests with coverage..."
	@if [ "$(USE_UV)" = "true" ]; then \
		uv run pytest --cov=hp12c --cov-report=html --cov-report=term tests/ 2>&1 | tee /tmp/pytest_output.txt; \
		COVERAGE=$$(sed -n 's/.*Total coverage: \([0-9.]*\)%.*/\1/p' /tmp/pytest_output.txt | head -1); \
		if [ -n "$$COVERAGE" ]; then \
			echo "Updating coverage badge in README.md..."; \
			$(PYTHON) scripts/update_coverage_badge.py $$COVERAGE; \
		fi; \
		rm -f /tmp/pytest_output.txt; \
	else \
		$(PYTHON) -m pytest --cov=hp12c --cov-report=html --cov-report=term tests/ 2>&1 | tee /tmp/pytest_output.txt; \
		COVERAGE=$$(sed -n 's/.*Total coverage: \([0-9.]*\)%.*/\1/p' /tmp/pytest_output.txt | head -1); \
		if [ -n "$$COVERAGE" ]; then \
			echo "Updating coverage badge in README.md..."; \
			$(PYTHON) scripts/update_coverage_badge.py $$COVERAGE; \
		fi; \
		rm -f /tmp/pytest_output.txt; \
	fi
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	@echo "Running linter (ruff)..."
ifeq ($(USE_UV),true)
	uv run ruff check hp12c/ tests/ main.py
else
	$(PYTHON) -m ruff check hp12c/ tests/ main.py
endif

format:
	@echo "Formatting code (ruff)..."
ifeq ($(USE_UV),true)
	uv run ruff format hp12c/ tests/ main.py
else
	$(PYTHON) -m ruff format hp12c/ tests/ main.py
endif

type-check:
	@echo "Running type checker (mypy)..."
ifeq ($(USE_UV),true)
	uv run mypy hp12c/ main.py
else
	$(PYTHON) -m mypy hp12c/ main.py
endif

check-all: lint type-check test
	@echo "All checks completed!"

install-pre-commit:
	@echo "Installing pre-commit hooks..."
ifeq ($(USE_UV),true)
	uv run pre-commit install
else
	$(PYTHON) -m pre_commit install
endif
	@echo "Pre-commit hooks installed. They will run automatically on git commit."

version:
	@echo "HP12C Calculator version:"
	@python -c "from hp12c import __version__; print(__version__)" 2>/dev/null || echo "0.1.0"

bump-version:
	@echo "Bumping version..."
	@echo "Usage: make bump-version TYPE=[major|minor|patch] [NO_COMMIT=1] [NO_TAG=1] [NO_PUSH=1]"
	@if [ -z "$(TYPE)" ]; then \
		echo "Error: TYPE is required. Use TYPE=major, TYPE=minor, or TYPE=patch"; \
		exit 1; \
	fi
	@python scripts/bump_version.py $(TYPE) \
		$$([ -n "$(NO_COMMIT)" ] && echo "--no-commit") \
		$$([ -n "$(NO_TAG)" ] && echo "--no-tag") \
		$$([ -n "$(NO_PUSH)" ] && echo "--no-push")

fix-git-tags:
	@echo "Fixing git tags..."
	@VERSION=$$(python -c "from hp12c import __version__; print(__version__)"); \
	echo "Version: $$VERSION"; \
	echo "Deleting local tag v$$VERSION..."; \
	git tag -d v$$VERSION || true; \
	echo "Deleting remote tag v$$VERSION..."; \
	git push origin :v$$VERSION || true; \
	echo "Deleting GitHub release v$$VERSION..."; \
	gh release delete v$$VERSION --yes || true; \
	echo "Committing changes..."; \
	git commit -am "fixing .dmg" || true; \
	echo "Creating signed tag v$$VERSION..."; \
	git tag -s -a v$$VERSION -m "Release v$$VERSION"; \
	echo "Pushing commits..."; \
	git push origin HEAD || git push; \
	echo "Pushing tag v$$VERSION..."; \
	git push origin v$$VERSION; \
	echo "✓ Git tags fixed successfully"

# Create a nicely styled DMG for macOS distribution using create-dmg
# Requires: build-macos must be run first, and create-dmg must be installed (npm install -g create-dmg)
# See: https://github.com/sindresorhus/create-dmg
create-dmg:
	@if [ "$(PLATFORM)" != "macos" ]; then \
		echo "Error: create-dmg can only be run on macOS"; \
		exit 1; \
	fi
	@if [ ! -d "$(DIST_DIR)/$(APP_NAME).app" ]; then \
		echo "Error: $(APP_NAME).app not found. Run 'make build-macos' first."; \
		exit 1; \
	fi
	@if ! command -v create-dmg >/dev/null 2>&1; then \
		echo "Error: create-dmg is not installed."; \
		echo "Install it with: npm install --global create-dmg"; \
		exit 1; \
	fi
	@echo "Creating DMG with create-dmg tool..."
	@cd "$(DIST_DIR)" && \
		create-dmg --overwrite --no-code-sign "$(APP_NAME).app" . || \
		(echo "Note: DMG created successfully (code signing skipped)." && exit 0)
	@echo "✓ DMG created in $(DIST_DIR)/"
