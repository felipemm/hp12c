"""
Main entry point for HP12C calculator.
Ported from Java FinanxApp.java.
"""

import sys

from hp12c.calculator.controller import Controller
from hp12c.persistence.config_dao import ConfigurationDAO
from hp12c.utils.logger import get_logger, setup_logging


def main():
    """Main entry point."""
    # Set up logging
    setup_logging()
    logger = get_logger(__name__)

    # Load config first to check which UI framework to use
    cfg_dao = ConfigurationDAO()
    cfg = cfg_dao.get_configuration()
    ui_framework = cfg.get_ui_framework() if cfg else "tkinter"

    # Only initialize QApplication if PyQt5 is explicitly requested
    # This avoids compatibility issues on newer macOS versions
    app = None
    if ui_framework == "pyqt5":
        try:
            from PyQt5.QtWidgets import QApplication

            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
                logger.info("QApplication initialized for PyQt5")
        except Exception as e:
            # Catch all exceptions (including macOS version errors)
            logger.warning(f"PyQt5 not available or incompatible ({e}), will use Tkinter")
            ui_framework = "tkinter"
            if cfg:
                cfg.set_ui_framework("tkinter")

    # Now create controller (it will use the appropriate framework)
    controller = Controller()
    window = controller.get_window()

    if window:
        frame = window.get_frame()

        # Check if it's a PyQt5 window (QMainWindow) or Tkinter (tk.Tk)
        frame_type = type(frame).__name__

        if frame_type == "QMainWindow":
            # PyQt5: Ensure QApplication exists
            if app is None:
                try:
                    from PyQt5.QtWidgets import QApplication

                    app = QApplication.instance()
                    if app is None:
                        app = QApplication(sys.argv)
                except Exception as e:
                    logger.error(f"Error initializing QApplication: {e}")
                    sys.exit(1)

            window.show()
            sys.exit(app.exec_())
        else:
            # Tkinter: Use mainloop
            frame.mainloop()


if __name__ == "__main__":
    main()
