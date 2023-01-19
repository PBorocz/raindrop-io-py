"""Top level CLI dunder init, primarily constants used across all commands."""
import sys
from typing import Final

from prompt_toolkit.styles import Style

CONTENT_TYPES: Final = {
    ".pdf": "application/pdf",
    ".py": "text/plain",
    ".txt": "text/plain",
    ".org": "text/plain",
}


COLOR_TABLE_COLUMN_1 = "#00ffff"
COLOR_TABLE_COLUMN_2 = "#00ff00"

PROMPT_STYLE: Final = Style.from_dict(
    {
        # We use our table color scheme to match
        "prompt": COLOR_TABLE_COLUMN_1,  # Prompt is cyan
        "": COLOR_TABLE_COLUMN_2,  # User input is green
    },
)


def prompt(sub_levels: tuple[str] | None = ()) -> str:
    """Render a command prompt to any number of 'levels'.

    With no sub-levels, prompt is: "> "
    With sub-levels ("A", "SubA"): "A> SubA> "
    """
    delimiter: str = "> "
    if sub_levels:
        prompt = ""
        for level in sub_levels:
            prompt += level + delimiter
    else:
        prompt = delimiter
    return [("class:prompt", prompt)]


def make_italic(str_):
    """Use Rich's rich text to make string italic."""
    return f"[italic]{str_}[/italic]"


def options_as_help(options: list[str]) -> str:
    """Return the list of options in a nice format for display."""
    return ", ".join([make_italic(option) for option in options])


def goodbye(console) -> None:
    """Called on successful exit from any command/event-loop."""
    console.print(
        "[italic]Thanks, Gracias, Merci, Danka, ありがとう, спасибо, Köszönöm...![/]\n",
    )
    sys.exit(0)
