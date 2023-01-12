"""List the attributes associated with user of the token provided"""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from raindroppy.api import API, Collection, User

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:

    user = User.get(api)

    for attr in ["id", "email", "fullName", "password", "pro", "registered"]:
        print(f"{attr:16s} {getattr(user, attr)}")

    # User configuration..
    print("\nConfig")
    print("\tconfig.broken_level:   ", user.config.broken_level)
    print("\tconfig.font_color:     ", user.config.font_color)
    print("\tconfig.font_size:      ", user.config.font_size)
    print("\tconfig.raindrops_view: ", user.config.raindrops_view)

    # User files..
    print("\nFiles")
    print("\tfiles.used:           ", user.files.used)
    print("\tfiles.size:           ", user.files.size)
    print("\tfiles.lastCheckPoint: ", user.files.lastCheckPoint)

    # User group membership
    print("\nGroups")
    for group in user.groups:
        print("\tgroups.group.title: ", group.title)
        print("\tgroups.hidden:      ", group.hidden)
        print("\tgroups.sort:        ", group.sort)
        print("\tCollections")
        for collection_id in group.collectionids:
            if collection := Collection.get(api, collection_id):
                print("\t\tgroups.collectionids.title: ", collection.title)
