"""Top level cli.commands dunder init, mostly common methods and data types."""
from dataclasses import dataclass
from typing import Iterable

from rich.table import Table

from raindropiopy.api import API, Collection, CollectionRef, Raindrop
from raindropiopy.cli import COLOR_TABLE_COLUMN_1, COLOR_TABLE_COLUMN_2
from raindropiopy.cli.models.eventLoop import EventLoop

WILDCARD: str = "*"


################################################################################
@dataclass
class SearchState:
    """Encapsulates all items necessary and possible for a Raindrop *search* and associated *results*."""

    # Search REQUEST:
    search: str = None
    collection_s: tuple[str] = None

    # Search RESULTS:
    results: list[Raindrop] = None
    selected: int | None = None

    def get_selected(self, ith: int) -> Raindrop | None:
        """Return the Raindrop associated with the ith entry in our results."""
        self.selected = ith - 1
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

    def display_results(self, el: EventLoop) -> None:
        """Display the list of raindrops in this package of search results (IF we got any!)."""
        if not self.results:
            if self.search:
                msg = f"Sorry, nothing found for search: '{self.search}'"
                if len(self.collection_s) == 0:
                    msg += " across ALL collections."
                elif len(self.collection_s) == 1:
                    msg += f" in collection: '{self.collection_s[0]}'."
                else:
                    msg += f" across {len(self.collection_s)} collections."
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

    def prompt(self) -> str:
        """Determine the appropriate prompt "addendum" based on current search state."""
        if self.selected is not None:
            return f"{self.selected + 1}/{len(self)}"
        return f"-/{len(self)}"

    def query(self, el: EventLoop):
        """Query Raindrop.io across 0, 1 or many collections for the respective search terms."""

        def _query_collection(
            api: API,
            search: str,
            collection: Collection | None,
        ) -> list[Raindrop]:
            # Set the search arguments:
            search_args = {"collection": collection}
            if search != WILDCARD:
                search_args["word"] = search

            results: list[Raindrop] = list()
            page: int = 0
            while raindrops := Raindrop.search(api, page=page, **search_args):
                for raindrop in raindrops:
                    results.append(raindrop)
                page += 1
            return results

        # Query based on whether or not we have specific collection(s) to query over:
        self.results: list[Raindrop] = list()
        if self.collection_s:
            for collection_title in self.collection_s:
                self.results.extend(
                    _query_collection(
                        el.state.api,
                        self.search,
                        el.state.find_collection(collection_title),
                    ),
                )
        else:
            self.results.extend(
                _query_collection(el.state.api, self.search, CollectionRef.All),
            )

    def __iter__(self) -> Iterable[tuple]:
        """Return iterable over entries."""
        return iter(enumerate(self.results))

    def __len__(self) -> int:
        """Return the number of raindrops in our search results."""
        return len(self.results)
