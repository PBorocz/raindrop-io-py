import os

from raindroppy import *

api = API(os.environ["RAINDROP_TOKEN"])

c = Collection.create(api, title="abcdef")
print(c.title)

c = Collection.update(api, id=c.id, title="12345")
print(c.title)

Collection.remove(api, id=c.id)
