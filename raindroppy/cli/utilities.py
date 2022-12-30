"""Miscellaneous Raindrop utilities used across the CLI."""
from beaupy.spinners import DOTS, Spinner
from models import RaindropState
from raindropio import Collection, CollectionRef, Tags, api


def find_or_add_collection(api, collection_name: str) -> CollectionRef:
    """Find existing (or add new) Raindrop collection.

    Return the ID associated with the collection with specified
    collection_name (this doesn't seem to be a supported method of the
    Raindrop API directly). If collection is not found, add it!.
    """
    for collection in Collection.get_roots(api):
        if collection_name.casefold() == collection.values.get("title").casefold():
            return collection

    # Doesn't exist, create it!
    print("Creating!")
    return Collection.create(api, title=collection_name)


def get_existing_state(api: api.API, casefold=True) -> RaindropState:
    """Return the current state of the Raindrop environment.

    Specifically: the current list of collections and tags available.
    """

    def _cf(string: str) -> str:
        if casefold:
            return string.casefold()
        return string

    spinner = Spinner(DOTS, "Getting current state of Raindrop environment...")
    spinner.start()

    # What collections do we currently have on Raindrop?
    collections: set[str] = set([_cf(root.title) for root in Collection.get_roots(api)])
    collections.union([_cf(child.title) for child in Collection.get_childrens(api)])

    # What tags we currently have available on Raindrop?
    tags: set[str] = set([_cf(tag.tag) for tag in Tags.get(api)])
    raindrop_state = RaindropState(collections=list(sorted(collections)), tags=list(sorted(tags)))

    spinner.stop()
    raindrop_state._print()

    return raindrop_state
