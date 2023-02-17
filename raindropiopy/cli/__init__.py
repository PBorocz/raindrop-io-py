"""Top level CLI dunder init, primarily constants used across all commands."""
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
WARNING = "#fffc00"

PROMPT_STYLE: Final = Style.from_dict(
    {
        # We use our table color scheme to match
        "prompt": COLOR_TABLE_COLUMN_1,  # Prompt is cyan
        "": COLOR_TABLE_COLUMN_2,  # User input is green
    },
)

PROMPT_STYLE_WARNING: Final = Style.from_dict(
    {
        # We use our table color scheme to match
        "prompt": WARNING,  # Prompt is yellow
        "": WARNING,  # User input is yellow
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


def options_as_help(options: list[str], depth: int = 1) -> str:
    """Return the list of options in a nice format for display.

    Input options might be: ["Action"  , "SomethingElse"  , "Done"]
    first, we convert to    ["(A)ction", "(S)omethingElse", "(D)one"]
    then we render to      "[italic](A)nAction[/italic], "

    Similarly, when called with: ["title", "tag", "back"] AND depth of *2*:
    we convert to                ["(ti)tle", "(ta)g", "(b)ack"]
    and then render to          "[italic](ti)tle[/italic] [italic](ta)g[/italic]..."
    """
    initial_letters = [f"({option[0:depth]}){option[depth:]}" for option in options]
    return ", ".join([make_italic(option) for option in initial_letters])


def goodbye(console) -> None:
    """Print a nice thank you message on successful exit from any command/event-loop."""
    console.print(
        "[italic]Thanks, Gracias, Merci, Danka, ありがとう, cпacи6o, Köszönöm...![/]\n",
    )
