"""Create a new collection."""
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from raindroppy.api import API, Collection

load_dotenv()

RAINDROP = API(os.environ["RAINDROP_TOKEN"])

now = datetime.now()
title = f"Test - {now:%Y-%m-%d %H:%M}"

print(f"Creating collection: '{title}'...", flush=True, end="")
try:
    collection = Collection.create(RAINDROP, title=title)
    print(f"Done, {collection.id=}.")
except Exception(exc):
    print(f"Sorry, unable to create collection! {exc}")
    sys.exit(1)

# If you want to actually *see* the new collection, set to False and
# look it up through any Raindrop mechanism (ie. app, url etc.),
# otherwise, we clean up after ourselves.
if True:
    print(f"Removing collection: '{title}'...", flush=True, end="")
    Collection.remove(RAINDROP, id=collection.id)
    print("Done.")
