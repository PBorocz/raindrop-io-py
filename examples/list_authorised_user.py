"""List the attributes associated with user of the token provided."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from raindroppy.api import API, User

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:

    user = User.get(api)

    for attr in ["id", "email", "fullName", "password", "pro", "registered"]:
        print(f"{attr:16s} {getattr(user, attr)}")

    # User configuration..
    print()
    print("config.broken_level:    ", user.config.broken_level)
    print("config.font_color:      ", user.config.font_color)
    print("config.font_size:       ", user.config.font_size)
    print("config.raindrops_view:  ", user.config.raindrops_view)

    # User files..
    print()
    print("files.used:             ", user.files.used)
    print("files.size:             ", user.files.size)
    print("files.lastCheckPoint:   ", user.files.lastCheckPoint)

    # User group membership
    print()
    for group in user.groups:
        print("groups.group.title:     ", group.title)
        print("groups.group.title:     ", group.title)
        print("groups.hidden:          ", group.hidden)
        print("groups.sort:            ", group.sort)
        print("groups.collectionids:   ", list(group.collectionids))
        print()
