"""Create a new link-based Raindrop into the Unsorted collection"""
import os

from dotenv import load_dotenv

from raindroppy.api import API, Raindrop

load_dotenv()

LINK = "https://www.python.org/"
TITLE = "Benevolent Dictator's Creation"

with API(os.environ["RAINDROP_TOKEN"]) as api:
    try:
        print(f"Creating Raindrop to: '{LINK}' with title: '{TITLE}'...", flush=True, end="")
        raindrop = Raindrop.create(api, link=LINK, title=TITLE, tags=["abc", "def"])
        print(f"Done.")
        print(f"{raindrop.id=}")
    except Exception(exc):
        print(f"Sorry, unable to create Raindrop! {exc}")
        sys.exit(1)

    # If you want to actually *see* the new Raindrop, set to False and
    # look it up through any Raindrop mechanism (ie. app, url etc.),
    # otherwise, we clean up after ourselves.
    if True:
        print(f"Removing raindrop: '{TITLE}'...", flush=True, end="")
        Raindrop.remove(api, id=raindrop.id)
        print("Done.")
