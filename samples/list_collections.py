# type: ignore
import os

from raindroppy.api import *

api = API(os.environ["RAINDROP_TOKEN"])


def print_collection(c):
    print("------------------------------")
    print("id", c.id)
    print("access", c.access.level, c.access.draggable)
    print("collaborators", c.collaborators)
    print("color", c.color)
    print("count", c.count)
    print("cover", c.cover)
    print("created", c.created)
    print("expanded", c.expanded)
    print("lastUpdate", c.lastUpdate)
    print("parent", c.parent)
    print("public", c.public)
    print("sort", c.sort)
    print("title", c.title)
    print("user", c.user)
    print("view", c.view)


for c in Collection.get_roots(api):
    print_collection(c)

print("---- children")
for c in Collection.get_childrens(api):
    print_collection(c)
