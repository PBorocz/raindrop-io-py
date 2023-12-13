"""List the title and count of Raindrops in "system" collections, eg. Unsorted, Trash and All."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from raindropiopy import API, SystemCollection

load_dotenv()


def _print(collection: SystemCollection) -> None:
    print("---------------------------------------------------")
    print("id:    ", collection.id)
    print("title: ", collection.title)
    print("count: ", collection.count)


with API(os.environ["RAINDROP_TOKEN"]) as api:
    for collection in SystemCollection.get_counts(api):
        _print(collection)
