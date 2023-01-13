"""Add/Create a new file-based bookmark to Raindrop."""
from datetime import datetime
from typing import Final

from humanize import naturaltime
from prompt_toolkit.completion import WordCompleter

from raindroppy.api.models import Collection, CollectionRef
from raindroppy.cli import PROMPT_STYLE, cli_prompt, options_as_help
from raindroppy.cli.cli import CLI


def get_total_raindrops(collections: list[Collection, CollectionRef]) -> int:
    """Return the total number of Raindrops *associated with named collections*"""
    return sum([collection.count for collection in collections if collection.count])


def _show_status(cli: CLI) -> None:
    """UI Controller for displaying current status."""
    human_diff = naturaltime(datetime.utcnow() - cli.state.refreshed)
    cli.console.print(f"Active User : {cli.state.user.fullName}")
    cli.console.print(f"Raindrops   : {get_total_raindrops(cli.state.collections):,d}")
    cli.console.print(f"Collections : {len(cli.state.collections):,d}")
    cli.console.print(f"Tags        : {len(cli.state.tags):,d}")
    cli.console.print(f"As Of       : {human_diff}")


def _show_collections(cli: CLI) -> None:
    """UI Controller for displaying current collections."""
    # FIXME: Add counts obo Unsorted Collection!

    def get_longest(collections: list[Collection, CollectionRef]) -> int:
        return max([len(collection.title) for collection in collections if collection.title])

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

    width = get_longest(cli.state.tags) + 1
    delim = "-" * width

    total = 0
    cli.console.print(f"{delim:{width}s}")
    for tag in cli.state.tags:
        cli.console.print(f"{tag:{width}s}")
        total += 1
    cli.console.print(f"{delim:{width}s}")
    cli.console.print(f"{total:{width},d}")


def show_help(cli: CLI) -> None:
    """Display help about this set of commands"""
    cli.console.print("status      : Show current status of Raindrop API connection.")
    cli.console.print("collections : Display the Collections currently defined along with count of Raindrops in each.")
    cli.console.print("tags        : Display the Tags currently defined.")
    cli.console.print("refresh     : Refresh the list of Collections & Tags from Raindrop.")


def process(cli: CLI) -> None:
    """Controller for managing the Raindrop environment, including showing statistics."""
    while True:
        options: Final = ["status", "collections", "tags", "refresh", "back", "."]
        completer: Final = WordCompleter(options)

        while True:
            try:
                cli.console.print(options_as_help(options))
                response = cli.session.prompt(
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
                    show_help(cli)

                # Normal cases
                elif response.casefold() in ("?",):
                    cli.console.print(options_as_help(options))
                elif response.casefold() == "status":
                    _show_status(cli)
                elif response.casefold() == "collections":
                    _show_collections(cli)
                elif response.casefold() == "tags":
                    _show_tags(cli)
                elif response.casefold() == "refresh":
                    cli.state.refresh()
                else:
                    cli.console.print(f"Sorry, must be one of {options_as_help(options)}")
            except (KeyboardInterrupt, EOFError):
                return None