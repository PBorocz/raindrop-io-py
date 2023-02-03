"""Create a new Raindrop bookmark."""
from dataclasses import dataclass
from typing import Final

from prompt_toolkit.completion import WordCompleter
from rich.table import Table

from raindropiopy.api import Collection
from raindropiopy.cli import (
    COLOR_TABLE_COLUMN_1,
    COLOR_TABLE_COLUMN_2,
    PROMPT_STYLE,
    prompt,
    options_as_help,
)
from raindropiopy.cli.commands import SearchResults, is_int
from raindropiopy.cli.models.eventLoop import EventLoop

WILDCARD = "*"


@dataclass
class SearchRequest:
    """Encapsulates all items necessary and possible for a Raindrop *search*."""

    search: str
    collection_s: tuple[str]
    collection: Collection = None


def _prompt_view_edit(el: EventLoop, search_results: SearchResults) -> str:
    """Prompt for the next thing to do with the specified raindrop."""
    prompt_addendum = f"{search_results.selected+1}/{len(search_results)}"
    while True:
        options: Final = ("view", "list", "edit", "open", "delete", "back/.")
        options_title: Final = options_as_help(options)
        el.console.print(options_title)
        return el.session.prompt(
            prompt(("search results", prompt_addendum)),
            completer=WordCompleter(options),
            style=PROMPT_STYLE,
            complete_while_typing=True,
            enable_history_search=False,
        )


def _view_raindrop(el: EventLoop, search_results: SearchResults) -> None:
    """Display the currently selected raindrop."""
    table = Table()
    table.add_column(
        "Attribute",
        justify="left",
        style=COLOR_TABLE_COLUMN_1,
        no_wrap=True,
    )
    table.add_column("Value", justify="left", style=COLOR_TABLE_COLUMN_2)

    # Lookup the raindrop to be displayed:
    raindrop = search_results.get_selected()

    # Disambiguate some attributes for easier viewing:
    raindrop._collection = raindrop.collection.id
    raindrop._tags = ", ".join(raindrop.tags)
    raindrop._created = str(raindrop.created).split(".")[0]
    raindrop._updated = str(raindrop.lastUpdate).split(".")[0]
    if raindrop._updated == raindrop._created:
        raindrop._updated = None

    for attr, title in [
        ["_collection", "Collection"],
        ["title", "Title"],
        ["type", "Type"],
        ["excerpt", "Description"],
        ["_tags", "Tags"],
        ["_created", "Created"],
        ["_updated", "Updated"],
        ["link", "Link"],
    ]:
        if value := getattr(raindrop, attr, "-"):
            table.add_row(title, str(value))

    el.console.print(table)


def process(el: EventLoop, search_results: SearchResults) -> bool:
    """Top-level UI Controller for viewing / edit a bookmark(s)."""
    _view_raindrop(el, search_results)
    while True:

        response = _prompt_view_edit(el, search_results)

        if response in ("b", "back", "."):
            return True

        elif response in ("q", "quit"):
            return False

        elif response.casefold() in ("v", "view"):
            _view_raindrop(el, search_results)

        elif response.casefold() in ("l", "list"):
            search_results.display_results(el, None)

        elif response.casefold() in ("d", "delete"):
            print("Sorry, that option is still under development!")

        elif response.casefold() in ("e", "edit"):
            print("Sorry, that option is still under development!")

        elif response.casefold() in ("o", "open"):
            print("Sorry, that option is still under development!")

        elif is_int(response):
            search_results.selected = int(response) - 1
            _view_raindrop(el, search_results)
