"""Display help."""
from rich.table import Table

from raindroppy.cli import COLOR_TABLE_COLUMN_1, COLOR_TABLE_COLUMN_2
from raindroppy.cli.models.eventLoop import EventLoop


def process(el: EventLoop) -> None:
    """Controller to display help."""
    el.console.print("Help is here, never fear!")


def help_search(el: EventLoop) -> None:
    """Render and display search help."""
    contents = (
        (
            "*",
            "All Raindrops (but you must specify at least one collection)",
        ),
        (
            "apple iphone",
            "Find items that contains such words in title, description, domain or in web page content",
        ),
        ("#coffee", "Find items that have a certain tag"),
        (
            "'superman vs. batman'",
            "Find items that contains exact phrase in title, description, domain or in web page content",
        ),
        (
            "-superman -#coffee",
            "Requires that the search results do not include this word or condition, eg. no superman, not tag coffee.",
        ),
        ("superman batman match:OR", "Find items with either search term"),
        ("created:2021-07-15 ", "Search for items created on a specific date"),
        ("created:2021-07 ", "Search for items created in a specific month"),
        ("created:2021 ", "Search for items created in a specific year"),
        ("created:>2021-07-15", "Put > in front of a date to find after specific date"),
        (
            "created:<2021-07-15",
            "Put < in front of a date to find before specific date",
        ),
        ("lastUpdate:2021-07-15", "Search for items updated in specific date"),
        ("link:dropbox", "Find items with a certain word (or words) in the URL"),
        ("link:'crunch base'", "Find items with a certain word (or words) in the URL"),
        ("type:link", "Find by type"),
        ("type:article", "Find by type"),
        ("type:image", "Find by type"),
        ("type:video", "Find by type"),
        ("type:document", "Find by type"),
        ("type:audio", "Find by type"),
        ("file:true", "Find files"),
        ("notag:true", "Find items without tags"),
    )
    table = Table(title=None, show_header=False)
    table.add_column("Search", style=COLOR_TABLE_COLUMN_1)
    table.add_column("Descript", style=COLOR_TABLE_COLUMN_2)
    for tpl in contents:
        table.add_row(*tpl)
    el.console.print(table)
