"""List the attributes associated with user of the token provided"""
import os

from dotenv import load_dotenv

from raindroppy.api import API, Collection, User

load_dotenv()

RAINDROP = API(os.environ["RAINDROP_TOKEN"])

user = User.get(RAINDROP)

for attr in ["id", "email", "fullName", "password", "pro", "registered"]:
    print(f"{attr:16s} {getattr(user, attr)}")

# User configuration..
print("\nConfig")
print(f"\tconfig.broken_level:   ", user.config.broken_level)
print(f"\tconfig.font_color:     ", user.config.font_color)
print(f"\tconfig.font_size:      ", user.config.font_size)
print(f"\tconfig.raindrops_view: ", user.config.raindrops_view)

# User files..
print("\nFiles")
print(f"\tfiles.used:           ", user.files.used)
print(f"\tfiles.size:           ", user.files.size)
print(f"\tfiles.lastCheckPoint: ", user.files.lastCheckPoint)

# User group membership
print("\nGroups")
for group in user.groups:
    print("\tgroups.group.title: ", group.title)
    print("\tgroups.hidden:      ", group.hidden)
    print("\tgroups.sort:        ", group.sort)
    print("\tCollections")
    for collectionid in group.collectionids:
        collection = Collection.get(RAINDROP, collectionid)
        print("\t\tgroups.collectionids.title: ", collection.title)
