"""Create a new file-based Raindrop into the Unsorted collection."""
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from raindropiopy.api import API, Raindrop

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:
    # Note that Raindrop only supports a small set of file types, see
    # https://help.raindrop.io/files for details.
    path_ = Path(__file__).parent / Path("sample_upload_file.pdf")
    print(f"Creating Raindrop of: '{path_.name}'...", flush=True, end="")
    try:
        raindrop = Raindrop.create_file(api, path_, content_type="application/pdf")
        print("Done.")
        print(f"{raindrop.id=}")
    except Exception as exc:
        print(f"Sorry, unable to create Raindrop! {exc}")
        sys.exit(1)

    # If you want to actually *see* the new Raindrop, set to False and
    # look it up through any Raindrop mechanism (ie. app, url etc.),
    # otherwise, we clean up after ourselves.
    if True:
        print(f"Removing Raindrop: '{path_.name}'...", flush=True, end="")
        Raindrop.remove(api, id=raindrop.id)
        print("Done.")
