"""Create a new Raindrop bookmark."""
import webbrowser
from typing import Final

from prompt_toolkit.completion import WordCompleter
from rich.table import Table

from raindropiopy.cli import (
    COLOR_TABLE_COLUMN_1,
    COLOR_TABLE_COLUMN_2,
    PROMPT_STYLE,
    PROMPT_STYLE_WARNING,
    WARNING,
    prompt,
    options_as_help,
)
from raindropiopy.api.models import Raindrop
from raindropiopy.cli.commands import get_confirmation, get_from_list, is_int
from raindropiopy.cli.models.eventLoop import EventLoop
from raindropiopy.cli.models.searchState import SearchState
from raindropiopy.cli.models.spinner import Spinner
from raindropiopy.cli.commands import get_title, get_description


def _prompt_view_edit(el: EventLoop, search_state: SearchState) -> str:
    """Prompt for the next thing to do with the specified raindrop."""
    while True:
        options: Final = ("open", "edit", "view", "list", "delete", "requery", "back/.")
        options_title: Final = options_as_help(options)
        el.console.print(options_title)
        response = el.session.prompt(
            prompt(("search results", search_state.prompt())),
            completer=WordCompleter(options),
            style=PROMPT_STYLE,
            complete_while_typing=True,
            enable_history_search=False,
        )
        if is_int(response) and search_state.results:
            i_response = int(response)
            if 1 <= i_response <= len(search_state):
                return int(response)
            else:
                print(
                    f"[{WARNING}]Sorry, raindrop selector must be between 1 and {len(search_state)}.",
                )
                continue
        return response


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
    raindrop._created = raindrop.created.isoformat().split("T")[0]
    raindrop._updated = raindrop.lastUpdate.isoformat().split("T")[0]
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
    search_state: SearchState,
    raindrop: Raindrop,
) -> None:
    """Edit selected attributes of the currently selected raindrop."""
    _view_raindrop(el, raindrop)

    # What attribute to edit?
    search_context = search_state.prompt()
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
        title = get_title(el, prompts)
        with Spinner("Updating Raindrop..."):
            Raindrop.update(el.state.api, id=raindrop.id, title=title)

    elif response.casefold().startswith("d"):
        prompts = ("search results", search_context, "edit", "description?")
        excerpt = get_description(el, prompts)
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


def process(el: EventLoop, search_state: SearchState) -> bool:
    """Top-level UI Controller for viewing / edit a bookmark(s).

    Return:
    - quit : Should we "quit" after this invocation?
    """
    while True:
        response = _prompt_view_edit(el, search_state)

        if is_int(response):
            raindrop = search_state.get_selected(int(response))
            _view_raindrop(el, raindrop)

        elif response.casefold() in ("b", "back", ".", "q", "quit"):
            return True

        elif response.casefold() in ("v", "view"):
            _view_raindrop(el, raindrop)

        elif response.casefold() in ("o", "open"):
            _open_raindrop(el, raindrop)

        elif response.casefold() in ("l", "list"):
            search_state.display_results(el)

        elif response.casefold() in ("r", "requery"):
            search_state.query(el)
            search_state.display_results(el)

        elif response.casefold() in ("d", "delete"):
            _delete_raindrop(el, raindrop)
            search_state.query(el)
            search_state.display_results(el)

        elif response.casefold() in ("e", "edit"):
            _edit_raindrop(el, search_state, raindrop)
            search_state.query(el)
            search_state.display_results(el)
