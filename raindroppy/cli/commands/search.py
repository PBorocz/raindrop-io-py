"""Create a new Raindrop bookmark."""
from typing import Optional

from beaupy import select_multiple
from rich.table import Table

from raindroppy.api import Collection, Raindrop
from raindroppy.cli import PROMPT_STYLE, cli_prompt
from raindroppy.cli.cli import CLI
from raindroppy.cli.spinner import Spinner


def __get_search_terms(cli: CLI) -> Optional[str]:
    """Prompt for all user response to perform a search, or None if user quits."""
    prompt = cli_prompt(("search?",))
    while True:
        try:
            response = cli.session.prompt(prompt, style=PROMPT_STYLE)
            if response == "?":
                cli.console.print("We need a search term here, eg. python, tag=foo etc.")
            elif response in ("q", "."):
                return None
            elif len(response) > 0:  # Empty response falls through to try again
                return response
        except (KeyboardInterrupt, EOFError):
            return None


def _get_search(cli: CLI) -> tuple[str, Optional[list[str]]]:
    """Prompt for all responses necessary for a search, ie. terms and collections"""
    if search := __get_search_terms(cli):
        collection_s: list[str] = select_multiple(list(cli.state.get_collection_titles()))
        return (search, collection_s)
    return None, None


def __do_search_in_collection(cli: CLI, search_terms: str, collection: Collection) -> Optional[list[Raindrop]]:
    return_ = list()
    page: int = 0
    while raindrops := Raindrop.search(cli.state.api, collection=collection, page=page, word=search_terms):
        for raindrop in raindrops:
            return_.append((collection, raindrop))
        page += 1
    return return_


def _do_search(cli: CLI, search_terms: str, collection_s: Optional[list[str]] = []) -> Optional[list[Raindrop]]:
    """Search across none, one or many collections for the respective search terms"""
    return_ = list()

    for collection_title in collection_s:
        collection = cli.state.find_collection(collection_title)
        assert collection, f"Sorry, unable to find a collection with {collection_title=}?!"
        return_.extend(__do_search_in_collection(cli, search_terms, collection))

    return return_


def _display_search_results(
    cli: CLI, search_terms: str, collection_s: Optional[list[str]], results: list[tuple[Collection, Raindrop]]
) -> None:
    if not results:
        msg = f"Sorry, nothing found with title containing '{search_terms}'"
        if len(collection_s) == 1:
            msg += f" in collection: '{collection_s[0]}'."
        else:
            msg += f" across {len(collection_s)} collections."
        cli.console.print(msg)
        return

    table = Table(title="Search Results")
    table.add_column("Collection", justify="right", style="#00ffff", no_wrap=True)
    table.add_column("Raindrop", style="#00ff00")
    for collection, raindrop in results:
        table.add_row(collection.title, raindrop.title)
    cli.console.print(table)


def process(cli: CLI) -> None:
    """Top-level UI Controller for searching for bookmark(s)."""

    while True:
        search, collection_s = _get_search(cli)
        if search is None:
            return None
        with Spinner(f"Searching for '{search}'..."):
            results = _do_search(cli, search, collection_s)

        _display_search_results(cli, search, collection_s, results)
