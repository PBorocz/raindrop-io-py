# raindroppy

Python wrapper for [raindrop.io API](https://developer.raindrop.io/).

This is a fork of [python-raindropio](https://github.com/atsuoishimoto/python-raindropio) from [Atsuo Ishimoto](https://github.com/atsuoishimoto). I needed a few additions and desired a simple terminal-based UI for interactive work with Raindrop itself.

## Requirements

- Requires Python 3.10 or later.


## Install

Until we learn how to "package" and distribute to PyPI, please use directly from this repo. Ultimately, you'll be able to:

```shell
pip3 install raindroppy
```

or 

```shell
poetry add raindroppy
```

## Setup

You need an API token from Raindrop.io to use this package. 

- Register & create a token:

    - Go to [app.draindrop.api/settings/integrations](https://app.raindrop.io/settings/integrations) and "+ create new app".

    - Give it a descriptive name and then select the app you just created. 

    - Select "Create test token" and copy the token provided.

- Save your token into your environment:

    - We use python-dotenv so a simple .env (or .envrc) file containing an entry for your token will suffice:

```
RAINDROP_TOKEN=01234567890-abcdefghf-aSample-API-Token-01234567890-abcdefghf
```

## API Usage

Two simple examples, for more, see raindroppy/api/samples directory.

### Create collection

```python
import os
from dotenv import load_dotenv

from raindroppy.api import API, Collection

load_dotenv()

api = API(os.environ["RAINDROP_TOKEN"])

c = Collection.create(api, title="Sample collection")
print(c.title)
```

### Search bookmarks from Unsorted collection.

```python
import os
from dotenv import load_dotenv

from raindroppy.api import API, CollectionRef, Raindrop

load_dotenv()

api = API(os.environ["RAINDROP_TOKEN"])

page = 0
while (items:=Raindrop.search(api, collection=CollectionRef.Unsorted, page=page)):
    print(page)
    for item in items:
        print(item.title)
    page += 1
```

## License

Copyright (c) 2022 Peter Borocz. See LICENSE for details.
