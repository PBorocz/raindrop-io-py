"""Top level cli.commands dunder init, mostly common methods and data types."""
from dataclasses import dataclass
from typing import Iterable, Final, Optional

from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from rich.table import Table

from raindropiopy.api import Raindrop, Collection, CollectionRef
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


def get_title(el: EventLoop, prompts: list[str]) -> str | None:
    """Mini-event loop to prompt for a raindrop Title."""
    while True:
        title = el.session.prompt(prompt(prompts), style=PROMPT_STYLE)
        if title == "?":
            el.console.print(
                "We need a Raindrop title here, eg. 'Home Page for xxxyyy'",
            )
        elif title == "q":
            return None
        else:
            return title


def get_description(el: EventLoop, prompts: list[str]) -> str | None:
    """Mini-event loop to prompt for a raindrop Description (nee excerpt)."""
    while True:
        description = el.session.prompt(prompt(prompts), style=PROMPT_STYLE)
        if description == "?":
            el.console.print(
                "We need a Raindrop description here, eg. 'This was an interesting site.'",
            )
        elif description == "q":
            return None
        else:
            return description


def get_collection_s(el: EventLoop, prompts: list[str]) -> str | None:
    """Mini event-loop to prompt for one or many raindrop collections."""
    while True:
        collection_s = get_from_list(
            el,
            ("search", "collection(s)?"),
            el.state.get_collection_titles(exclude_unsorted=False),
        )
        if collection_s == ".":
            return None

        if collection_s:
            unrecognised_collections = list()
            current_collections = el.state.get_collection_titles(
                exclude_unsorted=True,
                casefold=True,
            )
            for collection in collection_s.split():
                if collection.casefold() not in current_collections:
                    unrecognised_collections.append(collection)
            if unrecognised_collections:
                print(
                    "Sorry, the following collections are NOT currently defined:",
                    end="",
                )
                print(", ".join(unrecognised_collections))
                print(
                    "Must be blank or one of one of: "
                    + ", ".join(el.state.get_collection_titles(exclude_unsorted=True)),
                )
                continue

        return collection_s


def get_confirmation(
    el: EventLoop,
    prompt: str,
    prompt_style: Style = PROMPT_STYLE,
) -> bool:
    """Ask the user for a confirmation to perform the specific prompt supplied."""
    el_prompt: Final = [("class:prompt", f"\n{prompt} ")]
    options: Final = ("yes", "Yes", "No", "no")
    completer: Final = WordCompleter(options)
    response = el.session.prompt(
        el_prompt,
        completer=completer,
        style=prompt_style,
        complete_while_typing=True,
        enable_history_search=False,
    )
    if response == "q":
        return None
    else:
        if response.lower() in ["yes", "y", "ye"]:
            return True
        return False


################################################################################
@dataclass
class SearchRequest:
    """Encapsulates all items necessary and possible for a Raindrop *search*."""

    search: str
    collection_s: tuple[str]

    # Used once *per* query, ie. for each collection in self.collection_s
    collection: Collection = CollectionRef.All


################################################################################
@dataclass
class SearchResults:
    """Encapsulate all aspects for a set of search results."""

    results: list[Raindrop]
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

        # Do we need to show the "Collections" column?
        collection_ids = set([raindrop.collection.id for _, raindrop in self])
        show_collection_name = True if len(collection_ids) > 1 else False

        # How many tag columns do we have?
        max_tags = max([len(raindrop.tags) for _, raindrop in self])

        # ----------
        # Columns
        # ----------
        table = Table(show_header=False)
        table.add_column("#", justify="center", style=COLOR_TABLE_COLUMN_1)
        if show_collection_name:
            table.add_column(
                "Collection",
                justify="left",
                style=COLOR_TABLE_COLUMN_1,
                no_wrap=True,
            )
        table.add_column("Raindrop", style=COLOR_TABLE_COLUMN_2)

        # Add as many columns as the max number of tags we'll have in our results:
        for ith in range(0, max_tags):
            table.add_column(str(ith), style=COLOR_TABLE_COLUMN_2)

        # ----------
        # Rows..
        # ----------
        for ith, raindrop in self:

            # We always show the the "selector" number:
            row = [f"{ith+1}"]

            # We may or may not show the collection name:
            if show_collection_name:
                collection = el.state.find_collection_by_id(raindrop.collection.id)
                row.append(str(collection.title))

            # We always show the title:
            row.append(str(raindrop.title))

            # Show the tags:
            for tag in sorted(raindrop.tags):
                row.append(tag)

            table.add_row(*row)

        # ----------
        # Finally, render the table
        # ----------
        el.console.print(table)

    def __iter__(self) -> Iterable[tuple]:
        """Return iterable over entries."""
        return iter(enumerate(self.results))

    def __len__(self) -> int:
        """Return the number of raindrops in our search results."""
        return len(self.results)
