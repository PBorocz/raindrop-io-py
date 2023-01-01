"""Create a new collection."""
import os
import sys
from datetime import datetime
from getpass import getuser
from pathlib import Path

from dotenv import load_dotenv
from raindroppy.api import API, Collection

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:
    title = f"TEST Collection ({getuser()}@{datetime.now():%Y-%m-%dT%H:%M:%S})"
    print(f"Creating collection: '{title}'...", flush=True, end="")
    try:
        collection = Collection.create_link(api, title=title)
        print(f"Done, {collection.id=}.")
    except Exception(exc):
        print(f"Sorry, unable to create collection! {exc}")
        sys.exit(1)

    # If you want to actually *see* the new collection, set to False and
    # look it up through any Raindrop mechanism (ie. app, url etc.),
    # otherwise, we clean up after ourselves.
    if True:
        print(f"Removing collection: '{title}'...", flush=True, end="")
        Collection.remove(api, id=collection.id)
        print("Done.")
