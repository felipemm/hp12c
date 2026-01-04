"""
Main Calculator engine for HP12C.
Ported from Java Calculator.java (2000+ lines).
This is a comprehensive port with all key handlers.
"""

import threading

from hp12c.calculator.config import Configuration
from hp12c.calculator.exceptions import CalculatorException, Error
from hp12c.calculator.key import Key
from hp12c.hp12c_math.number import Number
from hp12c.model.display import Display
from hp12c.model.finance_memory import FinanceMemory
from hp12c.model.flags import Flags
from hp12c.model.general_memory import GeneralMemory
from hp12c.model.history import History
from hp12c.model.instruction import Instruction
from hp12c.model.program_memory import ProgramMemory
from hp12c.model.stack import Stack
from hp12c.model.step import Step
from hp12c.utils.logger import get_logger
from hp12c.utils.timer import Timer


class Calculator:
    """Main calculator engine."""

    def __init__(self):
        """Initialize calculator."""
        self._logger = get_logger(__name__)
        self._k: Key | None = None
        self._stp = Step()
        self._tmp: list[Number] | None = None
        self._controller = None
        self._flg = Flags()
        self._dsp = Display()
        self._worker: threading.Thread | None = None
        self._stk = Stack()
        self._fin = FinanceMemory()
        self._mem = GeneralMemory()
        self._prg = ProgramMemory()
        self._hst = History()
        self._cfg = Configuration()
        self._previous_display_status = (
            Display.STATUS_READY
        )  # Track previous status to detect number completion
        self.init()

    def init(self):
        """Initialize calculator components."""
        self._flg = Flags()
        self._stp = Step()
        self._hst = History()
        self._dsp = Display()
        self._stk = Stack()
        self._fin = FinanceMemory()
        self._mem = GeneralMemory()
        self._prg = ProgramMemory()
        self._cfg = Configuration()
        self._previous_display_status = Display.STATUS_READY
        # Worker will be created when needed

    # Getters and setters
    def get_controller(self):
        return self._controller

    def set_controller(self, controller):
        self._controller = controller

    def get_configs(self) -> Configuration:
        return self._cfg

    def set_configs(self, cfg: Configuration):
        self._cfg = cfg
        self.set_flags()
        self.set_display()

    def set_flags(self):
        """Set flags from configuration."""
        self.get_flags().set_begin(self._cfg.get_beg())
        self.get_flags().set_dmy(self._cfg.get_dmy())

    def set_display(self):
        """Set display from configuration."""
        if self._cfg.get_com() == 1:
            self.get_display().set_comma(True)
        else:
            self.get_display().set_comma(False)
        self.get_display().set_precision(self._cfg.get_fix())

    def get_stack(self) -> Stack:
        return self._stk

    def set_stack(self, stack: Stack):
        """Set stack."""
        self._stk = stack

    def get_finance_memory(self) -> FinanceMemory:
        return self._fin

    def set_finance_memory(self, finance_memory: FinanceMemory):
        """Set finance memory."""
        self._fin = finance_memory

    def get_general_memory(self) -> GeneralMemory:
        return self._mem

    def set_general_memory(self, general_memory: GeneralMemory):
        """Set general memory."""
        self._mem = general_memory

    def get_program_memory(self) -> ProgramMemory:
        return self._prg

    def set_program_memory(self, program_memory: ProgramMemory):
        """Set program memory."""
        self._prg = program_memory

    def get_operation_history(self) -> History:
        return self._hst

    def get_flags(self) -> Flags:
        return self._flg

    def get_display(self) -> Display:
        return self._dsp

    def set_x(self, x: Number):
        """Set X register."""
        if self._dsp.get_status() != 0:
            self._stk.put(x)
        else:
            self._stk.set(0, x)

    def get_x(self) -> Number:
        """Get X register."""
        return self._stk.top()

    def shift_up_if_output_status(self):
        """Shift stack up if output status."""
        if self._dsp.get_status() == 2 or self._dsp.get_status() == 3:
            self._stk.shift_down()

    def _update_one_way_binded_flags(self):
        """Update flags bound to other components."""
        self._stk.set_dmy(self._flg.get_dmy() == 1)
        self._fin.set_begin(self._flg.get_begin() == 1)
        self._fin.set_c(self._flg.get_c() == 1)

    def key_pressed(self, key: Key | None):
        """Handle key press."""
        self._update_one_way_binded_flags()
        if key is None:
            return
        if self._flg.get_run() == 1:
            self.stop_program()
            self._dsp.set_lock(True)
        # Key press handling (mostly no-op in Java)

    def process_key(self, key: Key):
        """Process a key press (alias for key_released for test compatibility)."""
        self.key_released(key)

    def key_released(self, key: Key | None):
        """Handle key release - main entry point."""
        if key is None:
            return
        self._k = key

        # Track previous display status and stack state before processing key
        previous_status = self._dsp.get_status()
        # Save the number being entered (from display) if we're in input mode
        # This will be used to record the number entry
        number_being_entered = None
        if previous_status == Display.STATUS_INPUT:
            # Get the number from display (it's being built there)
            number_being_entered = self._dsp.get_value()

        # Capture modifier state BEFORE the operation (flags get toggled during operation)
        modifier_before_operation = -1
        if self._flg.get_f() == 1:
            modifier_before_operation = Key.KEY_F.get_code()
        elif self._flg.get_g() == 1:
            modifier_before_operation = Key.KEY_G.get_code()

        try:
            if self._dsp.get_pause():
                t = Timer(1.0)
                t.run()
                self._dsp.set_pause(False)
            elif self._dsp.get_lock():
                self._dsp.set_lock(False)
                return

            if self._flg.get_prgm() == 1:
                self.program_input(self._k)
                return

            # Route to appropriate doKey method
            code = key.get_code()
            if code == 0:
                self.do_key_00()
            elif code == 1:
                self.do_key_01()
            elif code == 2:
                self.do_key_02()
            elif code == 3:
                self.do_key_03()
            elif code == 4:
                self.do_key_04()
            elif code == 5:
                self.do_key_05()
            elif code == 6:
                self.do_key_06()
            elif code == 7:
                self.do_key_07()
            elif code == 8:
                self.do_key_08()
            elif code == 9:
                self.do_key_09()
            elif code == 10:
                self.do_key_10()
            elif code == 11:
                self.do_key_11()
            elif code == 12:
                self.do_key_12()
            elif code == 13:
                self.do_key_13()
            elif code == 14:
                self.do_key_14()
            elif code == 15:
                self.do_key_15()
            elif code == 16:
                self.do_key_16()
            elif code == 20:
                self.do_key_20()
            elif code == 21:
                self.do_key_21()
            elif code == 22:
                self.do_key_22()
            elif code == 23:
                self.do_key_23()
            elif code == 24:
                self.do_key_24()
            elif code == 25:
                self.do_key_25()
            elif code == 26:
                self.do_key_26()
            elif code == 30:
                self.do_key_30()
            elif code == 31:
                self.do_key_31()
            elif code == 32:
                self.do_key_32()
            elif code == 33:
                self.do_key_33()
            elif code == 34:
                self.do_key_34()
            elif code == 35:
                self.do_key_35()
            elif code == 36:
                self.do_key_36()
            elif code == 40:
                self.do_key_40()
            elif code == 41:
                self.do_key_41()
            elif code == 42:
                self.do_key_42()
            elif code == 43:
                self.do_key_43()
            elif code == 44:
                self.do_key_44()
            elif code == 45:
                self.do_key_45()
            elif code == 48:
                self.do_key_48()
            elif code == 49:
                self.do_key_49()

            # Update display first to get final status
            self.update_display()

            # Check if we just completed a number entry
            # (transitioned from INPUT to OUTPUT/READY, or ENTER was pressed)
            current_status = self._dsp.get_status()
            number_completed = False

            # Number is completed if status changed from INPUT to something else
            # This happens when:
            # 1. An operation is performed after entering a number
            # 2. ENTER is pressed
            # 3. Any other key that ends input mode
            if previous_status == Display.STATUS_INPUT and current_status != Display.STATUS_INPUT:
                # Number entry was completed (status changed from INPUT)
                number_completed = True

            # Add instruction to history
            # This will handle both operations and completed number entries
            # We need to record:
            # 1. The number entry (if completed) - using the number from display
            # 2. The operation/key that was pressed - using current stack state
            self._add_to_history(
                number_completed=number_completed,
                previous_status=previous_status,
                number_being_entered=number_being_entered,
                modifier_before_operation=modifier_before_operation,
            )

            # Update previous status for next key press
            self._previous_display_status = current_status

            self.print_registers()
        except CalculatorException as e:
            self.clear_fgsr()
            self.show_error(e)
            raise
        except ZeroDivisionError as e:
            # Convert ZeroDivisionError to CalculatorException
            calc_ex = CalculatorException(Error.ERROR_MATH, str(e))
            self.clear_fgsr()
            self.show_error(calc_ex)
            raise calc_ex from e
        except Exception as e:
            print(f"Error: {e}")

    def _add_to_history(
        self,
        number_completed: bool = False,
        previous_status: int = Display.STATUS_READY,
        number_being_entered=None,
        modifier_before_operation: int = -1,
    ):
        """Add current instruction to history.
        Records both number entries and operations as separate entries.

        Args:
            number_completed: True if a number entry was just completed (status change)
            previous_status: The display status before the current key was processed
            number_being_entered: The Number object from display when in input mode
            modifier_before_operation: The modifier code (F or G) before the operation was performed
        """
        try:
            if self._k is None:
                return

            key_code = self._k.get_code()

            # Skip adding to history for modifier keys (F and G)
            # These are just modifiers - wait for the next key to form the complete operation
            if key_code == Key.KEY_F.get_code() or key_code == Key.KEY_G.get_code():
                return

            # Skip adding to history for number input keys during input
            # These keys are part of building a number, not operations
            input_keys = [
                Key.KEY_0.get_code(),
                Key.KEY_1.get_code(),
                Key.KEY_2.get_code(),
                Key.KEY_3.get_code(),
                Key.KEY_4.get_code(),
                Key.KEY_5.get_code(),
                Key.KEY_6.get_code(),
                Key.KEY_7.get_code(),
                Key.KEY_8.get_code(),
                Key.KEY_9.get_code(),
                Key.KEY_DOT.get_code(),  # Decimal point
            ]

            # Skip if it's a number input key and we're still in input mode (not completed)
            if (
                key_code in input_keys
                and self._dsp.get_status() == Display.STATUS_INPUT
                and not number_completed
            ):
                return

            # Skip EEX during input (entering exponent is part of number input)
            if (
                key_code == Key.KEY_EEX.get_code()
                and self._dsp.get_status() == Display.STATUS_INPUT
                and not number_completed
            ):
                return

            # Skip CHS during input (changing sign is part of number input)
            if (
                key_code == Key.KEY_CHS.get_code()
                and self._dsp.get_status() == Display.STATUS_INPUT
                and not number_completed
            ):
                return

            # If a number was just completed, we need to record TWO entries:
            # 1. The number entry itself (with the number from display)
            # 2. The operation/key that completed it (with updated stack)

            if number_completed and previous_status == Display.STATUS_INPUT:
                # First, record the completed number entry
                # Create a temporary stack with the number in X
                if number_being_entered is not None:
                    from hp12c.model.stack import Stack

                    temp_stack = Stack(other=self._stk)
                    temp_stack.set(0, number_being_entered)

                    # Use a special marker for number entries: use KEY_NULL (-1) as key
                    # This distinguishes it from actual operations
                    self._stp.set_step(-1, Key.KEY_NULL.get_code(), -1)
                    instr = Instruction(self._stp, temp_stack)
                    self._hst.put(instr)

                # Now record the operation/key that completed it (including ENTER)
                # Use the modifier captured BEFORE the operation (since flags get toggled)
                modifier = modifier_before_operation
                complement = -1
                if self._flg.get_sto() > 0 or self._flg.get_rcl() > 0:
                    # For STO/RCL, complement would be the memory index
                    complement = -1  # Simplified - full implementation would track the memory index

                self._stp.set_step(modifier, key_code, complement)
                instr = Instruction(self._stp, self._stk)
                self._hst.put(instr)
            else:
                # Normal operation (not completing a number)
                # Use the modifier captured BEFORE the operation (since flags get toggled)
                modifier = modifier_before_operation
                complement = -1
                if self._flg.get_sto() > 0 or self._flg.get_rcl() > 0:
                    # For STO/RCL, complement would be the memory index
                    complement = -1  # Simplified - full implementation would track the memory index

                # Update step
                self._stp.set_step(modifier, key_code, complement)

                # Create instruction from current step and stack state
                instr = Instruction(self._stp, self._stk)
                self._hst.put(instr)

            # Notify controller to refresh history window if open
            if self._controller and hasattr(self._controller, "get_window"):
                window = self._controller.get_window()
                if window and hasattr(window, "_update_history_view"):
                    window._update_history_view()
        except Exception as e:
            # Don't fail on history errors, just log
            print(f"Error adding to history: {e}")

    def update_display(self):
        """Update display from stack."""
        try:
            if self._dsp.get_status() != 1:
                self._dsp.set_value(self.get_x())
            else:
                self._stk.set(0, self._dsp.get_value())
        except CalculatorException as e:
            self.show_error(e)
        except Exception as e:
            print(f"Error: {e}")

    def print_registers(self):
        """Print registers for debugging."""
        if (
            self._dsp.get_status() != 1
            and self._flg.get_f() == 0
            and self._flg.get_g() == 0
            and self._flg.get_sto() == 0
            and self._flg.get_rcl() == 0
        ):
            print("--------------------")
            print(self._stp)
            print(self._stk)
            print(self._fin)

    # Key handler methods - implementing all doKeyXX methods
    def do_key_00(self):
        """Handle key 0."""
        if self._flg.get_f() == 1:
            self._dsp.set_precision(0)
            self._flg.toggle_f()
            # self._stp.set_step(Step.STP_F_0)  # Would need Step constants
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._tmp = self._mem.mean()
            self._stk.set(0, self._tmp[1])
            self._stk.put(self._tmp[0])
            self._flg.toggle_g()
            self._dsp.set_status(0)
        elif self._flg.get_sto() > 0:
            self.sto_input(0)
        elif self._flg.get_rcl() > 0:
            self.rcl_input(0)
        elif self._flg.get_gto() > 0:
            self.gto_input(0)
        else:
            self.shift_up_if_output_status()
            self._dsp.input_char("0")

    def do_key_01(self):
        """Handle key 1."""
        if self._flg.get_f() == 1:
            self._dsp.set_precision(1)
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._tmp = self._mem.y_linear_estimation(self._stk.top())
            self._stk.set_last_top()
            self._stk.set(0, self._tmp[1])
            self._stk.put(self._tmp[0])
            self._flg.toggle_g()
            self._dsp.set_status(0)
        elif self._flg.get_sto() > 0:
            self.sto_input(1)
        elif self._flg.get_rcl() > 0:
            self.rcl_input(1)
        elif self._flg.get_gto() > 0:
            self.gto_input(1)
        else:
            self.shift_up_if_output_status()
            self._dsp.input_char("1")

    def do_key_02(self):
        """Handle key 2."""
        if self._flg.get_f() == 1:
            self._dsp.set_precision(2)
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._tmp = self._mem.y_linear_estimation(self._stk.top())
            self._stk.set_last_top()
            self._stk.set(0, self._tmp[1])
            self._stk.put(self._tmp[0])
            self._flg.toggle_g()
            self._dsp.set_status(0)
        elif self._flg.get_sto() > 0:
            self.sto_input(2)
        elif self._flg.get_rcl() > 0:
            self.rcl_input(2)
        elif self._flg.get_gto() > 0:
            self.gto_input(2)
        else:
            self.shift_up_if_output_status()
            self._dsp.input_char("2")

    def do_key_03(self):
        """Handle key 3."""
        if self._flg.get_f() == 1:
            self._dsp.set_precision(3)
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._stk.factorial()
            self._flg.toggle_g()
            self._dsp.set_status(2)
        elif self._flg.get_sto() > 0:
            self.sto_input(3)
        elif self._flg.get_rcl() > 0:
            self.rcl_input(3)
        elif self._flg.get_gto() > 0:
            self.gto_input(3)
        else:
            self.shift_up_if_output_status()
            self._dsp.input_char("3")

    def do_key_04(self):
        """Handle key 4."""
        if self._flg.get_f() == 1:
            self._dsp.set_precision(4)
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._flg.set_dmy(1)
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            self.sto_input(4)
        elif self._flg.get_rcl() > 0:
            self.rcl_input(4)
        elif self._flg.get_gto() > 0:
            self.gto_input(4)
        else:
            self.shift_up_if_output_status()
            self._dsp.input_char("4")

    def do_key_05(self):
        """Handle key 5."""
        if self._flg.get_f() == 1:
            self._dsp.set_precision(5)
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._flg.set_dmy(0)
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            self.sto_input(5)
        elif self._flg.get_rcl() > 0:
            self.rcl_input(5)
        elif self._flg.get_gto() > 0:
            self.gto_input(5)
        else:
            self.shift_up_if_output_status()
            self._dsp.input_char("5")

    def do_key_06(self):
        """Handle key 6."""
        if self._flg.get_f() == 1:
            self._dsp.set_precision(6)
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._stk.put(self._mem.weighted_mean())
            self._flg.toggle_g()
            self._dsp.set_status(0)
        elif self._flg.get_sto() > 0:
            self.sto_input(6)
        elif self._flg.get_rcl() > 0:
            self.rcl_input(6)
        elif self._flg.get_gto() > 0:
            self.gto_input(6)
        else:
            self.shift_up_if_output_status()
            self._dsp.input_char("6")

    def do_key_07(self):
        """Handle key 7."""
        if self._flg.get_f() == 1:
            self._dsp.set_precision(7)
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._flg.set_begin(1)
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            self.sto_input(7)
        elif self._flg.get_rcl() > 0:
            self.rcl_input(7)
        elif self._flg.get_gto() > 0:
            self.gto_input(7)
        else:
            self.shift_up_if_output_status()
            self._dsp.input_char("7")

    def do_key_08(self):
        """Handle key 8."""
        if self._flg.get_f() == 1:
            self._dsp.set_precision(8)
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._flg.set_begin(0)
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            self.sto_input(8)
        elif self._flg.get_rcl() > 0:
            self.rcl_input(8)
        elif self._flg.get_gto() > 0:
            self.gto_input(8)
        else:
            self.shift_up_if_output_status()
            self._dsp.input_char("8")

    def do_key_09(self):
        """Handle key 9."""
        if self._flg.get_f() == 1:
            self._dsp.set_precision(9)
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            self.sto_input(9)
        elif self._flg.get_rcl() > 0:
            self.rcl_input(9)
        elif self._flg.get_gto() > 0:
            self.gto_input(9)
        else:
            self.shift_up_if_output_status()
            self._dsp.input_char("9")

    def do_key_10(self):
        """Handle key / (divide)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            pass  # STO_DIV step
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._stk.divide()
            self._dsp.set_status(2)

    def do_key_11(self):
        """Handle key N."""
        if self._flg.get_f() == 1:
            # Amortization - simplified
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._stk.put(self._stk.pop().multiply(Number.TWELVE))
            self._fin.set_n(self._stk.top())
            self._dsp.set_status(2)
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            self._fin.set_n(self._stk.top())
            self._flg.set_sto(0)
            self._dsp.set_status(0)
        elif self._flg.get_rcl() > 0:
            self._stk.put(self._fin.get_n())
            self._flg.set_rcl(0)
            self._dsp.set_status(0)
        else:
            if self._dsp.get_status() == 0 or self._dsp.get_status() == 3:
                self._stk.set(0, self._fin.period())
                self._fin.set_n(self._stk.top())
                self._dsp.set_status(3)
            else:
                self._fin.set_n(self._stk.top())
                self._dsp.set_status(0)

    def do_key_12(self):
        """Handle key I."""
        if self._flg.get_f() == 1:
            # Simple interest - simplified
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._stk.put(self._stk.pop().divide(Number.TWELVE))
            self._fin.set_i(self._stk.top())
            self._dsp.set_status(2)
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            self._fin.set_i(self._stk.top())
            self._flg.set_sto(0)
            self._dsp.set_status(0)
        elif self._flg.get_rcl() > 0:
            self._stk.put(self._fin.get_i())
            self._flg.set_rcl(0)
            self._dsp.set_status(0)
        else:
            if self._dsp.get_status() == 0 or self._dsp.get_status() == 3:
                self._stk.set(0, self._fin.rate())
                self._fin.set_i(self._stk.top())
                self._dsp.set_status(3)
            else:
                self._fin.set_i(self._stk.top())
                self._dsp.set_status(0)

    def do_key_13(self):
        """Handle key PV."""
        if self._flg.get_f() == 1:
            # NPV - simplified
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._mem.set(0, self._stk.top())
            self._flg.toggle_g()
            self._dsp.set_status(2)
        elif self._flg.get_sto() > 0:
            self._fin.set_pv(self._stk.top())
            self._flg.set_sto(0)
            self._dsp.set_status(0)
        elif self._flg.get_rcl() > 0:
            self._stk.put(self._fin.get_pv())
            self._flg.set_rcl(0)
            self._dsp.set_status(0)
        else:
            if self._dsp.get_status() == 0 or self._dsp.get_status() == 3:
                self._stk.set(0, self._fin.present_value())
                self._fin.set_pv(self._stk.top())
                self._dsp.set_status(3)
            else:
                self._fin.set_pv(self._stk.top())
                self._dsp.set_status(0)

    def do_key_14(self):
        """Handle key PMT."""
        if self._flg.get_f() == 1:
            self._stk.round(self._dsp.get_precision())
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._mem.put(self._stk.top(), Number.ONE)
            self._fin.set_n(self._fin.get_n().add(Number.ONE))
            self._flg.toggle_g()
            self._dsp.set_status(2)
        elif self._flg.get_sto() > 0:
            self._fin.set_pmt(self._stk.top())
            self._flg.set_sto(0)
            self._dsp.set_status(0)
        elif self._flg.get_rcl() > 0:
            self._stk.put(self._fin.get_pmt())
            self._flg.set_rcl(0)
            self._dsp.set_status(0)
        else:
            if self._dsp.get_status() == 0 or self._dsp.get_status() == 3:
                # Price payment - simplified
                self._fin.set_pmt(self._stk.top())
                self._dsp.set_status(3)
            else:
                self._fin.set_pmt(self._stk.top())
                self._dsp.set_status(0)

    def do_key_15(self):
        """Handle key FV."""
        if self._flg.get_f() == 1:
            # IRR - simplified
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._mem.set_times(self._mem.get_current_index(), self._stk.top())
            self._flg.toggle_g()
            self._dsp.set_status(2)
        elif self._flg.get_sto() > 0:
            self._fin.set_fv(self._stk.top())
            self._flg.set_sto(0)
            self._dsp.set_status(0)
        elif self._flg.get_rcl() > 0:
            self._stk.put(self._fin.get_fv())
            self._flg.set_rcl(0)
            self._dsp.set_status(0)
        else:
            if self._dsp.get_status() == 0 or self._dsp.get_status() == 3:
                self._stk.set(0, self._fin.future_value())
                self._fin.set_fv(self._stk.top())
                self._dsp.set_status(3)
            else:
                self._fin.set_fv(self._stk.top())
                self._dsp.set_status(0)

    def do_key_16(self):
        """Handle key CHS (change sign)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._stk.add_days_to_date()
            self._dsp.set_value(self._stk.top())
            self._dsp.set_status(0)
            self._flg.toggle_g()
            self._dsp.set_lock(True)
        elif self._flg.get_sto() > 0:
            self._flg.toggle_sto()
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            if self._dsp.get_status() != 1:
                self._stk.put(self._stk.pop().negate())
            else:
                self._dsp.input_char("-")

    def do_key_20(self):
        """Handle key * (multiply)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._stk.squared()
            self._flg.toggle_g()
            self._dsp.set_status(2)
        elif self._flg.get_sto() > 0:
            pass  # STO_MUL step
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._stk.multiply()
            self._dsp.set_status(2)

    def do_key_21(self):
        """Handle key y^x (power)."""
        if self._flg.get_f() == 1:
            # Bond price - simplified
            self._flg.toggle_f()
            self._dsp.set_status(2)
        elif self._flg.get_g() == 1:
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            pass  # STO_POW step
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._stk.pow()
            self._dsp.set_status(2)

    def do_key_22(self):
        """Handle key 1/x (reciprocal)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            pass  # STO_RECIPROCAL step
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._stk.reciprocal()
            self._dsp.set_status(2)

    def do_key_23(self):
        """Handle key %T (percent of total)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            pass  # STO_PERC_TOT step
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._stk.percent_of_total()
            self._dsp.set_status(2)

    def do_key_24(self):
        """Handle key Δ% (percent difference)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            pass  # STO_PERC_DELTA step
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._stk.percent_difference()
            self._dsp.set_status(2)

    def do_key_25(self):
        """Handle key % (percent)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            pass  # STO_PERC step
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._stk.percent()
            self._dsp.set_status(2)

    def do_key_26(self):
        """Handle key EEX (enter exponent)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            pass  # STO_EEX step
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._dsp.set_mode(Display.MODE_EXPONENTIAL)
            self._dsp.set_status(1)

    def do_key_30(self):
        """Handle key - (subtract)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            pass  # STO_SUB step
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._stk.subtract()
            self._dsp.set_status(2)

    def do_key_31(self):
        """Handle key R/S (run/stop)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            pass  # STO_RS step
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            if self._flg.get_run() == 1:
                self.stop_program()
            else:
                self.execute_program()

    def do_key_32(self):
        """Handle key SST (single step)."""
        if self._flg.get_f() == 1:
            # F-SST step
            self._prg.set_current_index(0)
            self._flg.toggle_f()
            self._dsp.set_status(0)
        elif self._flg.get_g() == 1:
            if not self._prg.back():
                self._prg.set_current_index(self._prg.get_size() - 1)
            self._dsp.set_status(0)
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            pass  # STO_SST step
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            if not self._prg.next():
                self._prg.set_current_index(0)
            self._dsp.set_status(0)

    def do_key_33(self):
        """Handle key R↓ (roll down)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._flg.toggle_gto()
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            self._flg.toggle_sto()
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._stk.roll_down()
            self._dsp.set_status(2)

    def do_key_34(self):
        """Handle key x↔y (swap)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            # G + XY = square root
            self._stk.sqrt()
            self._flg.toggle_g()
            self._dsp.set_status(2)
        elif self._flg.get_sto() > 0:
            self._flg.toggle_sto()
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._stk.swap_top_pair()
            self._dsp.set_status(2)

    def do_key_35(self):
        """Handle key CLX (clear X)."""
        if self._flg.get_f() == 1:
            self._mem.clear()
            self._fin.clear()
            self._stk.clear()
            self._stk.clear_last_top()
            self._flg.toggle_f()
            self._dsp.set_status(0)
        elif self._flg.get_g() == 1:
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            self._flg.toggle_sto()
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._stk.set(0, Number.ZERO)
            self._dsp.set_status(0)

    def do_key_36(self):
        """Handle key ENTER."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self.set_x(self._stk.get_last_top())
            self._dsp.set_status(2)
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            self._flg.toggle_sto()
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._stk.put(self._dsp.get_value())
            self._dsp.set_status(0)

    def do_key_40(self):
        """Handle key + (add)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            pass  # STO_SUM step
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._stk.add()
            self._dsp.set_status(2)

    def do_key_41(self):
        """Handle key ON."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._flg.toggle_g()
        elif self._flg.get_sto() > 0:
            self._flg.toggle_sto()
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        elif self._flg.get_on() == 1:
            self._flg.toggle_on()
        else:
            # ON button pressed - save everything and quit
            if self._controller:
                self._controller.quit()
            else:
                self._flg.toggle_on()

    def do_key_42(self):
        """Handle key f."""
        if self._flg.get_f() > 0:
            self.clear_fgsr()
        else:
            self.clear_fgsr()
            self._flg.toggle_f()

    def do_key_43(self):
        """Handle key g."""
        if self._flg.get_g() > 0:
            self.clear_fgsr()
        else:
            self.clear_fgsr()
            self._flg.toggle_g()

    def do_key_44(self):
        """Handle key STO."""
        if self._flg.get_sto() > 0:
            self.clear_fgsr()
        else:
            self.clear_fgsr()
            self._flg.toggle_sto()

    def do_key_45(self):
        """Handle key RCL."""
        if self._flg.get_rcl() > 0:
            self.clear_fgsr()
        else:
            self.clear_fgsr()
            self._flg.toggle_rcl()

    def do_key_48(self):
        """Handle key . (decimal point)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._tmp = self._mem.standard_deviation()
            self._stk.set(0, self._tmp[1])
            self._stk.put(self._tmp[0])
            self._flg.toggle_g()
            self._dsp.set_status(0)
        elif self._flg.get_sto() > 0:
            self.sto_input(-1)
        elif self._flg.get_rcl() > 0:
            self.rcl_input(-1)
        elif self._flg.get_gto() > 0:
            self.gto_input(-1)
        elif self._flg.get_on() == 1:
            self._dsp.toggle_comma()
            self._flg.toggle_on()
        else:
            self.shift_up_if_output_status()
            self._dsp.input_char(".")

    def do_key_49(self):
        """Handle key Σ+ (sum plus)."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        elif self._flg.get_g() == 1:
            self._mem.sub_stats(self._stk.top(), self._stk.get(1))
            self._stk.set_last_top()
            self._stk.set(0, self._mem.get_r1())
            self._flg.toggle_g()
            self._dsp.set_status(0)
        elif self._flg.get_sto() > 0:
            self._flg.toggle_sto()
        elif self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()
        else:
            self._mem.sum_stats(self._stk.top(), self._stk.get(1))
            self._stk.set_last_top()
            self._stk.set(0, self._mem.get_r1())
            self._dsp.set_status(0)

    # Helper methods
    def sto_input(self, i: int):
        """Handle STO input."""
        if self._flg.get_sto() == 1:
            self._tmp = [Number.ZERO, Number.ZERO, Number.ZERO]
            if self._mem.get_size() <= 20:
                if i == -1:
                    self._tmp[0] = Number.ZERO
                    self._tmp[1] = Number.ONE
                    self._flg.set_sto(3)
                else:
                    self._tmp[0] = Number.ZERO
                    self._tmp[1] = Number.ZERO
                    self._tmp[2] = Number.n(i)
                    self._flg.set_sto(4)
            elif self._mem.get_size() <= 100:
                if i == -1:
                    return
                self._tmp[0] = Number.ZERO
                self._tmp[1] = Number.n(i)
                self._flg.set_sto(3)
            else:
                if i == -1:
                    return
                self._tmp[0] = Number.n(i)
                self._flg.set_sto(2)
        elif self._flg.get_sto() == 2:
            if i == -1:
                return
            if self._tmp is None:
                return
            self._tmp[1] = Number.n(i)
            self._flg.set_sto(3)
        elif self._flg.get_sto() == 3:
            if i == -1:
                return
            if self._tmp is None:
                return
            self._tmp[2] = Number.n(i)
            self._flg.set_sto(4)

        if self._flg.get_sto() == 4:
            self._flg.set_sto(0)
            if self._tmp is None:
                return
            idx = self._tmp[0].i() * 100 + self._tmp[1].i() * 10 + self._tmp[2].i()
            self._mem.set(idx, self._stk.top())
            self._dsp.set_status(2)

    def rcl_input(self, i: int):
        """Handle RCL input."""
        if self._flg.get_rcl() == 1:
            self._tmp = [Number.ZERO, Number.ZERO, Number.ZERO]
            if self._mem.get_size() <= 20:
                if i == -1:
                    self._tmp[0] = Number.ZERO
                    self._tmp[1] = Number.ONE
                    self._flg.set_rcl(3)
                else:
                    self._tmp[0] = Number.ZERO
                    self._tmp[1] = Number.ZERO
                    self._tmp[2] = Number.n(i)
                    self._flg.set_rcl(4)
            elif self._mem.get_size() <= 100:
                if i == -1:
                    return
                self._tmp[0] = Number.ZERO
                self._tmp[1] = Number.n(i)
                self._flg.set_rcl(3)
            else:
                if i == -1:
                    return
                self._tmp[0] = Number.n(i)
                self._flg.set_rcl(2)
        elif self._flg.get_rcl() == 2:
            if i == -1:
                return
            if self._tmp is None:
                return
            self._tmp[1] = Number.n(i)
            self._flg.set_rcl(3)
        elif self._flg.get_rcl() == 3:
            if i == -1:
                return
            if self._tmp is None:
                return
            self._tmp[2] = Number.n(i)
            self._flg.set_rcl(4)

        if self._flg.get_rcl() == 4:
            self._flg.set_rcl(0)
            if self._tmp is None:
                return
            idx = self._tmp[0].i() * 100 + self._tmp[1].i() * 10 + self._tmp[2].i()
            self.set_x(self._mem.get(idx))
            self._dsp.set_status(2)

    def gto_input(self, i: int):
        """Handle GTO input."""
        if self._flg.get_gto() == 1:
            self._tmp = [Number.ZERO, Number.ZERO, Number.ZERO]
            if self._prg.get_size() <= 20:
                if i == -1:
                    self._tmp[0] = Number.ZERO
                    self._tmp[1] = Number.ONE
                    self._flg.set_gto(3)
                else:
                    self._tmp[0] = Number.ZERO
                    self._tmp[1] = Number.ZERO
                    self._tmp[2] = Number.n(i)
                    self._flg.set_gto(4)
            elif self._prg.get_size() <= 100:
                if i == -1:
                    return
                self._tmp[0] = Number.ZERO
                self._tmp[1] = Number.n(i)
                self._flg.set_gto(3)
            else:
                if i == -1:
                    return
                self._tmp[0] = Number.n(i)
                self._flg.set_gto(2)
        elif self._flg.get_gto() == 2:
            if i == -1:
                return
            if self._tmp is None:
                return
            self._tmp[1] = Number.n(i)
            self._flg.set_gto(3)
        elif self._flg.get_gto() == 3:
            if i == -1:
                return
            if self._tmp is None:
                return
            self._tmp[2] = Number.n(i)
            self._flg.set_gto(4)

        if self._flg.get_gto() == 4:
            self._flg.set_gto(0)
            if self._tmp is None:
                return
            idx = self._tmp[0].i() * 100 + self._tmp[1].i() * 10 + self._tmp[2].i()
            self._prg.set_current_index(idx)
            self._dsp.set_status(2)

    def program_input(self, key: Key | None):
        """Handle program mode input."""
        if key is None:
            return
        if self._dsp.get_lock():
            self._dsp.set_lock(False)
            return
        # Simplified program input handling
        # Full implementation would handle all program mode operations

    def show_error(self, e: CalculatorException):
        """Show error on display."""
        if e.get_error() != Error.ERROR_MAG:
            self.show_display_message(f" Error {e.get_code()}")
        self._logger.error(f"Calculator error: {e}")

    def show_display_message(self, msg: str):
        """Show message on display."""
        self._dsp.set_message(msg)
        self._dsp.set_lock(True)
        if self._controller and hasattr(self._controller, "get_window"):
            window = self._controller.get_window()
            if window and hasattr(window, "update_display"):
                window.update_display()

    def clear_fgsr(self):
        """Clear F, G, STO, RCL flags."""
        if self._flg.get_f() == 1:
            self._flg.toggle_f()
        if self._flg.get_g() == 1:
            self._flg.toggle_g()
        if self._flg.get_sto() > 0:
            self._flg.toggle_sto()
        if self._flg.get_rcl() > 0:
            self._flg.toggle_rcl()

    def execute_step(self, stp: Step):
        """Execute a program step."""
        if stp.get_key() == Key.KEY_NULL.get_code() or (
            stp.get_modifier() == Key.KEY_G.get_code()
            and stp.get_key() == Key.KEY_ROLL.get_code()
            and stp.get_complement() == Key.KEY_0.get_code()
        ):
            self.stop_program()
        elif (
            stp.get_modifier() == Key.KEY_G.get_code() and stp.get_key() == Key.KEY_ROLL.get_code()
        ):
            self._prg.set_current_index(stp.get_complement())
        elif stp.get_modifier() == Key.KEY_G.get_code() and stp.get_key() == Key.KEY_XY.get_code():
            if self._stk.get(0).less_than_or_equal_to(self._stk.get(1)):
                self._prg.next()
            else:
                self._prg.next()
                self._prg.next()
        elif stp.get_modifier() == Key.KEY_G.get_code() and stp.get_key() == Key.KEY_CLX.get_code():
            if self._stk.get(0).is_zero():
                self._prg.next()
            else:
                self._prg.next()
                self._prg.next()
        elif stp.get_key() == Key.KEY_STO.get_code():
            self._mem.set(stp.get_complement(), self._stk.top())
            self._dsp.set_status(2)
            self._prg.next()
        elif stp.get_key() == Key.KEY_RCL.get_code():
            self.set_x(self._mem.get(stp.get_complement()))
            self._dsp.set_status(2)
            self._prg.next()
        else:
            if stp.get_modifier() > -1:
                self.key_released(Key.get_key(stp.get_modifier()))
            if stp.get_key() > -1:
                self.key_released(Key.get_key(stp.get_key()))
            if stp.get_complement() > -1:
                self.key_released(Key.get_key(stp.get_complement()))
            self._prg.next()

    def execute_single_step(self):
        """Execute single program step."""
        self.show_display_message("running")
        self.get_display().set_lock(False)
        if self._prg.get_current_index() == 0:
            self._prg.next()
        current_step = self._prg.get_current()
        if current_step is not None:
            self.execute_step(current_step)
        if self._prg.get_current_index() == self._prg.get_size() - 1:
            self.stop_program()

    def execute_program(self):
        """Execute program in background thread."""

        def worker():
            while self._flg.get_run() == 1:
                self.execute_single_step()
                import time

                time.sleep(0.01)

        self._flg.set_run(1)
        self._worker = threading.Thread(target=worker, daemon=True)
        self._worker.start()

    def stop_program(self):
        """Stop program execution."""
        self._prg.set_current_index(0)
        self._flg.set_run(0)
        self._dsp.set_lock(False)
        if self._controller and hasattr(self._controller, "get_window"):
            window = self._controller.get_window()
            if window and hasattr(window, "update_display"):
                window.update_display()
