"""Unit tests for Stack class."""

from hp12c.hp12c_math.number import Number
from hp12c.model.stack import Stack


class TestStack:
    """Test cases for Stack class."""

    def test_initialization(self):
        """Test stack initialization."""
        stack = Stack()
        assert stack is not None
        # Stack should be initialized with zeros
        assert stack.get(0).equals(Number.ZERO)

    def test_push_and_get(self):
        """Test pushing values and getting them."""
        stack = Stack()
        value = Number("42")
        stack.push(value)

        assert stack.get(0).equals(value)

    def test_stack_levels(self):
        """Test stack has 4 levels (X, Y, Z, T)."""
        stack = Stack()

        # Push 4 different values
        stack.push(Number("1"))
        stack.push(Number("2"))
        stack.push(Number("3"))
        stack.push(Number("4"))

        # Check all levels
        assert stack.get(0).equals(Number("4"))  # X
        assert stack.get(1).equals(Number("3"))  # Y
        assert stack.get(2).equals(Number("2"))  # Z
        assert stack.get(3).equals(Number("1"))  # T

    def test_pop(self):
        """Test pop operation."""
        stack = Stack()
        stack.push(Number("5"))
        stack.push(Number("10"))

        popped = stack.pop()
        assert popped.equals(Number("10"))
        assert stack.get(0).equals(Number("5"))

    def test_roll_down(self):
        """Test roll down operation."""
        stack = Stack()
        # Push 1, 2, 3, 4
        stack.push(Number("1"))
        stack.push(Number("2"))
        stack.push(Number("3"))
        stack.push(Number("4"))

        stack.roll_down()

        # After roll_down: stack rotates down one position
        # T → Z → Y → X → T (circular rotation)
        # Initial: X=4, Y=3, Z=2, T=1
        # After:   X=1 (from T), Y=4 (from X), Z=3 (from Y), T=2 (from Z)
        assert stack.get(0).equals(Number("1"))  # X gets T's value
        assert stack.get(1).equals(Number("4"))  # Y gets X's value
        assert stack.get(2).equals(Number("3"))  # Z gets Y's value
        assert stack.get(3).equals(Number("2"))  # T gets Z's value

    def test_swap(self):
        """Test swap operation (X and Y)."""
        stack = Stack()
        stack.push(Number("5"))
        stack.push(Number("10"))

        stack.swap()

        assert stack.get(0).equals(Number("5"))
        assert stack.get(1).equals(Number("10"))

    def test_clear(self):
        """Test clear operation."""
        stack = Stack()
        stack.push(Number("42"))
        stack.push(Number("100"))

        stack.clear()

        # All levels should be zero
        for i in range(4):
            assert stack.get(i).equals(Number.ZERO)

    def test_last_x(self):
        """Test LAST X register."""
        stack = Stack()
        stack.push(Number("5"))
        stack.push(Number("10"))
        stack.pop()  # This should save 10 to LAST X

        last_x = stack.get_last_x()
        assert last_x.equals(Number("10"))

    def test_stack_overflow_behavior(self):
        """Test stack behavior when pushing more than 4 values."""
        stack = Stack()
        # Push 5 values
        for i in range(5):
            stack.push(Number(str(i + 1)))

        # When pushing more than 4 values, the oldest values get pushed out
        # After pushing 1,2,3,4,5: X=5, Y=4, Z=3, T=2 (value 1 is lost)
        assert stack.get(0).equals(Number("5"))  # X contains newest value
        assert stack.get(1).equals(Number("4"))  # Y
        assert stack.get(2).equals(Number("3"))  # Z
        assert stack.get(3).equals(Number("2"))  # T contains second-oldest (oldest was pushed out)
