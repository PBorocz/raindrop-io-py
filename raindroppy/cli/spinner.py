"""Spinner capability"""
#
# Inspired (simplified) from beaupy; thanks to Peter Výboch!
# https://github.com/petereon/beaupy/blob/master/beaupy/spinners/_spinners.py
#
from itertools import cycle

from rich.live import Live

ARC = ["◜", "◠", "◝", "◞", "◡", "◟"]


class Spinner:
    """Raindroppy simple CLI progress spinner as context manager"""

    _spinner_characters: cycle
    _live_display: Live

    def __init__(self, text: str = "Loading...") -> None:
        """Create spinner for user feedback.

        Args:
            text (str): Text that will be shown after the spinner.

        Example:
            with Spinner("I'm doing work..."):
                do_something()
        """
        self._spinner_characters: list[str] = cycle(ARC)
        self._live_display = Live(
            "",
            transient=True,  # Remove spinner once complete.
            refresh_per_second=10,  # Reasonable default
            get_renderable=lambda: f"{next(self._spinner_characters)} {text}",
        )

    def __enter__(self):
        """Starts the spinner"""
        self._live_display.start()

    def __exit__(self, exc_type, exc_value, exc_tb):
        """Stops the spinner"""
        self._live_display.stop()
