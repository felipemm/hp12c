"""
Main entry point for HP12C calculator.
Ported from Java FinanxApp.java.
"""

import sys
from hp12c_python_java_port.calculator.controller import Controller
from hp12c_python_java_port.persistence.config_dao import ConfigurationDAO


def main():
    """Main entry point."""
    # Load config first to check which UI framework to use
    # This allows us to initialize QApplication early if needed
    cfg_dao = ConfigurationDAO()
    cfg = cfg_dao.get_configuration()
    ui_framework = cfg.get_ui_framework() if cfg else "tkinter"

    # Initialize QApplication BEFORE creating Controller if PyQt5 is requested
    app = None
    if ui_framework == "pyqt5":
        try:
            from PyQt5.QtWidgets import QApplication
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            print("QApplication initialized for PyQt5")
        except ImportError:
            print("PyQt5 not available, falling back to Tkinter")
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

        if frame_type == 'QMainWindow':
            # PyQt5: Ensure QApplication exists
            if app is None:
                from PyQt5.QtWidgets import QApplication
                app = QApplication.instance()
                if app is None:
                    app = QApplication(sys.argv)

            window.show()
            sys.exit(app.exec_())
        else:
            # Tkinter: Use mainloop
            frame.mainloop()


if __name__ == "__main__":
    main()
