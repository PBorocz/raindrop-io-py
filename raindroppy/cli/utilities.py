"""Miscellaneous Raindrop utilities used across the CLI."""
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from api import API, Collection, CollectionRef


def get_user_history_path():
    history_path = Path("~/.config/raindroppy").expanduser()
    history_path.mkdir(parents=True, exist_ok=True)

    history_file = history_path / Path(".cli_history")
    if not history_file.exists():
        open(history_file, "a").close()
    return history_file


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


def validate_url(url: str) -> Optional[str]:
    """Validate the url provided, returning a message if invalid, None otherwise"""
    if not url:
        return "Sorry, you need to specify a valid URL, e.g. https://www.msn.com"
    try:
        parts = urlparse(url)
        if all([parts.scheme, parts.netloc]):
            return None
    except ValueError:
        pass
    return f"Sorry, URL provided {url} isn't valid."


def validate_site(url: str) -> Optional[str]:
    """Validate that the url provided actually goes to a live site, return message if not."""
    return None
    # FIXME!!
