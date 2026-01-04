"""
History view window for Tkinter.
Shows instruction history with step and stack information.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
from hp12c.calculator.calculator import Calculator
from hp12c.calculator.key import Key


class HistoryViewWindow:
    """Window showing instruction history."""

    def __init__(self, parent, calculator: Optional[Calculator], main_window=None):
        """Initialize history view window.

        Args:
            parent: Parent window
            calculator: Calculator instance to read history from
            main_window: Main window instance (to notify on close and for auto-refresh)
        """
        self._parent = parent
        self._calculator = calculator
        self._main_window = main_window
        self._window = None
        self._last_history_size = 0
        self._build()

    def _build(self):
        """Build the history view window."""
        self._window = tk.Toplevel(self._parent)
        self._window.title("Instruction History")
        self._window.geometry("800x600")
        self._window.resizable(True, True)

        # Create main frame with scrollbar
        main_frame = ttk.Frame(self._window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create treeview for history
        columns = ("index", "modifier", "key", "complement", "stack_x")
        self._tree = ttk.Treeview(
            main_frame,
            columns=columns,
            show="headings",
            height=25,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self._tree.yview)

        # Configure column headings
        self._tree.heading("index", text="#")
        self._tree.heading("modifier", text="Modifier")
        self._tree.heading("key", text="Key")
        self._tree.heading("complement", text="Complement")
        self._tree.heading("stack_x", text="Stack X")

        # Configure column widths
        self._tree.column("index", width=50, anchor=tk.CENTER)
        self._tree.column("modifier", width=150, anchor=tk.W)
        self._tree.column("key", width=150, anchor=tk.W)
        self._tree.column("complement", width=100, anchor=tk.CENTER)
        self._tree.column("stack_x", width=200, anchor=tk.E)

        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Button frame
        button_frame = ttk.Frame(self._window)
        button_frame.pack(fill=tk.X, padx=5, pady=5)

        refresh_btn = ttk.Button(button_frame, text="Refresh", command=self.update)
        refresh_btn.pack(side=tk.RIGHT, padx=5)

        clear_btn = ttk.Button(button_frame, text="Clear", command=self._on_clear)
        clear_btn.pack(side=tk.RIGHT, padx=5)

        close_btn = ttk.Button(button_frame, text="Close", command=self._on_close)
        close_btn.pack(side=tk.RIGHT, padx=5)

        # Handle window close
        self._window.protocol("WM_DELETE_WINDOW", self._on_close)

        # Initial update
        self.update()

    def _get_modifier_operation_name(self, modifier_code: int, key_code: int) -> Optional[str]:
        """Get the actual operation name when a modifier is used.

        Returns the operation name if modifier+key creates a specific operation,
        otherwise returns None to use the default key name.
        """
        if modifier_code == -1:
            return None

        # Map of (modifier_code, key_code) -> operation_name
        modifier_operations = {
            # F modifier operations
            (Key.KEY_F.get_code(), Key.KEY_N.get_code()): "Amortization",
            (Key.KEY_F.get_code(), Key.KEY_I.get_code()): "Simple Interest",
            (Key.KEY_F.get_code(), Key.KEY_PV.get_code()): "NPV",
            (Key.KEY_F.get_code(), Key.KEY_PMT.get_code()): "Round",
            (Key.KEY_F.get_code(), Key.KEY_FV.get_code()): "IRR",
            (Key.KEY_F.get_code(), Key.KEY_POW.get_code()): "Bond Price",
            (Key.KEY_F.get_code(), Key.KEY_SST.get_code()): "F-SST",
            (Key.KEY_F.get_code(), Key.KEY_CLX.get_code()): "Clear All",
            # F modifier with digits (precision)
            (Key.KEY_F.get_code(), Key.KEY_0.get_code()): "Fix 0",
            (Key.KEY_F.get_code(), Key.KEY_1.get_code()): "Fix 1",
            (Key.KEY_F.get_code(), Key.KEY_2.get_code()): "Fix 2",
            (Key.KEY_F.get_code(), Key.KEY_3.get_code()): "Fix 3",
            (Key.KEY_F.get_code(), Key.KEY_4.get_code()): "Fix 4",
            (Key.KEY_F.get_code(), Key.KEY_5.get_code()): "Fix 5",
            (Key.KEY_F.get_code(), Key.KEY_6.get_code()): "Fix 6",
            (Key.KEY_F.get_code(), Key.KEY_7.get_code()): "Fix 7",
            (Key.KEY_F.get_code(), Key.KEY_8.get_code()): "Fix 8",
            (Key.KEY_F.get_code(), Key.KEY_9.get_code()): "Fix 9",

            # G modifier operations
            (Key.KEY_G.get_code(), Key.KEY_N.get_code()): "N×12",
            (Key.KEY_G.get_code(), Key.KEY_I.get_code()): "I÷12",
            (Key.KEY_G.get_code(), Key.KEY_PV.get_code()): "Mem0",
            (Key.KEY_G.get_code(), Key.KEY_PMT.get_code()): "Σ+",
            (Key.KEY_G.get_code(), Key.KEY_FV.get_code()): "Mem×",
            (Key.KEY_G.get_code(), Key.KEY_CHS.get_code()): "ΔDYS",
            (Key.KEY_G.get_code(), Key.KEY_POW.get_code()): "x²",
            (Key.KEY_G.get_code(), Key.KEY_0.get_code()): "Mean",
            (Key.KEY_G.get_code(), Key.KEY_1.get_code()): "ŷ,r",
            (Key.KEY_G.get_code(), Key.KEY_2.get_code()): "ŷ,r",
            (Key.KEY_G.get_code(), Key.KEY_3.get_code()): "n!",
            (Key.KEY_G.get_code(), Key.KEY_4.get_code()): "DMY",
            (Key.KEY_G.get_code(), Key.KEY_5.get_code()): "MDY",
            (Key.KEY_G.get_code(), Key.KEY_6.get_code()): "x̄w",
            (Key.KEY_G.get_code(), Key.KEY_7.get_code()): "BEG",
            (Key.KEY_G.get_code(), Key.KEY_8.get_code()): "END",
            (Key.KEY_G.get_code(), Key.KEY_DOT.get_code()): "s",
            (Key.KEY_G.get_code(), Key.KEY_SST.get_code()): "BST",
            (Key.KEY_G.get_code(), Key.KEY_ROLL.get_code()): "GTO",
            (Key.KEY_G.get_code(), Key.KEY_ENTER.get_code()): "LastX",
        }

        return modifier_operations.get((modifier_code, key_code))

    def _format_key_name(self, code: int) -> str:
        """Format key code to readable name."""
        if code == -1:
            return ""
        key = Key.get_key(code)
        if key == Key.KEY_NULL:
            return f"Code {code}"
        # Remove KEY_ prefix and format nicely
        name = key.name.replace("KEY_", "")
        # Format some common keys
        name_map = {
            "DIV": "/",
            "MUL": "*",
            "SUB": "-",
            "SUM": "+",
            "POW": "y^x",
            "RECIPROCAL": "1/x",
            "PERC_TOT": "%T",
            "PERC_DELTA": "Δ%",
            "PERC": "%",
            "ROLL": "R↓",
            "XY": "x↔y",
            "CLX": "CLX",
            "ENTER": "ENTER",
            "TOT": "Σ+",
        }
        return name_map.get(name, name)

    def _is_number_entry(self, step) -> bool:
        """Check if this instruction represents a number entry."""
        # Number entries have KEY_NULL (-1) as key, no modifier, no complement
        return (step.get_key() == Key.KEY_NULL.get_code() and
                step.get_modifier() == -1 and
                step.get_complement() == -1)

    def update(self):
        """Update history display from calculator."""
        if not self._calculator:
            return

        # Get history
        history = self._calculator.get_operation_history()
        if not history:
            return

        # Check if history has changed
        current_size = history.get_size()
        has_new_entries = False

        # Count non-None entries
        non_none_count = 0
        for i in range(current_size):
            instr = history.get(i)
            if instr is not None:
                non_none_count += 1

        if non_none_count != self._last_history_size:
            has_new_entries = True
            self._last_history_size = non_none_count

        # Clear existing items
        for item in self._tree.get_children():
            self._tree.delete(item)

        # Add history entries (most recent first, index 0 is newest)
        # Count valid entries first to get proper numbering
        entry_count = 0
        for i in range(current_size):
            instr = history.get(i)
            if instr is not None:
                entry_count += 1

        # Now insert entries, newest first (index 0 is newest)
        display_index = 0
        for i in range(current_size):
            instr = history.get(i)
            if instr is not None:
                step = instr.get_step()
                stack = instr.get_stack()

                # Check if this is a number entry
                if self._is_number_entry(step):
                    # For number entries, show the number value instead of "ENTER"
                    stack_x = str(stack.get(0)) if stack else ""
                    key_name = stack_x  # Show the number as the "key"
                    modifier_name = ""
                    complement = ""
                else:
                    # Get modifier and key codes
                    modifier_code = step.get_modifier()
                    key_code = step.get_key()
                    complement_code = step.get_complement()

                    # Format modifier and key
                    modifier_name = self._format_key_name(modifier_code)
                    key_name = self._format_key_name(key_code)

                    # Check if this modifier+key combination has a specific operation name
                    operation_name = self._get_modifier_operation_name(modifier_code, key_code)

                    if operation_name:
                        # Show the operation name in the complement column
                        complement = operation_name
                    else:
                        # Show complement code if it's not -1
                        complement = str(complement_code) if complement_code != -1 else ""

                    stack_x = str(stack.get(0)) if stack else ""

                # Insert at the beginning to show newest first (index 0 is newest)
                # Display index shows position in history (0 = most recent)
                self._tree.insert(
                    "",
                    tk.END,
                    values=(
                        display_index,
                        modifier_name,
                        key_name,
                        complement if complement != -1 else "",
                        stack_x
                    )
                )
                display_index += 1

        # Auto-scroll to top (newest entry)
        if has_new_entries and self._tree.get_children():
            # Scroll to first item
            first_item = self._tree.get_children()[0]
            self._tree.see(first_item)
            # Select first item to highlight it
            self._tree.selection_set(first_item)

    def _on_clear(self):
        """Clear history."""
        if self._calculator:
            history = self._calculator.get_operation_history()
            if history:
                history.clear()
                self.update()

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
            self._main_window._history_view_window = None
        if self._window:
            self._window.destroy()

    def destroy(self):
        """Destroy window."""
        self._on_close()
