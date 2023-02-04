"""Create a new Raindrop bookmark."""
import humanize
import webbrowser
from typing import Final

from prompt_toolkit.completion import WordCompleter
from rich.table import Table

from raindropiopy.cli import (
    COLOR_TABLE_COLUMN_1,
    COLOR_TABLE_COLUMN_2,
    PROMPT_STYLE,
    PROMPT_STYLE_WARNING,
    prompt,
    options_as_help,
)
from raindropiopy.api.models import Raindrop
from raindropiopy.cli.commands import (
    get_confirmation,
    get_from_list,
    SearchResults,
    is_int,
)
from raindropiopy.cli.models.eventLoop import EventLoop
from raindropiopy.cli.models.spinner import Spinner


# FIXME: Normalise and put into commands/__init__.py to share with search.py
def __get_title(el: EventLoop, prompts: list[str]) -> str | None:
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


# FIXME: Normalise and put into commands/__init__.py to share with search.py
def __get_description(el: EventLoop, prompts: list[str]) -> str | None:
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


def _view_raindrop(el: EventLoop, raindrop: Raindrop) -> None:
    """Display the currently selected raindrop."""
    table = Table(show_header=False)
    table.add_column(
        "Attribute",
        justify="left",
        style=COLOR_TABLE_COLUMN_1,
        no_wrap=True,
    )
    table.add_column("Value", justify="left", style=COLOR_TABLE_COLUMN_2)

    # Disambiguate some attributes for easier viewing:
    raindrop._collection = el.state.find_collection_by_id(raindrop.collection.id).title
    raindrop._tags = ", ".join(raindrop.tags)
    raindrop._type = raindrop.type.value.title()
    raindrop._created = humanize.naturaldate(raindrop.created).title()
    raindrop._updated = humanize.naturaldate(raindrop.lastUpdate).title()
    if raindrop._updated == raindrop._created:
        raindrop._updated = None

    for attr, title in [
        ["_collection", "Collection"],
        ["title", "Title"],
        ["excerpt", "Description"],
        ["_tags", "Tags"],
        ["_type", "Type"],
        ["_created", "Created"],
        ["_updated", "Updated"],
    ]:
        if value := getattr(raindrop, attr, "-"):
            table.add_row(title, str(value))

    el.console.print(table)


def _edit_raindrop(
    el: EventLoop,
    search_results: SearchResults,
    raindrop: Raindrop,
) -> None:
    """Edit selected attributes of the currently selected raindrop."""
    _view_raindrop(el, raindrop)

    # What attribute to edit?
    search_context = f"{search_results.selected+1}/{len(search_results)}"
    options: Final = ("title", "tags", "description", "back/.")
    options_title: Final = options_as_help(options, 2)
    el.console.print(options_title)
    prompts = ("search results", search_context, "edit")
    response = el.session.prompt(
        prompt(prompts),
        completer=WordCompleter(options),
        style=PROMPT_STYLE,
        complete_while_typing=True,
        enable_history_search=False,
    )
    if response.casefold() in ("b", "back", "."):
        return

    elif response.casefold().startswith("ta"):
        prompts = ("search results", search_context, "edit", "tag(s)?")
        tags = get_from_list(el, prompts, list(el.state.tags))
        with Spinner("Updating Raindrop..."):
            Raindrop.update(el.state.api, id=raindrop.id, tags=tags)

    elif response.casefold().startswith("ti"):
        prompts = ("search results", search_context, "edit", "title?")
        title = __get_title(el, prompts)
        with Spinner("Updating Raindrop..."):
            Raindrop.update(el.state.api, id=raindrop.id, title=title)

    elif response.casefold().startswith("d"):
        prompts = ("search results", search_context, "edit", "description?")
        excerpt = __get_description(el, prompts)
        with Spinner("Updating Raindrop..."):
            Raindrop.update(el.state.api, id=raindrop.id, excerpt=excerpt)

    return


def _open_raindrop(el: EventLoop, raindrop: Raindrop) -> None:
    """Open the currently selected raindrop."""
    webbrowser.open(raindrop.link)


def _delete_raindrop(el: EventLoop, raindrop: Raindrop) -> None:
    """Delete the currently selected raindrop (after confirmation)."""
    _view_raindrop(el, raindrop)
    if get_confirmation(el, "Are you sure?", PROMPT_STYLE_WARNING):
        with Spinner(f"Deleting Raindrop: [italic]{raindrop.title}[/]..."):
            Raindrop.remove(el.state.api, id=raindrop.id)


def _prompt_view_edit(el: EventLoop, search_results: SearchResults) -> str:
    """Prompt for the next thing to do with the specified raindrop."""
    prompt_addendum = f"{search_results.selected+1}/{len(search_results)}"
    while True:
        options: Final = ("open", "edit", "view", "list", "delete", "back/.")
        options_title: Final = options_as_help(options)
        el.console.print(options_title)
        return el.session.prompt(
            prompt(("search results", prompt_addendum)),
            completer=WordCompleter(options),
            style=PROMPT_STYLE,
            complete_while_typing=True,
            enable_history_search=False,
        )


def process(el: EventLoop, search_results: SearchResults) -> bool:
    """Top-level UI Controller for viewing / edit a bookmark(s)."""
    raindrop = (
        search_results.get_selected()
    )  # Lookup the particular raindrop to be worked on..
    _view_raindrop(el, raindrop)  # and display it!
    while True:

        response = _prompt_view_edit(el, search_results)

        if response.casefold() in ("b", "back", "."):
            return True

        elif response.casefold() in ("q", "quit"):
            return False

        if response.casefold() in ("v", "view"):
            _view_raindrop(el, raindrop)

        elif response.casefold() in ("o", "open"):
            _open_raindrop(el, raindrop)

        elif response.casefold() in ("l", "list"):
            search_results.display_results(el, None)

        elif response.casefold() in ("d", "delete"):
            _delete_raindrop(el, raindrop)
            return True  # At this point, the search results are incomplete, go back/up

        elif response.casefold() in ("e", "edit"):
            _edit_raindrop(el, search_results, raindrop)

        elif is_int(response):
            search_results.selected = (
                int(response) - 1
            )  # Convert from user-based to list indexing
            raindrop = search_results.get_selected()
            _view_raindrop(el, raindrop)
