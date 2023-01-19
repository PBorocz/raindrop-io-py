"""Top level cli.commands dunder init, mostly common methods."""

from typing import Final, Optional

from prompt_toolkit.completion import WordCompleter

from raindroppy.cli import PROMPT_STYLE, prompt
from raindroppy.cli.models.eventLoop import EventLoop


def get_from_list(
    el: EventLoop,
    prompt_s: tuple[str],
    options: tuple[str],
) -> Optional[str]:
    """Mini-event loop to prompt for one or more selected options from the list provided."""
    completer: Final = WordCompleter(options)
    while True:
        response = el.session.prompt(
            prompt(prompt_s),  # ("create", "url", f"{prompt}?"))
            completer=completer,
            style=PROMPT_STYLE,
            complete_while_typing=True,
            enable_history_search=False,
        )
        if response == "?":
            el.console.print(", ".join(options))
        else:
            break
    return response
