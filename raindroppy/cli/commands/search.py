"""Create a new Raindrop bookmark."""
from typing import Optional

from raindroppy.api import Raindrop
from raindroppy.cli import PROMPT_STYLE, cli_prompt
from raindroppy.cli._cli import CLI
from raindroppy.cli.spinner import Spinner


def __get_search_terms(cli: CLI) -> Optional[str]:
    prompt = cli_prompt(("search?",))
    while True:
        try:
            response = cli.session.prompt(prompt, style=PROMPT_STYLE)
            if response == "?":
                cli.console.print("We need a search term here, eg. python, tag='foo' etc.")
            elif response in ("q", "."):
                return None
            else:
                return response
        except (KeyboardInterrupt, EOFError):
            return None


def __do_search(cli: CLI, search_terms: str) -> None:
    count_: int = 0
    page: int = 0
    while raindrops := Raindrop.search(cli.state.api, page=page, word=search_terms):
        for raindrop in raindrops:
            cli.console.print(raindrop.title)
            count_ += 1
        page += 1

    if not count_:
        cli.console.print(f"Sorry, nothing found with title containing '{search_terms}'")


def process(cli: CLI) -> None:
    """Top-level UI Controller for adding bookmark(s) from the terminal."""

    while True:
        search = __get_search_terms(cli)
        if search is None:
            return None
        with Spinner(f"Searching for '{search}'..."):
            __do_search(cli, search)
