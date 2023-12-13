"""List the attributes associated with user of the token provided."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from raindropiopy import API, User

load_dotenv()


def _print(key, value):
    print(f"{key:.<48} {value!s}")


with API(os.environ["RAINDROP_TOKEN"]) as api:
    user = User.get(api)

    for attr in ["id", "email", "full_name", "password", "pro", "registered"]:
        _print(attr, getattr(user, attr))

    # User configuration..
    print()
    _print("config.broken_level", user.config.broken_level.value)
    _print("config.font_color", user.config.font_color)
    _print("config.font_size", user.config.font_size)
    _print("config.lang", user.config.lang)
    _print("config.last_collection", user.config.last_collection)
    _print("config.raindrops_sort", user.config.raindrops_sort)
    _print("config.raindrops_view", user.config.raindrops_view)
    for (
        attr,
        value,
    ) in user.config.other.items():  # (user "internal_" use only fields)
        _print(f"config.other.{attr}", value)

    # User files..
    print()
    _print("files.used", user.files.used)
    _print("files.size", user.files.size)
    _print("files.last_checkpoint", user.files.last_checkpoint)

    # User group membership
    for group in user.groups:
        print()
        _print("groups.group.title", group.title)
        _print("groups.group.title", group.title)
        _print("groups.hidden", group.hidden)
        _print("groups.sort", group.sort)
        _print("groups.collectionids", list(group.collectionids))
