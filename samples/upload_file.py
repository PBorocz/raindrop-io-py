import os
from pathlib import Path

from dotenv import load_dotenv

from raindroppy.api import *

load_dotenv()
api = API(os.environ["RAINDROP_TOKEN"])

collection = Collection.create(api, title="Test collection")
print(collection.title)

# (note that Raindrop only supports a small set of file types, see https://help.raindrop.io/files for the list)
raindrop = Raindrop.upload(api, Path(__file__), "text/plain", collection)
print(raindrop.title)

Raindrop.remove(api, id=raindrop.id)

Collection.remove(api, id=collection.id)
