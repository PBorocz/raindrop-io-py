# raindroppy

Python wrapper for [raindrop.io API](https://developer.raindrop.io/).

This is a _fork_ of [https://github.com/atsuoishimoto/python-raindropio](python-raindropio) from [https://github.com/atsuoishimoto](Atsuo Ishimoto).

I needed a few additions and desired a simple terminal-based UI for interactive work with Raindrop itself.

## Requirements

- Requires Python 3.10 or later.


## Install

Until I understand how to "package" and distribute to PyPI, please use directly from this repo. Ultimately, you'll be able to:

```shell
pip3 install raindroppy
```

or 

```shell
poetry add raindroppy
```

## Setup

You must register your application at https://app.raindrop.io/settings/integrations.

### Register & Create a API token at [https://app.raindrop.io/settings/integrations](app.draindrop.api/settings/integrations)

### Save your API Token into your environment.

We use python-dotenv so a simple .env (or .envrc) file containing an entry for RAINDROP_TOKEN will suffice:

```
# -*- mode: yaml;-*-
RAINDROP_TOKEN=790db7cf-aSample-API-Token.01234567890-abcdefghf
```

## API Usage

### Create collection

```python
from raindropio import API, Collection
api = API(raidrop_access_token)

c = Collection.create(api, title="Sample collection")
print(c.title)
```

### Search bookmarks from Unsorted collection.

```python
from raindropio import API, CollectionRef, Raindrop
api = API(raidrop_access_token)

page = 0
while (items:=Raindrop.search(api, collection=CollectionRef.Unsorted, page=page)):
    print(page)
    for item in items:
        print(item.title)
    page += 1
```

## License

Copyright 2022 Peter Borocz

See LICENSE for detail.
