"""Create a new link-based Raindrop into the Unsorted collection."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from raindroppy.api import API, Raindrop

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:
    link, title = "https://www.python.org/", "Benevolent Dictator's Creation"
    try:
        print(
            f"Creating Raindrop to: '{link}' with title: '{title}'...",
            flush=True,
            end="",
        )
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

    # If you want to actually *see* the new Raindrop, set to False and
    # look it up through any Raindrop mechanism (ie. app, url etc.),
    # otherwise, we clean up after ourselves.
    if True:
        print(f"Removing raindrop: '{title}'...", flush=True, end="")
        Raindrop.remove(api, id=raindrop.id)
        print("Done.")
