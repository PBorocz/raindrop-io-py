"""Add/Create a new file-based bookmark to Raindrop."""
from datetime import datetime
from typing import Final

from humanize import naturaltime
from prompt_toolkit.completion import WordCompleter

from api.models import Collection, CollectionRef
from cli import PROMPT_STYLE, cli_prompt, options_as_help
from cli.lui import LI


def _show_status(li: LI) -> None:
    """UI Controller for displaying current status."""
    human_diff = naturaltime(datetime.utcnow() - li.state.refreshed)
    li.console.print(f"Active User : {li.state.user.fullName}")
    li.console.print(f"Collections : {len(li.state.collections):,d}")
    li.console.print(f"Tags        : {len(li.state.tags):,d}")
    li.console.print(f"As Of       : {human_diff}")


def _show_collections(li: LI) -> None:
    """UI Controller for displaying current collections."""
    # FIXME: Add counts obo Unsorted Collection!

    def get_longest(collections: list[Collection, CollectionRef]) -> int:
        return max([len(collection.title) for collection in collections if collection.title])

    def get_total_raindrops(collections: list[Collection, CollectionRef]) -> int:
        return sum([collection.count for collection in collections if collection.count])

    max_len = get_longest(li.state.collections) + 1
    total = get_total_raindrops(li.state.collections)

    li.console.print(f"{'-'*max_len:{max_len}s} ---")
    for collection in li.state.collections:
        li.console.print(f"{collection.title:{max_len}s} {collection.count}")
    li.console.print(f"{'-'*max_len:{max_len}s} ---")
    li.console.print(f"{'Total':{max_len}s} {total:,d}")


def _show_tags(li: LI) -> None:
    """UI Controller for displaying current tags."""

    def get_longest(tags: list[str]) -> int:
        return max([len(tag) for tag in tags])

    width = get_longest(li.state.tags) + 1
    delim = "-" * width

    total = 0
    li.console.print(f"{delim:{width}s}")
    for tag in li.state.tags:
        li.console.print(f"{tag:{width}s}")
        total += 1
    li.console.print(f"{delim:{width}s}")
    li.console.print(f"{total:{width},d}")


def show_help(li: LI) -> None:
    """Display help about this set of commands"""
    li.console.print("status      : Show current status of Raindrop API connection.")
    li.console.print("collections : Display the Collections currently defined along with count of Raindrops in each.")
    li.console.print("tags        : Display the Tags currently defined.")
    li.console.print("refresh     : Refresh the list of Collections & Tags from Raindrop.")


def process(li: LI) -> None:
    """Top-level UI Controller for showing a set of statistics."""
    while True:
        options: Final = ["status", "collections", "tags", "refresh", "back"]
        completer: Final = WordCompleter(options)

        while True:
            try:
                li.console.print(options_as_help(options))
                response = li.session.prompt(
                    cli_prompt(("manage",)),
                    completer=completer,
                    style=PROMPT_STYLE,
                    complete_while_typing=True,
                    enable_history_search=False,
                )
                # Special cases...
                if response.casefold() in ("back", "."):
                    return None
                elif response.casefold() in ("h", "help"):
                    show_help(li)

                # Normal cases
                elif response.casefold() in ("?",):
                    li.console.print(options_as_help(options))
                elif response.casefold() == "status":
                    _show_status(li)
                elif response.casefold() == "collections":
                    _show_collections(li)
                elif response.casefold() == "tags":
                    _show_tags(li)
                elif response.casefold() == "refresh":
                    li.state.refresh()
                else:
                    li.console.print(f"Sorry, must be one of {options_as_help(options)}")
            except (KeyboardInterrupt, EOFError):
                return None
