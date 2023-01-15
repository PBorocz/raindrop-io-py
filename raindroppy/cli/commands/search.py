"""Create a new Raindrop bookmark."""
from dataclasses import dataclass
from typing import Iterable, Optional

from rich.table import Table

from raindroppy.api import Collection, Raindrop
from raindroppy.cli import PROMPT_STYLE, cli_prompt
from raindroppy.cli.cli import CLI
from raindroppy.cli.commands import get_from_list
from raindroppy.cli.spinner import Spinner


@dataclass
class SearchRequest:
    """Encapsulates all items necessary and possible for a Raindrop *search*."""

    search: str
    collection_s: tuple[str]
    tag_s: tuple[str]

    collection: Collection = None


@dataclass
class SearchResult:
    """A single Raindrop search result."""

    collection: Collection
    raindrop: Raindrop


@dataclass
class SearchResults:
    """Encapsulates all items associated with the *results* of a Raindrop search."""

    results: list[SearchResult]

    def __iter__(self) -> Iterable[SearchResult]:
        for result in self.results:
            yield result


def __prompt_search_terms(cli: CLI) -> tuple[bool, Optional[str]]:
    """Prompt for all user response to perform a search, or None if user quits."""
    while True:
        try:
            response = cli.session.prompt(cli_prompt(("search?",)), style=PROMPT_STYLE)
            if response == "?":
                cli.console.print("We need a search term here, eg. python, tag=foo etc.")
            elif response in ("q", "."):
                return True, None
            else:
                return False, response
        except (KeyboardInterrupt, EOFError):
            return True, None


def _prompt_search(cli: CLI) -> SearchRequest:
    """Prompt for all responses necessary for a search, ie. terms and collections"""
    quit, search = __prompt_search_terms(cli)
    if quit:
        return None

    # What collection(s) to search across?
    collection_s = get_from_list(cli, ("search", "collection(s)"), cli.state.get_collection_titles())

    # What tag(s) to search for?
    tag_s = get_from_list(cli, ("search", "tag(s)"), cli.state.tags)

    return SearchRequest(search, collection_s.split(), tag_s.split())


def __do_search_in_collection(cli: CLI, search_request: SearchRequest) -> SearchResults:
    results = list()
    page: int = 0
    while raindrops := Raindrop.search(
        cli.state.api, collection=search_request.collection, page=page, word=search_request.search
    ):
        for raindrop in raindrops:
            results.append(SearchResult(search_request.collection, raindrop))
        page += 1
    return SearchResults(results)


def _do_search(cli: CLI, search_request: SearchRequest) -> Optional[list[Raindrop]]:
    """Search across none, one or many collections for the respective search terms"""
    return_ = list()
    for collection_title in search_request.collection_s:
        search_request.collection = cli.state.find_collection(collection_title)
        assert search_request.collection, f"Sorry, unable to find a collection with {collection_title=}?!"
        return_.extend(__do_search_in_collection(cli, search_request))
    return return_


def _display_search_results(cli: CLI, search_request: SearchRequest, search_results: SearchResults) -> None:
    if not search_results:
        msg = f"Sorry, nothing found with title containing '{search_request.search}'"
        if len(search_request.collection_s) == 1:
            msg += f" in collection: '{search_request.collection_s[0]}'."
        else:
            msg += f" across {len(search_request.collection_s)} collections."
        cli.console.print(msg)
        return

    table = Table()
    table.add_column("Collection", justify="left", style="#00ffff", no_wrap=True)
    table.add_column("Raindrop", style="#00ff00")
    for search_result in search_results:
        table.add_row(search_result.collection.title, search_result.raindrop.title)
    cli.console.print(table)


def process(cli: CLI) -> None:
    """Top-level UI Controller for searching for bookmark(s)."""

    while True:
        search_request = _prompt_search(cli)
        if search_request is None:
            return None

        with Spinner(f"Searching for '{search_request.search}'..."):
            search_results = _do_search(cli, search_request)

        _display_search_results(cli, search_request, search_results)
