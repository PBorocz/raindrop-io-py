"""Constants used across all commands"""
from typing import Final

from prompt_toolkit.styles import Style

CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".py": "text/plain",
    ".txt": "text/plain",
    ".org": "text/plain",
}


PROMPT_STYLE: Final = Style.from_dict(
    {
        "prompt": "#00ffff",  # Prompt is cyan
        "": "#00ff00",  # User input  is green
    }
)


def make_italic(str_):
    return f"[italic]{str_}[/italic]"


def cli_prompt(sub_levels: tuple[str] | None = ()) -> str:
    if sub_levels:
        prompt = ""
        for level in sub_levels:
            prompt += level + "> "
    else:
        prompt = "> "
    return [("class:prompt", prompt)]


def options_as_help(options: list[str]) -> str:
    return ", ".join([make_italic(option) for option in options])
