import os

from dotenv import load_dotenv

from raindroppy.api import *

load_dotenv()
api = API(os.environ["RAINDROP_TOKEN"])


collection = Collection.create(api, title="Test collection")

raindrop = Raindrop.create(
    api, link="https://www.python.org/", tags=["abc", "def"], collection=collection
)
print(raindrop.title)
