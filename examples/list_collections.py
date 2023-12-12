"""List all the collections associated with the token from our current environment."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from raindropiopy import API, Collection

load_dotenv()


def print_collection(collection: Collection) -> None:
    """Print the collection, somewhat nicely."""
    fprint = lambda key, value: print(f"{key:.<24} {value!s}")  # noqa: E731

    print("---------------------------------------------------")
    fprint("id", collection.id)
    fprint("title", collection.title)
    fprint("parent", collection.parent)
    fprint("access.draggable", collection.access.draggable)
    fprint("access.level", collection.access.level.value)
    fprint("collaborators", collection.collaborators)
    fprint("color", collection.color)
    fprint("count", collection.count)
    fprint("cover", collection.cover)
    fprint("created", collection.created)
    fprint("expanded", collection.expanded)
    fprint("public", collection.public)
    fprint("sort", collection.sort)
    fprint("user", collection.user.id)
    fprint("view", collection.view.value)
    fprint("last_update", collection.last_update)

    for attr, value in collection.other.items():
        fprint(f"other.{attr}", value)


# Note: we don't distinguish here between "root" and "child"
# collections, instead using the convenience method that collapses the
# two into a single list (use collection.parent to distinguish).
with API(os.environ["RAINDROP_TOKEN"]) as api:
    for collection in Collection.get_collections(api):
        print_collection(collection)
