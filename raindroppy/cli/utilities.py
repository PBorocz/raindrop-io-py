"""Miscellaneous Raindrop utilities used across the CLI."""
from beaupy.spinners import DOTS, Spinner
from models import RaindropState

from raindroppy.api import API, Collection, CollectionRef, Tag


def find_or_add_collection(api: API, collection_name: str) -> CollectionRef:
    """Find existing (or add new) Raindrop collection.

    Return the ID associated with the collection with specified
    collection_name (this doesn't seem to be a supported method of the
    Raindrop API directly). If collection is not found, add it!.
    """
    for collection in Collection.get_roots(api):
        if collection_name.casefold() == collection.values.get("title").casefold():
            return collection

    # Doesn't exist, create it!
    return Collection.create_link(api, title=collection_name)


def get_current_state(api: API, casefold: bool = True, debug: bool = False) -> RaindropState:
    """Return the current state of the Raindrop environment (ie. current collections and tags available)."""

    def _cf(casefold: bool, string: str) -> str:
        if casefold:
            return string.casefold()
        return string

    msg = "Getting current state of Raindrop environment..."
    if debug:
        print(msg)
    else:
        spinner = Spinner(DOTS, msg)
        spinner.start()

    # What collections do we currently have on Raindrop?
    collections: set[str] = set([_cf(casefold, root.title) for root in Collection.get_roots(api)])
    collections.union([_cf(casefold, child.title) for child in Collection.get_childrens(api)])

    # What tags we currently have available on Raindrop across *all* collections?
    tags: set[str] = set([_cf(casefold, tag.tag) for tag in Tag.get(api)])

    if not debug:
        spinner.stop()

    raindrop_state = RaindropState(collections=list(sorted(collections)), tags=list(sorted(tags)))
    raindrop_state._print()

    return raindrop_state
