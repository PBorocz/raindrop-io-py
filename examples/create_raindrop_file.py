"""Create a new file-based Raindrop into the Unsorted collection"""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from raindroppy.api import API, Raindrop

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:
    # Create new raindrop of this actual file. Note that Raindrop only supports a
    # small set of file types, see https://help.raindrop.io/files for details.
    path_, content_type = Path(__file__), "text/plain"
    print(f"Creating Raindrop of: '{path_.name}'...", flush=True, end="")
    try:
        raindrop = Raindrop.create_file(api, path_, content_type)
        print("Done.")
        print(f"{raindrop.id=}")
    except Exception as exc:
        print(f"Sorry, unable to create Raindrop! {exc}")
        sys.exit(1)

    # If you want to actually *see* the new Raindrop, set to False and
    # look it up through any Raindrop mechanism (ie. app, url etc.),
    # otherwise, we clean up after ourselves.
    if True:
        print(f"Removing raindrop: '{path_.name}'...", flush=True, end="")
        Raindrop.remove(api, id=raindrop.id)
        print("Done.")
