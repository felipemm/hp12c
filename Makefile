.PHONY: help build build-macos build-windows build-linux clean install distclean run install-deps

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
	@echo "  make clean        - Remove build artifacts"
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

# macOS: Create .app bundle
# Note: We clean dist directory completely to avoid PyQt5 framework symlink conflicts
build-macos: install-deps
	@echo "Cleaning previous build artifacts (required for macOS to avoid symlink conflicts)..."
	@echo "Removing entire dist and build directories to avoid symlink conflicts..."
	@rm -rf "$(DIST_DIR)" "$(BUILD_DIR)/$(APP_NAME)" "$(SPEC_FILE)"
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
	@echo "Building $(APP_NAME) macOS application bundle..."
	$(PYINSTALLER) \
		--name=$(APP_NAME) \
		--windowed \
		--clean \
		--noconfirm \
		--icon=$(ICON_PATH) \
		--osx-bundle-identifier=com.hp12c.emulator \
		$(COMMON_ARGS) \
		$(MAIN_SCRIPT)
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
ifeq ($(USE_UV),true)
	uv run pytest --cov=hp12c --cov-report=html --cov-report=term tests/
else
	$(PYTHON) -m pytest --cov=hp12c --cov-report=html --cov-report=term tests/
endif
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
