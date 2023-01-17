"""Create a new Raindrop bookmark."""
from dataclasses import dataclass
from typing import Optional

from prompt_toolkit.completion import WordCompleter
from rich.table import Table

from raindroppy.api import Collection, CollectionRef, Raindrop
from raindroppy.cli import PROMPT_STYLE, cli_prompt
from raindroppy.cli.cli import CLI
from raindroppy.cli.commands import get_from_list
from raindroppy.cli.commands.help import help_search
from raindroppy.cli.spinner import Spinner

WILDCARD = "*"


@dataclass
class SearchRequest:
    """Encapsulates all items necessary and possible for a Raindrop *search*."""

    search: str
    collection_s: tuple[str]

    collection: Collection = None


def __prompt_search_terms(cli: CLI) -> tuple[bool, Optional[str]]:
    """Prompt for all user response to perform a search, or None if user quits."""
    # What tag(s) to do allow for autocomplete?
    search_tags = [f"#{tag}" for tag in cli.state.tags]
    completer = WordCompleter(search_tags)

    while True:
        response = cli.session.prompt(
            cli_prompt(("search term(s)?",)),
            completer=completer,
            style=PROMPT_STYLE,
            complete_while_typing=True,
            enable_history_search=False,
        )
        if response == "?":
            help_search(cli)
        elif response in ("q", "."):
            return True, None
        elif response:
            return False, response

        # Otherwise, we fall through and try again, we need *some* search terms!


def _prompt_search(cli: CLI) -> SearchRequest:
    """Prompt for all responses necessary for a search, ie. terms and collections."""
    quit, search = __prompt_search_terms(cli)
    if quit:
        return None

    # What collection(s) to search across?
    collection_s = get_from_list(
        cli,
        ("search", "in collection(s)?"),
        cli.state.get_collection_titles(exclude_unsorted=False),
    )
    if collection_s == ".":
        return None

    return SearchRequest(search, collection_s.split())


def __do_search(cli: CLI, request: SearchRequest) -> list[Raindrop]:
    results = list()
    page: int = 0
    search_args = {"collection": request.collection}
    if request.search != WILDCARD:
        search_args["word"] = request.search
    while raindrops := Raindrop.search(
        cli.state.api,
        page=page,
        **search_args,
    ):
        for raindrop in raindrops:
            results.append(raindrop)
        page += 1
    return results


def _do_search(cli: CLI, request: SearchRequest) -> Optional[list[Raindrop]]:
    """Search across none, one or many collections for the respective search terms."""
    return_ = list()
    if request.collection_s:
        for collection_title in request.collection_s:
            request.collection = cli.state.find_collection(collection_title)
            return_.extend(__do_search(cli, request))
    else:
        request.collection = CollectionRef.All
        return_.extend(__do_search(cli, request))

    return return_


def _display_results(
    cli: CLI,
    request: SearchRequest,
    raindrops: list[Raindrop],
) -> None:
    if not raindrops:
        msg = f"Sorry, nothing found for search: '{request.search}'"
        if len(request.collection_s) == 1:
            msg += f" in collection: '{request.collection_s[0]}'."
        else:
            msg += f" across {len(request.collection_s)} collections."
        cli.console.print(msg)
        return

    table = Table()
    table.add_column("Collection", justify="left", style="#00ffff", no_wrap=True)
    table.add_column("Raindrop", style="#00ff00")
    for raindrop in raindrops:
        collection = cli.state.find_collection_by_id(raindrop.collection.id)
        table.add_row(collection.title, raindrop.title)
    cli.console.print(table)


def process(cli: CLI) -> None:
    """Top-level UI Controller for searching for bookmark(s)."""
    while True:
        request = _prompt_search(cli)
        if request is None:
            return None
        if request.search == WILDCARD and not request.collection_s:
            print("Sorry, wildcard search requires at least one collection.")
            continue

        # Do search and display results (after which we go back for another try.
        collection_text = ", ".join(request.collection_s)
        if request.search == WILDCARD:
            # Wildcard with at least one collection:
            spinner_text = f"Finding all raindrops in {collection_text}"
        elif not request.collection_s:
            # Not a wildcard but don't have a collection specified:
            spinner_text = f"Searching for '{request.search}' across all collections"
        else:
            # Not a wildcard but have collection(s) to search over:
            spinner_text = f"Searching for '{request.search}' in {collection_text}"

        with Spinner(f"{spinner_text}..."):
            raindrops = _do_search(cli, request)
        _display_results(cli, request, raindrops)
