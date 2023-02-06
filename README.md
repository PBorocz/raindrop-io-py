``` html
<div align="center">
  <a href="https://choosealicense.com/licenses/mit/">
    <img alt="MIT License"
         src="https://img.shields.io/badge/License-MIT-green.svg" />
  </a>

  <a href="https://www.python.org/">
    <img alt="Python Version"
         src="https://img.shields.io/badge/python-3.10+-green" />
  </a>

  <a href="https://github.com/pre-commit/pre-commit">
    <img alt="pre-commit"
       src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit" />
  </a>
</div>
```
# Raindrop-IO-py

Python wrapper for the API to the [Raindrop.io](https://raindrop.io) Bookmark Manager as well as a simple command-line interface to perform common operations.

## Background

I wanted to use an existing API for the Raindrop Bookmark Manager ([python-raindropio](https://github.com/atsuoishimoto/python-raindropio)) to perform some bulk operations through a simple command-line interface. However, the API available was incomplete and didn't contain any user-interface. Thus, this is a _fork_ and significant extension of [python-raindropio](https://github.com/atsuoishimoto/python-raindropio) (ht [Atsuo Ishimoto](https://github.com/atsuoishimoto)).

This package includes:

-   An API providing access to the Raindrop environment. For instance: create, update, delete link/file-based Raindrops; create, update delete Raindrop collections, tags etc.
-   A terminal-based user-interface that both tests the API as well as providing (me) a fast, simple interface to my Raindrop collections.

## Status

As the API layer is based on a fork of an existing package, it's reasonably stable. However, the command-line interface (CLI) is brand new (and lacking tests, ie. "works for me!" ;-).

## Requirements

Requires Python 3.10 or later (well, at least I'm developing against 3.10.9).

## Install

``` shell
[.venv] python -m pip install raindrop-io-py
```

## Setup

To use this package, besides your own account on [Raindrop](https://raindrop.io), you'll need to create an `integration app` on the Raindrop.io site from which you can create API token(s).

-   Go to [<https://app.draindrop.api/settings/integrations>](https://app.raindrop.io/settings/integrations) and select `+ create new app`.

-   Give it a descriptive name and then select the app you just created.

-   Select `Create test token` and copy the token provided. Note that the basis for calling it a _test_ token is that it only gives you access to bookmarks within *your own account*. Raindrop allows you to use their API against other people's environments using oAuth (see untested/unsupported `flask_oauth.py` file in /examples)

-   Save your token into your environment (we use python-dotenv so a simple .env/.envrc file containing your token should suffice), for example:

``` shell
# If you use direnv or it's equivalent, place something like this in a .env file:
RAINDROP_TOKEN=01234567890-abcdefghf-aSample-API-Token-01234567890-abcdefghf

# Or for bash:
export RAINDROP_TOKEN=01234567890-abcdefghf-aSample-API-Token-01234567890-abcdefghf

# Or for fish:
set -gx RAINDROP_TOKEN 01234567890-abcdefghf-aSample-API-Token-01234567890-abcdefghf

# etc...
```

## Examples

A full suite of examples are provided in the `examples` directory. Each can be run independently as:

``` shell
[.venv] % python examples/list_collections.py
```

or a wrapper script is available to run all of them, in logical order with a small wait to be nice to Raindrop's API:

``` shell
[.venv] % python examples/RUN_ALL.py
```

## API Usage

Here are a few examples of API usage (all of these should be able to be executed "as-is"):

### Create a New Raindrop Bookmark to a URL

``` python
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

(after this has executed, go to your Raindrop.io environment (site or app) and you should see this Raindrop to python.org available)

### Create a New Raindrop Collection

``` python
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

(after this has executed, go to your Raindrop.io environment (site or app) and you should see this collection available)

### Display All Bookmarks from the **Unsorted** Raindrop Collection

``` python
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

``` shell
[.venv] % raindropiopy
```

Note: remember to setup `RAINDROP-TOKEN` in your environment!

## Acknowledgments

-   [python-raindropio](https://github.com/atsuoishimoto/python-raindropio) from [Atsuo Ishimoto](https://github.com/atsuoishimoto).

## License

The project is licensed under the MIT License.

## Release History

### Unreleased

### v0.0.12 - 2023-02-06

- CHANGED: (Internal), move from README.org to README.md to allow PyPI to display project information correctly.

### v0.0.11 - 2023-02-06

- CHANGED: Raindrop search API call is now non-paged (the "paged" version is still available as `Raindrop.search_paged`).

### v0.0.10 - 2023-02-05

- ADDED: Ability to specify raindrop field: Description on a created Raindrop (either file or link-based).
- ADDED: Ability to re-query existing search results (eg. after changes) and smoothed out post-search interactions.

### v0.0.9 - 2023-02-04

- ADDED: An ability to view, edit and delete raindrops returned from a search.
- ADDED: A simple `RUN_ALL.py` script to the examples directory to...well, run all the examples in order!
- CHANGED: The display of raindrops returned from a search to include tags and to only show Collection name if all raindrops are across multiple collections.

### v0.0.8 - 2023-01-25

- CHANGED: Added simple version method in root package:

``` python
from raindropiopy import version
print(version())
```

### v0.0.7 - 2023-01-25

- CHANGED: Moved from keeping README in markdown to org file format. Incorporated package's ChangeLog into README as well (at the bottom).
- CHANGED: Added new manage.py release automation capability (internal only, nothing public-facing).

### v0.0.6 - 2023-01-22

- FIXED: CLI autocomplete now works again after adding support for "single-letter" command-shortcuts.
- ADDED: A set of missing attributes to the Raindrop API model type, eg. file, cache etc. Only attribute still missing is "highlights".

### v0.0.5 - 2023-01-21

- ADDED: Support use of [Vulture](https://github.com/jendrikseipp/vulture) for dead-code analysis (not in pre-commit through due to conflict with ruff's McCabe complexity metric)
- CHANGED: Moved internal module name to match that of package name. Since we couldn't use raindroppy as a package name on PyPI due to similarities with existing packages (one of which was for a **crypto** package), we renamed this package to raindrop-io-py. In concert, the internal module is now `raindropiopy`:

``` python
from raindroiopy.api import API
```

- FIXED: Sample file upload specification in `examples/create_raindrop_file.py` is now correct.
