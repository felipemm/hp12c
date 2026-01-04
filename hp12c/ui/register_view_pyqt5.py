"""
Register view window for PyQt5.
Shows all calculator registers (Stack, Finance, General Memory).
"""


from PyQt5.QtWidgets import (
    QDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
)

from hp12c.calculator.calculator import Calculator


class RegisterViewWindow(QDialog):
    """Window showing all calculator registers."""

    def __init__(self, parent, calculator: Calculator | None, main_window=None):
        """Initialize register view window.

        Args:
            parent: Parent window
            calculator: Calculator instance to read registers from
            main_window: Main window instance (to notify on close)
        """
        super().__init__(parent)
        self._calculator = calculator
        self._main_window = main_window
        self._build()

    def _build(self):
        """Build the register view window."""
        self.setWindowTitle("Registers View")
        self.setMinimumSize(500, 600)
        self.resize(500, 600)

        layout = QVBoxLayout(self)

        # Create tab widget
        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Stack registers tab
        stack_widget = QTreeWidget()
        stack_widget.setHeaderLabels(["Register", "Value"])
        stack_widget.setColumnWidth(0, 150)
        stack_widget.setColumnWidth(1, 300)
        tabs.addTab(stack_widget, "Stack Registers")
        self._stack_tree = stack_widget

        # Finance registers tab
        finance_widget = QTreeWidget()
        finance_widget.setHeaderLabels(["Register", "Value"])
        finance_widget.setColumnWidth(0, 150)
        finance_widget.setColumnWidth(1, 300)
        tabs.addTab(finance_widget, "Finance Registers")
        self._finance_tree = finance_widget

        # General memory tab
        memory_widget = QTreeWidget()
        memory_widget.setHeaderLabels(["Register", "Value", "Times"])
        memory_widget.setColumnWidth(0, 100)
        memory_widget.setColumnWidth(1, 200)
        memory_widget.setColumnWidth(2, 100)
        tabs.addTab(memory_widget, "General Memory")
        self._memory_tree = memory_widget

        # Display tab
        display_widget = QGroupBox("Display Information")
        display_layout = QGridLayout()
        display_widget.setLayout(display_layout)
        tabs.addTab(display_widget, "Display")
        self._display_labels = {}

        labels = [
            ("Current Value", "value"),
            ("Status", "status"),
            ("Mode", "mode"),
            ("Precision", "precision"),
            ("Comma Separator", "comma"),
        ]

        for i, (label_text, key) in enumerate(labels):
            display_layout.addWidget(QLabel(f"{label_text}:"), i, 0)
            value_label = QLabel("")
            value_label.setFont(QLabel().font())
            display_layout.addWidget(value_label, i, 1)
            self._display_labels[key] = value_label

        # Buttons
        button_layout = QHBoxLayout()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.update)
        button_layout.addWidget(refresh_btn)
        button_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self._on_close)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

        # Initial update
        self.update()

    def update(self) -> None:
        """Update register values from calculator."""
        if not self._calculator:
            return

        # Update stack registers
        stack = self._calculator.get_stack()
        if stack:
            self._stack_tree.clear()
            stack_array = stack.get_array()
            register_names = ["RegX", "RegY", "RegZ", "RegT"]
            for i, name in enumerate(register_names):
                if i < len(stack_array):
                    value_str = str(stack_array[i])
                    item = QTreeWidgetItem(self._stack_tree)
                    item.setText(0, name)
                    item.setText(1, value_str)

            # LastX
            last_x = stack.get_last_top()
            item = QTreeWidgetItem(self._stack_tree)
            item.setText(0, "LastX")
            item.setText(1, str(last_x))

        # Update finance registers
        finance = self._calculator.get_finance_memory()
        if finance:
            self._finance_tree.clear()
            registers = [
                ("RegN", finance.get_n()),
                ("RegI", finance.get_i()),
                ("RegPV", finance.get_pv()),
                ("RegPMT", finance.get_pmt()),
                ("RegFV", finance.get_fv()),
            ]
            for name, value in registers:
                item = QTreeWidgetItem(self._finance_tree)
                item.setText(0, name)
                item.setText(1, str(value))

        # Update general memory
        memory = self._calculator.get_general_memory()
        if memory:
            self._memory_tree.clear()
            size = memory.get_size()
            for i in range(size):
                value, times = memory.get_with_times(i)
                item = QTreeWidgetItem(self._memory_tree)
                item.setText(0, f"Mem{i}")
                item.setText(1, str(value))
                item.setText(2, str(times))

        # Update display
        display = self._calculator.get_display()
        if display:
            self._display_labels["value"].setText(display.get_string())
            status_names = {0: "Ready", 1: "Input", 2: "Output", 3: "Output2"}
            status = display.get_status()
            self._display_labels["status"].setText(status_names.get(status, str(status)))
            mode_names = {0: "Normal", 1: "Exponential", 2: "Program"}
            mode = display.get_mode()
            self._display_labels["mode"].setText(mode_names.get(mode, str(mode)))
            self._display_labels["precision"].setText(str(display.get_precision()))
            self._display_labels["comma"].setText("Comma (,)" if display.get_comma() else "Dot (.)")

    def _on_close(self):
        """Handle window close."""
        if self._main_window:
            self._main_window._register_view_window = None
        self.accept()
