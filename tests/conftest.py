"""Pytest configuration and shared fixtures."""

import pytest

from hp12c.calculator.calculator import Calculator
from hp12c.calculator.config import Configuration
from hp12c.hp12c_math.number import Number


@pytest.fixture
def calculator():
    """Create a Calculator instance for testing."""
    calc = Calculator()
    return calc


@pytest.fixture
def config():
    """Create a Configuration instance for testing."""
    return Configuration.create_configuration()


@pytest.fixture
def number_zero():
    """Create a Number instance with value zero."""
    return Number.ZERO


@pytest.fixture
def number_one():
    """Create a Number instance with value one."""
    return Number.ONE


@pytest.fixture
def number_ten():
    """Create a Number instance with value ten."""
    return Number.TEN


@pytest.fixture
def sample_numbers():
    """Create a list of sample Number instances."""
    return [
        Number.ZERO,
        Number.ONE,
        Number.TWO,
        Number.TEN,
        Number("3.14159"),
        Number("-42"),
    ]
