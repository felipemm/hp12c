"""
Timer utility.
Ported from Java Timer.java.
"""

import time


class Timer:
    """Simple timer utility."""

    def __init__(self, sec: float):
        """Initialize timer with seconds."""
        self._sec = sec

    def run(self):
        """Run timer (sleep)."""
        time.sleep(self._sec)

    def set_time(self, sec: float):
        """Set timer duration."""
        self._sec = sec
