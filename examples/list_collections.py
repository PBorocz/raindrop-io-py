"""List all the collections associated with the token provided."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from raindropiopy import API, Collection

load_dotenv()


def _print(key, value):
    print(f"{key:.<24} {value!s}")


def print_collection(coll: Collection) -> None:
    """Print the collection, nicely."""
    print("---------------------------------------------------")
    _print("id", coll.id)
    _print("title", coll.title)
    _print("access.draggable", coll.access.draggable)
    _print("access.level", coll.access.level.value)
    _print("collaborators", coll.collaborators)
    _print("color", coll.color)
    _print("count", coll.count)
    _print("cover", coll.cover)
    _print("created", coll.created)
    _print("expanded", coll.expanded)
    _print("lastUpdate", coll.lastUpdate)
    _print("parent", coll.parent)
    _print("public", coll.public)
    _print("sort", coll.sort)
    _print("user", coll.user.id)
    _print("view", coll.view.value)
    for attr, value in coll.internal_.items():
        _print(f"internal_{attr}", value)


# Note: we don't distinguish here between "root" and "child"
# collections, using the convenience method that collapses the two
# into a single list:
with API(os.environ["RAINDROP_TOKEN"]) as api:
    for collection in Collection.get_collections(api):
        print_collection(collection)
