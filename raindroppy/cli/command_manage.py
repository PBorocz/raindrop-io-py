"""Add/Create a new file-based bookmark to Raindrop."""
from datetime import datetime

from api.models import Collection, CollectionRef
from beaupy import select
from humanize import naturaltime
from run import CLI  # Typing

CURSOR_STYLE = "red"


def _show_status(cli: CLI) -> None:
    """UI Controller for displaying current status."""
    human_diff = naturaltime(datetime.utcnow() - cli.state.refreshed)
    cli.console.print(f"Active User : {cli.state.user.fullName}")
    cli.console.print(f"Collections : {len(cli.state.collections):,d}")
    cli.console.print(f"Tags        : {len(cli.state.tags):,d}")
    cli.console.print(f"As Of       : {human_diff}")


def _show_collections(cli: CLI) -> None:
    """UI Controller for displaying current collections."""
    # FIXME: Add counts obo Unsorted Collection!

    def get_longest(collections: list[Collection, CollectionRef]) -> int:
        return max([len(collection.title) for collection in collections if collection.title])

    def get_total_raindrops(collections: list[Collection, CollectionRef]) -> int:
        return sum([collection.count for collection in collections if collection.count])

    max_len = get_longest(cli.state.collections) + 1
    total = get_total_raindrops(cli.state.collections)

    cli.console.print(f"{'-'*max_len:{max_len}s} ---")
    for collection in cli.state.collections:
        cli.console.print(f"{collection.title:{max_len}s} {collection.count}")
    cli.console.print(f"{'-'*max_len:{max_len}s} ---")
    cli.console.print(f"{'Total':{max_len}s} {total:,d}")


def _show_tags(cli: CLI) -> None:
    """UI Controller for displaying current tags."""

    def get_longest(tags: list[str]) -> int:
        return max([len(tag) for tag in tags])

    max_len = get_longest(cli.state.tags) + 1

    total = 0
    cli.console.print(f"{'-'*max_len:{max_len}s} ---")
    for tag in cli.state.tags:
        cli.console.print(f"{tag:{max_len}s}")
        total += 1
    cli.console.print(f"{'-'*max_len:{max_len}s} ---")
    cli.console.print(f"{'Total':{max_len}s} {total:,d}")


def process(cli: CLI) -> None:
    """Top-level UI Controller for showing a set of statistics."""
    while True:

        options = [
            "Show Status",
            "Show All Collections",
            "Show All Tags",
            "Refresh Local Environment From Raindrop",
            "(Back)",
        ]

        response = select(options, return_index=True)

        if response == 0:
            _show_status(cli)
        elif response == 1:
            _show_collections(cli)
        elif response == 2:
            _show_tags(cli)
        elif response == 3:
            cli.state.refresh()
        elif response == 4:
            return None
