"""Example to show how to search across the Raindrop environment."""
import os
import sys
from time import sleep

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from raindropiopy import API, Raindrop

load_dotenv()


def _search(api, **search_args):
    """Search for all Raindrops (in Unsorted since we're not passing in a collection.id)."""
    print(f"Searching with {search_args}")
    page = 0
    while raindrops := Raindrop.search(api, page=page, **search_args):
        for raindrop in raindrops:
            print(f"Found! {raindrop.id=} {raindrop.title=}\n")
        page += 1


with API(os.environ["RAINDROP_TOKEN"]) as api:

    # Create a sample Raindrop to be searched for:
    link = "https://www.python.org/"
    title = "Our Benevolent Dictators Creation"
    print("Creating sample Raindrop...", flush=True, end="")
    try:
        raindrop = Raindrop.create_link(
            api,
            link=link,
            title=title,
            tags=["abc", "def"],
        )
        print("Done.")
        print(f"{raindrop.id=}")
    except Exception as exc:
        print(f"Sorry, unable to create Raindrop! {exc}")
        sys.exit(1)

    # Nothing is instantaneous...be nice to Raindrop and wait a bit...
    print(
        "Waiting 10 seconds for Raindrop's backend to complete indexing....",
        flush=True,
        end="",
    )
    sleep(10)
    print("Ok")

    # OK, now (for example), search by tag:
    _search(api, tag="def")

    # or, search by link domain or title:
    _search(api, word="python.org")
    _search(api, word="Benevolent")

    # Cleanup
    print("Removing sample Raindrop...", flush=True, end="")
    Raindrop.delete(api, id=raindrop.id)
    print("Done.")
