
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

# RaindropPY

Python wrapper for [raindrop.io API](https://developer.raindrop.io/).

This is a fork of [python-raindropio](https://github.com/atsuoishimoto/python-raindropio) from [Atsuo Ishimoto](https://github.com/atsuoishimoto). I needed a few additions and desired a simple terminal-based UI for interactive work with Raindrop itself.

This is NOT ready for use yet! We're still learning the foibles of creating a repository for public use.

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

You need to create an integration "app" on Raindrop.io to receive API token(s) to use this package.

- Go to [app.draindrop.api/settings/integrations](https://app.raindrop.io/settings/integrations) and "+ create new app".

- Give it a descriptive name and then select the app you just created. 

- For testing, select "Create test token" and copy the token provided.

- For production use, copy the CLIENT_ID and CLIENT_SECRET tokens provided.

- Save your token(s) into your environment:

    - We use python-dotenv so a simple .env (or .envrc) file containing an entry for your token will suffice:

```
RAINDROP_TEST_TOKEN=01234567890-abcdefghf-aSample-API-Token-01234567890-abcdefghf
# or
RAINDROP_CLIENT_ID=1234567890-abcdefgh-1234567890
RAINDROP_CLIENT_SECRET=abcdefgh-1234567890-abcdefgh
```

## API Usage & Examples

Two simple examples, for more, see raindroppy/api/samples directory.

### Create a collection

```python
import os
from dotenv import load_dotenv

from raindroppy.api import API, Collection

load_dotenv()

api = API(os.environ["RAINDROP_TEST_TOKEN"])

c = Collection.create(api, title="Sample collection")
print(f"{c.title=})
```

### Search bookmarks from Unsorted collection.

```python
import os
from dotenv import load_dotenv

from raindroppy.api import API, CollectionRef, Raindrop

load_dotenv()

api = API(os.environ["RAINDROP_TEST_TOKEN"])

page = 0
while (items := Raindrop.search(api, collection=CollectionRef.Unsorted, page=page)):
    print(page)
    for item in items:
        print(f"{item.title=}")
    page += 1
```

## Acknowledgements

 - [python-raindropio](https://github.com/atsuoishimoto/python-raindropio) from [Atsuo Ishimoto](https://github.com/atsuoishimoto).


## License

Copyright (c) 2022 Peter Borocz. See LICENSE for details.


## Feedback

If you have any feedback, please reach out to peter.borocz at gmail.com.
