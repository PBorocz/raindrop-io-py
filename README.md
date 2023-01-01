
# RaindropPY

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python Version](https://img.shields.io/badge/python-3.10+-green)](https://www.python.org/)

Python wrapper for the raindrop.io bookmark manager [API](https://developer.raindrop.io/).

This is probably ready for use yet! We're still learning the foibles of creating a repository for public use.

This is a fork of [python-raindropio](https://github.com/atsuoishimoto/python-raindropio) from [Atsuo Ishimoto](https://github.com/atsuoishimoto). I needed a few additions and desired a simple terminal-based UI for interactive work with Raindrop itself.

## Requirements

- Requires Python 3.10 or later (well, at least I'm developing against 3.10.9)


## Install

Until I learn how to "package" and distribute to PyPI, please use directly from this repo. _Ultimately_, you'll be able to:

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

- For testing and/or to only access your Raindrop environment, select "Create test token" and copy the token provided.

- Save your token(s) into your environment:

    - We use python-dotenv so a simple .env (or .envrc) file containing an entry for your token will suffice:

```
RAINDROP_TEST_TOKEN=01234567890-abcdefghf-aSample-API-Token-01234567890-abcdefghf
# or
RAINDROP_CLIENT_ID=1234567890-abcdefgh-1234567890
RAINDROP_CLIENT_SECRET=abcdefgh-1234567890-abcdefgh
```

## API Usage & Examples

A full suite of examples are provided in the examples directory, here's are two simple ones:

### Create a collection

```python
import os
from dotenv import load_dotenv
from raindroppy.api import API, Collection
load_dotenv()

with API(os.environ["RAINDROP_TEST_TOKEN"]) as api:
    c = Collection.create(api, title="Sample collection")
    print(f"{c.title=})
```

### Search bookmarks from the *Unsorted* collection

```python
import os
from dotenv import load_dotenv
from raindroppy.api import API, CollectionRef, Raindrop
load_dotenv()

with API(os.environ["RAINDROP_TEST_TOKEN"]) as api:
    page = 0
    while (items := Raindrop.search(api, collection=CollectionRef.Unsorted, page=page)):
        print(page)
        for item in items:
            print(f"{item.title=}")
        page += 1
```

## Acknowledgments

- [python-raindropio](https://github.com/atsuoishimoto/python-raindropio) from [Atsuo Ishimoto](https://github.com/atsuoishimoto).


## License

Copyright (c) 2022 Peter Borocz. See LICENSE for details.


## Feedback

Feel free to file issues or reach out to me directly at peter.borocz at gmail.com.
