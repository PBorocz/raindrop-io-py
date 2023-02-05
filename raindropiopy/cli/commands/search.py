"""Create a new Raindrop bookmark."""

from prompt_toolkit.completion import WordCompleter
from rich import print

# from raindropiopy.api import Collection, CollectionRef, Raindrop
from raindropiopy.cli import PROMPT_STYLE, prompt
from raindropiopy.cli.models.searchState import SearchState, WILDCARD
from raindropiopy.cli.commands import get_collection_s
from raindropiopy.cli.commands.help import help_search
from raindropiopy.cli.commands.view_edit import process as process_view_edit
from raindropiopy.cli.models.eventLoop import EventLoop
from raindropiopy.cli.models.spinner import Spinner


def __prompt_search_terms(el: EventLoop) -> tuple[bool, str | None]:
    """Prompt for all user response to perform a search, or None if user quits.

    Returns:
    - bool -> True if done with search?
    - str  -> Optional term(s) to search on
    """
    # What tag(s) to do allow for autocomplete?
    search_tags = [f"#{tag}" for tag in el.state.tags]
    completer = WordCompleter(search_tags)
    while True:
        response = el.session.prompt(
            prompt(("search term(s)?",)),
            completer=completer,
            style=PROMPT_STYLE,
            complete_while_typing=True,
            enable_history_search=False,
        )
        if response == "?":
            help_search(el)
        elif response in ("q", "."):
            return True, None
        elif response:
            return False, response

        # Otherwise, we fall through and try again, we need *some* search terms (even if "*" for wildcard)


def _prompt_search(el: EventLoop) -> SearchState | None:
    """Prompt for all responses necessary for a search, ie. terms and collections.

    Returns SearchState for a new search to be performed or None if we're done.
    """
    quit, search_term_s = __prompt_search_terms(el)
    if quit:
        return None

    collection_s = get_collection_s(el, ("search", "collection(s)?"))
    if collection_s == "." or collection_s is None:
        return None

    search_state = (
        SearchState()
    )  # Holds both search request information as we as search results.
    search_state.search = search_term_s
    search_state.collection_s = collection_s.split()
    return search_state


def process(el: EventLoop) -> None:
    """Top-level UI Controller for searching for bookmark(s)."""
    while True:
        search_state = _prompt_search(el)

        if search_state is None:
            return None  # We're REALLY done..

        elif search_state.search == WILDCARD and not search_state.collection_s:
            print("Sorry, wildcard search requires at least one collection.")
            continue

        # Do search and display results (after which we go back for another try.
        collection_text = ", ".join(search_state.collection_s)
        if search_state.search == WILDCARD:
            # Wildcard with at least one collection:
            spinner_text = f"Finding all raindrops in {collection_text}"
        elif not search_state.collection_s:
            # Not a wildcard but don't have a collection specified:
            spinner_text = (
                f"Searching for '{search_state.search}' across all collections"
            )
        else:
            # Not a wildcard but have collection(s) to search over:
            spinner_text = f"Searching for '{search_state.search}' in {collection_text}"

        ################################################################################
        # Do the query and display the results, transferring control over to view/edit
        ################################################################################
        with Spinner(f"{spinner_text}..."):
            search_state.query(el)

        search_state.display_results(el)

        if search_state.results:
            if not process_view_edit(el, search_state):
                return None

        # Otherwise, we go back an try to do another search..
