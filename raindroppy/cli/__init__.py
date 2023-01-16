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


PROMPT_STYLE: Final = Style.from_dict(
    {
        "prompt": "#00ffff",  # Prompt is cyan
        "": "#00ff00",  # User input  is green
    },
)


def cli_prompt(sub_levels: tuple[str] | None = ()) -> str:
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
