
# RaindropPY

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python Version](https://img.shields.io/badge/python-3.10+-green)](https://www.python.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Python wrapper for the [Raindrop.io](https://raindrop.io) Bookmark Manager [API](https://developer.raindrop.io/) as well as a simple command-line interface to prove out the API.

## Background

I needed a few additions to an existing API ([python-raindropio](https://github.com/atsuoishimoto/python-raindropio))and desired a simple terminal-based UI for interactive work with Raindrop itself.

Thus, this is a fork of [python-raindropio](https://github.com/atsuoishimoto/python-raindropio) from [Atsuo Ishimoto](https://github.com/atsuoishimoto). 

## Status

As the API to Raindrop itself is based on a fork of an existing package, it's reasonably stable (as of this writing, only one minor change is envisioned)

However, the command-line interface (CLI) is brand new and lacking tests. Thus, it's probably **NOT** ready for serious use yet. Similarly, real installation support will come when I learn the ins/outs of _package_ creation and distribution.

## Requirements

- Requires Python 3.10 or later (well, at least I'm developing against 3.10.9)


## Install

Until I learn how to "package" and distribute to PyPI, **please use directly from this repo**. _Ultimately_, you'll be able to:

```shell
pip3 install raindroppy
```

or 

```shell
poetry add raindroppy
```

## Setup

You need to create an integration _app_ on Raindrop.io to receive API token(s) to use this package.

- Go to [app.draindrop.api/settings/integrations](https://app.raindrop.io/settings/integrations) and select `+ create new app`.

- Give it a descriptive name and then select the app you just created. 

- For testing and/or to only access your Raindrop environment, select `Create test token` and copy the token provided.

- Save your token(s) into your environment (we use python-dotenv so a simple .env/.envrc file your information should suffice), for example:
```
RAINDROP_TEST_TOKEN=01234567890-abcdefghf-aSample-API-Token-01234567890-abcdefghf
# or
RAINDROP_CLIENT_ID=1234567890-abcdefgh-1234567890
RAINDROP_CLIENT_SECRET=abcdefgh-1234567890-abcdefgh
```

## API Usage & Examples

A full suite of examples are provided in the examples directory, here are a few to give you some idea of the usage model:

### Create a New Raindrop Bookmark to a URL

```python
import os
import sys

from dotenv import load_dotenv

from raindroppy.api import API, Raindrop

load_dotenv()

with API(os.environ["RAINDROP_TEST_OKEN"]) as api:
    link, title = "https://www.python.org/", "Our Benevolent Dictator's Creation"
    
    print(f"Creating Raindrop to: '{link}' with title: '{title}'...", flush=True, end="")
    raindrop = Raindrop.create_link(api, link=link, title=title, tags=["abc", "def"])
    print(f"Done, id={raindrop.id}")
```

### Create a New Raindrop Collection

```python
import os
import sys
from datetime import datetime
from getpass import getuser

from dotenv import load_dotenv

from raindroppy.api import API, Collection

load_dotenv()

with API(os.environ["RAINDROP_TEST_TOKEN"]) as api:
    title = f"TEST Collection ({getuser()}@{datetime.now():%Y-%m-%dT%H:%M:%S})"
    
    print(f"Creating collection: '{title}'...", flush=True, end="")
    collection = Collection.create(api, title=title)
    print(f"Done, {collection.id=}.")
```

### Display All Bookmarks from the *Unsorted* Raindrop Collection

```python
import os
from dotenv import load_dotenv

from raindroppy.api import API, CollectionRef, Raindrop

load_dotenv()


with API(os.environ["RAINDROP_TEST_TOKEN"]) as api:
    page = 0
    while (items := Raindrop.search(api, collection=CollectionRef.Unsorted, page=page)):
        for item in items:
            print(item.title)
        page += 1
```

## Command-Line Interface Usage

```shell
[.venv] % python raindroppy/cli/run.py
```

## Acknowledgments

- [python-raindropio](https://github.com/atsuoishimoto/python-raindropio) from [Atsuo Ishimoto](https://github.com/atsuoishimoto).


## License

Copyright (c) 2022 Peter Borocz. See LICENSE for details.
