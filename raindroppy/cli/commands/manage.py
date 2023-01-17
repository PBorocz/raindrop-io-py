"""Add/Create a new file-based bookmark to Raindrop."""
from datetime import datetime
from typing import Final

from humanize import naturaltime
from prompt_toolkit.completion import WordCompleter
from rich.table import Table

from raindroppy.api.models import Collection, CollectionRef
from raindroppy.cli import (
    COLOR_TABLE_COLUMN_1,
    COLOR_TABLE_COLUMN_2,
    PROMPT_STYLE,
    cli_prompt,
    options_as_help,
)
from raindroppy.cli.cli import CLI


def get_total_raindrops(collections: list[Collection, CollectionRef]) -> int:
    """Return the total number of Raindrops *associated with named collections*."""
    return sum([collection.count for collection in collections if collection.id > 0])


def _show_status(cli: CLI) -> None:
    """UI Controller for displaying current status."""
    human_diff = naturaltime(datetime.utcnow() - cli.state.refreshed)
    table = Table(title=None, show_header=False)
    table.add_column("parm", style=COLOR_TABLE_COLUMN_1, no_wrap=True)
    table.add_column("data", style=COLOR_TABLE_COLUMN_2, justify="right")
    table.add_row("Active User", f"{cli.state.user.fullName}")
    table.add_row("Raindrops", f"{get_total_raindrops(cli.state.collections):,d}")
    table.add_row("Collections", f"{len(cli.state.collections):,d}")
    table.add_row("Tags", f"{len(cli.state.tags):,d}")
    table.add_row("As Of", f"{human_diff}")
    cli.console.print(table)


def _show_collections(cli: CLI) -> None:
    """Displaying current collections."""
    total = get_total_raindrops(cli.state.collections)
    table = Table(title=None, show_header=False)
    table.add_column("Collection", style=COLOR_TABLE_COLUMN_1, no_wrap=True)
    table.add_column("Count", style=COLOR_TABLE_COLUMN_2, justify="right")
    for collection in cli.state.collections:
        table.add_row(collection.title, f"{collection.count:,d}")
    table.add_section()
    table.add_row("Total Raindrops", f"{total:,d}")
    cli.console.print(table)


def _show_tags(cli: CLI) -> None:
    """Display current tags."""
    total = 0
    table = Table(title=None, show_header=False)
    table.add_column("Tag", style=COLOR_TABLE_COLUMN_1, no_wrap=True)
    for tag in cli.state.tags:
        table.add_row(tag)
        total += 1
    table.add_section()
    table.add_row(f"{total:,d}")
    cli.console.print(table)


def show_help(cli: CLI) -> None:
    """Display help about this set of commands."""
    cli.console.print("status      : Show current status of Raindrop API connection.")
    cli.console.print(
        "collections : Display the Collections currently defined along with count of Raindrops in each.",
    )
    cli.console.print("tags        : Display the Tags currently defined.")
    cli.console.print(
        "refresh     : Refresh the list of Collections & Tags from Raindrop.",
    )


def process(cli: CLI) -> None:
    """Controller for managing the Raindrop environment, including showing statistics."""
    while True:
        options: Final = [
            "(s)tatus",
            "(c)ollections",
            "(t)ags",
            "(r)efresh",
            "(b)ack or .",
        ]
        completer: Final = WordCompleter(options)

        while True:
            cli.console.print(options_as_help(options))
            response = cli.session.prompt(
                cli_prompt(("manage",)),
                completer=completer,
                style=PROMPT_STYLE,
                complete_while_typing=True,
                enable_history_search=False,
            )
            # Special cases...
            if response.casefold() in ("back", "b", "."):
                return None
            elif response.casefold() in ("help", "h"):
                show_help(cli)

            # Normal cases
            elif response.casefold() in ("?",):
                cli.console.print(options_as_help(options))
            elif response.casefold() in ("status", "s"):
                _show_status(cli)
            elif response.casefold() in ("collections", "c"):
                _show_collections(cli)
            elif response.casefold() in ("tags", "t"):
                _show_tags(cli)
            elif response.casefold() in ("refresh", "r"):
                cli.state.refresh()
            else:
                cli.console.print(
                    f"Sorry, must be one of {options_as_help(options)}",
                )
