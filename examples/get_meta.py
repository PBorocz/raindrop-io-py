"""List the results of the "get_meta" call (primarily num of broken links, last change date and pro-level)."""
import os
import sys
from pprint import pprint

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from raindropiopy import API, SystemCollection

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:
    pprint(SystemCollection.get_meta(api))
