"""Create, update and delete a Collection"""
import os

from dotenv import load_dotenv

from raindroppy.api import API, Collection

load_dotenv()

RAINDROP = API(os.environ["RAINDROP_TOKEN"])

# Create a new collection..
title = "abcdef"
print(f"Creating collection: '{title}'...", flush=True, end="")
c = Collection.create(RAINDROP, title=title)
print("Done.")

# Update it's title (amongst other possibilities)
title = "12345"
print(f"Updating collection: '{title}'...", flush=True, end="")
c = Collection.update(RAINDROP, id=c.id, title=title)
print("Done.")

# Cleanup
print(f"Removing collection: '{title}'...", flush=True, end="")
Collection.remove(RAINDROP, id=c.id)
print("Done.")
