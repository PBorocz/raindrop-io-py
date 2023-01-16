"""List all the collections associated with the token provided."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from raindroppy.api import API, Collection

load_dotenv()


def _print(c: Collection) -> None:
    print("---------------------------------------------------")
    print("id:               ", c.id)
    print("title:            ", c.title)
    print("user:             ", c.user.id)
    print("collaborators:    ", c.collaborators)
    print("public:           ", c.public)
    print("access.level:     ", c.access.level.value)
    print("access.draggable: ", c.access.draggable)
    print("color:            ", c.color)
    print("count:            ", c.count)
    print("cover:            ", c.cover)
    print("parent:           ", c.parent)
    print("sort:             ", c.sort)
    print("view:             ", c.view.value)
    print("expanded:         ", c.expanded)
    print("lastUpdate:       ", c.lastUpdate)
    print("created:          ", c.created)


# Note: we don't distinguish here between "root" and "child"
# collections, using the convenience method that collapses the two
# into a single list:
with API(os.environ["RAINDROP_TOKEN"]) as api:
    for collection in Collection.get_collections(api):
        _print(collection)
