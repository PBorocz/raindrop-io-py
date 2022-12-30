import os

from raindroppy import *

api = API(os.environ["RAINDROP_TOKEN"])

c = User.get(api)

print("id:", c.id)
print("config:", c.config)
print("email:", c.email)
print("email_MD5:", c.email_MD5)
print("files:", c.files)
print("fullName:", c.fullName)
print("groups:", c.groups)
print("password:", c.password)
print("pro:", c.pro)
print("registered:", c.registered)

print("broken_level:", c.config.broken_level)
print("font_color :", c.config.font_color)
print("font_size:", c.config.font_size)
print("last_collection:", c.config.last_collection)
print("raindrops_view:", c.config.raindrops_view)


for group in c.groups:
    print("group title:", group.title)
    print("hidden:", group.hidden)
    print("sort:", group.sort)

    print("collection:")
    for collectionid in group.collectionids:
        collection = Collection.get(api, collectionid)
        print(collection.title)
