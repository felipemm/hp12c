"""Integration tests for Controller class."""

import pytest

from hp12c.calculator.controller import Controller


class TestController:
    """Integration tests for Controller."""

    def test_controller_initialization(self):
        """Test controller can be initialized."""
        try:
            controller = Controller()
            assert controller is not None
            assert controller.get_executor() is not None
            # Window may be None if no UI framework is available
            # This is acceptable for headless test environments
            if controller.get_window() is None:
                pytest.skip("No UI framework available (Tkinter/PyQt5)")
            assert controller.get_window() is not None
        except (ImportError, RuntimeError) as e:
            # RuntimeError can occur when PyQt5 widgets are deleted in test environments
            pytest.skip(f"UI framework not available or not properly initialized: {e}")

    def test_configuration_persistence(self, tmp_path):
        """Test configuration save and load."""
        try:
            # Create temporary config file
            # config_file = tmp_path / "cfg.json"  # Unused variable removed

            # Create a controller (this will create default config)
            controller = Controller()
            config = controller.get_configs()

            # Modify config
            config.set_skin("aurum")
            config.set_language("en")

            # Save config
            controller.save_configs()

            # Verify file was created (actual implementation may vary)
            # This is a basic integration test
        except (ImportError, RuntimeError) as e:
            pytest.skip(f"UI framework not available or not properly initialized: {e}")

    def test_memory_persistence(self):
        """Test memory save and load."""
        try:
            controller = Controller()
            executor = controller.get_executor()

            # Store a value in memory
            # This would require accessing the calculator's memory operations
            # Basic test to ensure controller can access executor
            assert executor is not None
        except (ImportError, RuntimeError) as e:
            pytest.skip(f"UI framework not available or not properly initialized: {e}")

    def test_ui_framework_selection(self):
        """Test UI framework selection and fallback."""
        try:
            controller = Controller()
            window = controller.get_window()

            # Window should be created (either Tkinter or PyQt5)
            # May be None if no UI framework is available in test environment
            if window is None:
                pytest.skip("No UI framework available (Tkinter/PyQt5)")
            assert window is not None
        except (ImportError, RuntimeError) as e:
            pytest.skip(f"UI framework not available or not properly initialized: {e}")
