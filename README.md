
# Raindrop-io-py

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)
[![Python Version](https://img.shields.io/badge/python-3.10+-green)](https://www.python.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

Python wrapper for the [Raindrop.io](https://raindrop.io) Bookmark Manager as well as a simple command-line interface to perform common operations.


## Background & Acknowledgments

I needed a few additions to an existing API for the Raindrop Bookmark Manager and desired a simple terminal-based UI for interactive work with Raindrop itself. Thus, this is a _fork_ of [python-raindropio](https://github.com/atsuoishimoto/python-raindropio) from [Atsuo Ishimoto](https://github.com/atsuoishimoto) ...thanks Atsuo!


## Status

As the API layer is based on a fork of an existing package, it's reasonably stable (as of this writing, only one minor enhancement is envisioned)

However, the command-line interface (CLI) is brand new and lacking tests. Thus, it's probably **NOT** ready for serious use yet.

## Requirements

Requires Python 3.10 or later (well, at least I'm developing against 3.10.9).

## Install

```shell
[.venv] python -m pip install raindrop-io-py
```

## Setup

To use this package, besides your own account on [Raindrop](https://raindrop.io), you'll need to create an _integration app_ on the Raindrop.io site from which you can create API token(s). 

- Go to [app.draindrop.api/settings/integrations](https://app.raindrop.io/settings/integrations) and select `+ create new app`.

- Give it a descriptive name and then select the app you just created. 

- Select `Create test token` and copy the token provided. Note that the basis for calling it a "test" token is that it only gives you access to bookmarks within _your own account_. Raindrop allows you to use their API against other people's environments using oAuth (see untested/unsupported flask_oauth file in /examples)

- Save your token into your environment (we use python-dotenv so a simple .env/.envrc file your information should suffice), for example:

```
# in a .env file:
RAINDROP_TOKEN=01234567890-abcdefghf-aSample-API-Token-01234567890-abcdefghf

# or for bash:
export RAINDROP_TOKEN=01234567890-abcdefghf-aSample-API-Token-01234567890-abcdefghf

# or go fish:
set -gx RAINDROP_TOKEN 01234567890-abcdefghf-aSample-API-Token-01234567890-abcdefghf

# ...
```

## API Usage & Examples

A full suite of examples are provided in the `examples` directory, here are a few to give you some idea of the usage model:

### Create a New Raindrop Bookmark to a URL

```python
import os
import sys

from dotenv import load_dotenv

from raindropiopy.api import API, Raindrop

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:
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

from raindropiopy.api import API, Collection

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:
    title = f"TEST Collection ({getuser()}@{datetime.now():%Y-%m-%dT%H:%M:%S})"
    print(f"Creating collection: '{title}'...", flush=True, end="")
    collection = Collection.create(api, title=title)
    print(f"Done, {collection.id=}.")
```

After this has executed, go to your Raindrop.io environment (site or app) and you should see this collection defined.

### Display All Bookmarks from the *Unsorted* Raindrop Collection

```python
import os
from dotenv import load_dotenv

from raindropiopy.api import API, CollectionRef, Raindrop

load_dotenv()


with API(os.environ["RAINDROP_TOKEN"]) as api:
    page = 0
    while (items := Raindrop.search(api, collection=CollectionRef.Unsorted, page=page)):
        for item in items:
            print(item.title)
        page += 1
```

## Command-Line Interface Usage

```shell
# Remember to setup RAINDROP_TOKEN in your environment!
[.venv] % raindropiopy
```

## Acknowledgments

- [python-raindropio](https://github.com/atsuoishimoto/python-raindropio) from [Atsuo Ishimoto](https://github.com/atsuoishimoto).


## License

The project is licensed under the MIT License.
