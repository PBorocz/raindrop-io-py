"""List all the tags currently associated with the user of the token provided"""
import os

from dotenv import load_dotenv

from raindroppy.api import API, Tag

load_dotenv()

RAINDROP = API(os.environ["RAINDROP_TOKEN"])

tags = Tag.get(RAINDROP)

print(f"{'Tag':10s} {'Count'}")
print(f"{'='*10} {'='*5:}")
total = 0
for tag in sorted(tags, key=lambda tag: tag.tag):
    print(f"{tag.tag:10s} {tag.count:5d}")
    total += tag.count

print(f"{'='*10} {'='*5:}")
print(f"{'Total':10s} {total:5d}")
