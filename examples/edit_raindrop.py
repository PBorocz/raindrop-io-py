import os

from dotenv import load_dotenv

from raindroppy.api import API, Raindrop

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:

    # Create a new Raindrop..
    link="https://www.python.org/"
    print(f"Creating Raindrop: '{link}'...", flush=True, end="")
    raindrop = Raindrop.create(api, link=link, tags=["abc", "def"])
    print(f"Done, title is {raindrop.title}.")

    # Update it's title (amongst other possibilities)
    print(f"Updating Raindrop: '{link}'...", flush=True, end="")
    raindrop = Raindrop.update(api, id=raindrop.id, title="A Nicer Title for Link to Python.org")
    print(f"Done, title is now: {raindrop.title}.")

    # Cleanup
    print(f"Removing Raindrop: '{link}'...", flush=True, end="")
    Raindrop.remove(api, id=raindrop.id)
    print("Done.")
