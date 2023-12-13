"""Create, update and delete a Collection."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from raindropiopy import API, Collection

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:
    # Create a new collection..
    title = "abcdef"
    print(f"Creating collection: '{title}'...", flush=True, end="")
    c = Collection.create(api, title=title)
    print("Done.")

    # Update it's title (amongst other possibilities)
    title = "12345"
    print(f"Updating collection: '{title}'...", flush=True, end="")
    c = Collection.update(api, id=c.id, title=title)
    print("Done.")

    # Cleanup
    print(f"Removing collection: '{title}'...", flush=True, end="")
    Collection.delete(api, id=c.id)
    print("Done.")
