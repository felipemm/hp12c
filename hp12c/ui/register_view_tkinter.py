"""
Register view window for Tkinter.
Shows all calculator registers (Stack, Finance, General Memory).
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from hp12c.calculator.calculator import Calculator


class RegisterViewWindow:
    """Window showing all calculator registers."""

    def __init__(self, parent, calculator: Optional[Calculator], main_window=None):
        """Initialize register view window.

        Args:
            parent: Parent window
            calculator: Calculator instance to read registers from
            main_window: Main window instance (to notify on close)
        """
        self._parent = parent
        self._calculator = calculator
        self._main_window = main_window
        self._window = None
        self._build()

    def _build(self):
        """Build the register view window."""
        self._window = tk.Toplevel(self._parent)
        self._window.title("Registers View")
        self._window.geometry("500x600")
        self._window.resizable(True, True)

        # Create notebook for tabs
        notebook = ttk.Notebook(self._window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Stack registers tab
        stack_frame = ttk.Frame(notebook)
        notebook.add(stack_frame, text="Stack Registers")
        self._build_stack_tab(stack_frame)

        # Finance registers tab
        finance_frame = ttk.Frame(notebook)
        notebook.add(finance_frame, text="Finance Registers")
        self._build_finance_tab(finance_frame)

        # General memory tab
        memory_frame = ttk.Frame(notebook)
        notebook.add(memory_frame, text="General Memory")
        self._build_memory_tab(memory_frame)

        # Display tab
        display_frame = ttk.Frame(notebook)
        notebook.add(display_frame, text="Display")
        self._build_display_tab(display_frame)

        # Update button
        button_frame = ttk.Frame(self._window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        update_btn = ttk.Button(button_frame, text="Refresh", command=self.update)
        update_btn.pack(side=tk.RIGHT, padx=5)
        close_btn = ttk.Button(button_frame, text="Close", command=self._on_close)
        close_btn.pack(side=tk.RIGHT, padx=5)

        # Handle window close
        self._window.protocol("WM_DELETE_WINDOW", self._on_close)

        # Initial update
        self.update()

    def _build_stack_tab(self, parent):
        """Build stack registers tab."""
        # Create treeview
        tree = ttk.Treeview(parent, columns=("value",), show="tree headings", height=10)
        tree.heading("#0", text="Register")
        tree.heading("value", text="Value")
        tree.column("#0", width=150)
        tree.column("value", width=300)
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._stack_tree = tree

    def _build_finance_tab(self, parent):
        """Build finance registers tab."""
        # Create treeview
        tree = ttk.Treeview(parent, columns=("value",), show="tree headings", height=10)
        tree.heading("#0", text="Register")
        tree.heading("value", text="Value")
        tree.column("#0", width=150)
        tree.column("value", width=300)
        tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self._finance_tree = tree

    def _build_memory_tab(self, parent):
        """Build general memory tab."""
        # Create frame with scrollbar
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create treeview
        tree = ttk.Treeview(frame, columns=("value", "times"), show="tree headings", height=15,
                           yscrollcommand=scrollbar.set)
        tree.heading("#0", text="Register")
        tree.heading("value", text="Value")
        tree.heading("times", text="Times")
        tree.column("#0", width=100)
        tree.column("value", width=200)
        tree.column("times", width=100)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=tree.yview)
        self._memory_tree = tree

    def _build_display_tab(self, parent):
        """Build display tab."""
        # Display info
        info_frame = ttk.LabelFrame(parent, text="Display Information", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._display_labels = {}
        labels = [
            ("Current Value", "value"),
            ("Status", "status"),
            ("Mode", "mode"),
            ("Precision", "precision"),
            ("Comma Separator", "comma"),
        ]

        for i, (label_text, key) in enumerate(labels):
            ttk.Label(info_frame, text=f"{label_text}:").grid(row=i, column=0, sticky=tk.W, padx=5, pady=2)
            value_label = ttk.Label(info_frame, text="", font=("Courier", 10))
            value_label.grid(row=i, column=1, sticky=tk.W, padx=5, pady=2)
            self._display_labels[key] = value_label

    def update(self):
        """Update register values from calculator."""
        if not self._calculator:
            return

        # Update stack registers
        if hasattr(self, '_stack_tree'):
            # Clear existing items
            for item in self._stack_tree.get_children():
                self._stack_tree.delete(item)

            stack = self._calculator.get_stack()
            if stack:
                stack_array = stack.get_array()
                register_names = ["RegX", "RegY", "RegZ", "RegT"]
                for i, name in enumerate(register_names):
                    if i < len(stack_array):
                        value_str = str(stack_array[i])
                        self._stack_tree.insert("", tk.END, text=name, values=(value_str,))

                # LastX
                last_x = stack.get_last_top()
                self._stack_tree.insert("", tk.END, text="LastX", values=(str(last_x),))

        # Update finance registers
        if hasattr(self, '_finance_tree'):
            # Clear existing items
            for item in self._finance_tree.get_children():
                self._finance_tree.delete(item)

            finance = self._calculator.get_finance_memory()
            if finance:
                registers = [
                    ("RegN", finance.get_n()),
                    ("RegI", finance.get_i()),
                    ("RegPV", finance.get_pv()),
                    ("RegPMT", finance.get_pmt()),
                    ("RegFV", finance.get_fv()),
                ]
                for name, value in registers:
                    value_str = str(value)
                    self._finance_tree.insert("", tk.END, text=name, values=(value_str,))

        # Update general memory
        if hasattr(self, '_memory_tree'):
            # Clear existing items
            for item in self._memory_tree.get_children():
                self._memory_tree.delete(item)

            memory = self._calculator.get_general_memory()
            if memory:
                size = memory.get_size()
                for i in range(size):
                    value, times = memory.get_with_times(i)
                    self._memory_tree.insert("", tk.END, text=f"Mem{i}", values=(str(value), str(times)))

        # Update display
        if hasattr(self, '_display_labels'):
            display = self._calculator.get_display()
            if display:
                self._display_labels["value"].config(text=display.get_string())
                status_names = {0: "Ready", 1: "Input", 2: "Output", 3: "Output2"}
                status = display.get_status()
                self._display_labels["status"].config(text=status_names.get(status, str(status)))
                mode_names = {0: "Normal", 1: "Exponential", 2: "Program"}
                mode = display.get_mode()
                self._display_labels["mode"].config(text=mode_names.get(mode, str(mode)))
                self._display_labels["precision"].config(text=str(display.get_precision()))
                self._display_labels["comma"].config(text="Comma (,)" if display.get_comma() else "Dot (.)")

    def show(self):
        """Show window."""
        if self._window:
            self._window.deiconify()
            self._window.lift()

    def hide(self):
        """Hide window."""
        if self._window:
            self._window.withdraw()

    def _on_close(self):
        """Handle window close."""
        if self._main_window:
            self._main_window._register_view_window = None
        if self._window:
            self._window.destroy()

    def destroy(self):
        """Destroy window."""
        self._on_close()
