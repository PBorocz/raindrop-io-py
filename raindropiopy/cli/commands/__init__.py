"""Top level cli.commands dunder init, mostly common methods."""
from dataclasses import dataclass, field
from typing import Iterable, Final, Optional

from prompt_toolkit.completion import WordCompleter
from rich.table import Table

from raindropiopy.api import Raindrop, Collection
from raindropiopy.cli import COLOR_TABLE_COLUMN_1, COLOR_TABLE_COLUMN_2
from raindropiopy.cli import PROMPT_STYLE, prompt
from raindropiopy.cli.models.eventLoop import EventLoop


def is_int(string: str) -> bool:
    """Make (compound) conditionals easier."""
    try:
        int(string)
        return True
    except ValueError:
        return False


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


################################################################################
@dataclass
class SearchRequest:
    """Encapsulates all items necessary and possible for a Raindrop *search*."""

    search: str
    collection_s: tuple[str]
    collection: Collection = None


################################################################################
@dataclass
class SearchResults:
    """Encapsulate all aspects for a set of search results."""

    results: list[Raindrop] = field(default_factory=list)
    selected: int | None = None

    def get_selected(self) -> Raindrop | None:
        """Return the Raindrop associated with the ith entry in our results."""
        if self.selected is None:
            return None
        try:
            return self.results[self.selected]
        except IndexError:
            return None

    def get(self, ith: int) -> str | None:
        """Return the Raindrop associated with the ith entry in our results."""
        try:
            return self.results[ith]
        except IndexError:
            return None

    def display_results(self, el: EventLoop, request: SearchRequest | None) -> None:
        """Display the list of raindrops in this package of search results."""
        if not self.results:
            if request:
                msg = f"Sorry, nothing found for search: '{request.search}'"
                if len(request.collection_s) == 1:
                    msg += f" in collection: '{request.collection_s[0]}'."
                else:
                    msg += f" across {len(request.collection_s)} collections."
                el.console.print(msg)
            return

        table = Table()
        table.add_column("#", justify="center", style=COLOR_TABLE_COLUMN_1)
        table.add_column(
            "Collection",
            justify="left",
            style=COLOR_TABLE_COLUMN_1,
            no_wrap=True,
        )
        table.add_column("Raindrop", style=COLOR_TABLE_COLUMN_2)
        for ith, raindrop in self:
            collection = el.state.find_collection_by_id(raindrop.collection.id)
            table.add_row(f"{ith+1}", collection.title, raindrop.title)
        el.console.print(table)

    def __iter__(self) -> Iterable[tuple]:
        """Return iterable over entries."""
        return iter(enumerate(self.results))

    def __len__(self) -> int:
        """Return the number of raindrops in our search results."""
        return len(self.results)
