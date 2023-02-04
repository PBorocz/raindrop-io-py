"""Spinner capability."""
#
# Inspired from beaupy (thanks Peter Výboch!) using underlying Rich-based "Live" class.
#
from itertools import cycle

from rich.live import Live

ARC = ["◜", "◠", "◝", "◞", "◡", "◟"]


class Spinner:
    """Rich-based CLI progress spinner as a Context Manager."""

    _spinner_characters: cycle
    _live_display: Live

    def __init__(self, text: str = "Loading...") -> None:
        """Create spinner for user feedback during a time-consuming operation.

        :param text: Text that will be shown after the spinner.

        Example:
        -------
            with Spinner("Please wait, I'm doing some work..."):
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
        """Start the spinner."""
        self._live_display.start()

    def __exit__(self, _exc_type, _exc_value, _exc_tb):
        """Stop the spinner."""
        self._live_display.stop()
