"""Create a new Raindrop bookmark."""
from typing import Optional

from prompt_toolkit.completion import WordCompleter

from raindropiopy.api import Raindrop
from raindropiopy.cli import PROMPT_STYLE, prompt
from raindropiopy.cli.commands import (
    get_from_list,
    is_int,
    SearchRequest,
    SearchResults,
)
from raindropiopy.cli.commands.help import help_search
from raindropiopy.cli.commands.view_edit import process as process_view_edit
from raindropiopy.cli.models.eventLoop import EventLoop
from raindropiopy.cli.models.spinner import Spinner

WILDCARD: str = "*"
SEARCH_RESULTS: SearchResults = None  # Only a single set of search results at a time.


def __prompt_search_terms(el: EventLoop) -> tuple[bool, str | None, int | None]:
    """Prompt for all user response to perform a search, or None if user quits."""
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
            return True, None, None
        elif response:
            # Is response the (ith) number of a search result?
            if is_int(response) and SEARCH_RESULTS:
                return False, None, int(response) - 1  # Move back to 0-based indexing.
            return False, response, None

        # Otherwise, we fall through and try again, we need *some* search terms!


def _prompt_search(el: EventLoop) -> tuple[SearchRequest | None, str | None]:
    """Prompt for all responses necessary for a search, ie. terms and collections."""
    quit, search, ith = __prompt_search_terms(el)
    if quit:
        return None, None
    if ith is not None:
        return None, ith

    # What collection(s) to search across?
    collection_s = get_from_list(
        el,
        ("search", "collection(s)?"),
        el.state.get_collection_titles(exclude_unsorted=False),
    )
    if collection_s == ".":
        return None, None

    return SearchRequest(search, collection_s.split()), None


def __do_search(el: EventLoop, request: SearchRequest) -> list[Raindrop]:
    results = list()
    page: int = 0
    search_args = {"collection": request.collection}
    if request.search != WILDCARD:
        search_args["word"] = request.search
    while raindrops := Raindrop.search(
        el.state.api,
        page=page,
        **search_args,
    ):
        for raindrop in raindrops:
            results.append(raindrop)
        page += 1
    return results


def _do_search_wrapper(
    el: EventLoop,
    request: SearchRequest,
) -> Optional[list[Raindrop]]:
    """Search across 0, 1 or many collections for the respective search terms."""
    return_ = list()
    if request.collection_s:
        for collection_title in request.collection_s:
            request.collection = el.state.find_collection(collection_title)
            return_.extend(__do_search(el, request))
    else:
        return_.extend(__do_search(el, request))

    return SearchResults(results=return_)


def process(el: EventLoop) -> None:
    """Top-level UI Controller for searching for bookmark(s)."""
    global SEARCH_RESULTS
    while True:
        request, ith = _prompt_search(el)

        if request is None and ith is None:
            return None  # We're REALLY done..

        elif ith is not None:
            # Transfer control over to the view/edit logic
            SEARCH_RESULTS.selected = ith
            stay_in_search = process_view_edit(el, SEARCH_RESULTS)
            if not stay_in_search:
                return None  # We're also REALLY done..

            # Stay here but clear out our existing search results..
            SEARCH_RESULTS = None
            continue

        elif request.search == WILDCARD and not request.collection_s:
            print("Sorry, wildcard search requires at least one collection.")
            continue

        # Do search and display results (after which we go back for another try.
        collection_text = ", ".join(request.collection_s)
        if request.search == WILDCARD:
            # Wildcard with at least one collection:
            spinner_text = f"Finding all raindrops in {collection_text}"
        elif not request.collection_s:
            # Not a wildcard but don't have a collection specified:
            spinner_text = f"Searching for '{request.search}' across all collections"
        else:
            # Not a wildcard but have collection(s) to search over:
            spinner_text = f"Searching for '{request.search}' in {collection_text}"

        with Spinner(f"{spinner_text}..."):
            SEARCH_RESULTS = _do_search_wrapper(el, request)

        SEARCH_RESULTS.display_results(el, request)
