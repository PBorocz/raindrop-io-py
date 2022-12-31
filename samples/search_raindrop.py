import os
from time import sleep

from dotenv import load_dotenv

from raindroppy.api import API, Raindrop

load_dotenv()

RAINDROP = API(os.environ["RAINDROP_TOKEN"])

def _search(**search_args):
    """Search for all Raindrops (in Unsorted since we're not passing in a collection.id)."""
    print(f"Searching with {search_args}")
    page = 0
    while (raindrops := Raindrop.search(RAINDROP, page=page, **search_args)):
        for raindrop in raindrops:
            print(f"Found! {raindrop.id=} {raindrop.title=}\n")
        page += 1

# Create a sample Raindrop to be searched for:
link = "https://www.python.org/"
title = "Our Benevolent Dictators Creation"
print(f"Creating sample Raindrop...", flush=True, end="")
try:
    raindrop = Raindrop.create(RAINDROP, link=link, title=title, tags=['abc', 'def'])
    print(f"Done.")
    print(f"{raindrop.id=}")
except Exception(exc):
    print(f"Sorry, unable to create Raindrop! {exc}")
    sys.exit(1)

# Nothing is instantaneous...be nice to Raindrop and wait a bit...
print("Waiting 10 seconds for Raindrop's backend to complete indexing....", flush=True, end="")
sleep(10)
print("Ok")

# OK, now (for example), search by tag:
_search(tag="def")

# or, search by link domain or title:
_search(word="python.org")
_search(word="Benevolent")

# Cleanup
print(f"Removing sample raindrop...", flush=True, end="")
Raindrop.remove(RAINDROP, id=raindrop.id)
print("Done.")
