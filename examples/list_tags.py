"""List all the tags currently associated with the user of the token provided."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from raindropiopy import API, Tag

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:
    tags = Tag.get(api)

    print(f"{'Tag':10s} {'Count'}")
    print(f"{'='*10} {'='*5:}")
    total = 0
    for tag in sorted(tags, key=lambda tag: tag.tag):
        print(f"{tag.tag:10s} {tag.count:5d}")
        total += tag.count

    print(f"{'='*10} {'='*5:}")
    print(f"{'Total':10s} {total:5d}")
