[![version](https://img.shields.io/badge/python-3.10+-green)](https://www.python.org/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![license](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/PBorocz/raindrop-io-py/blob/trunk/LICENSE)
|docs|

# Raindrop-IO-py

Python wrapper for the API to the [Raindrop.io](https://raindrop.io) Bookmark Manager as well as a simple command-line interface to perform common operations.

## Background

I wanted to use an existing API for the Raindrop Bookmark Manager ([python-raindropio](https://github.com/atsuoishimoto/python-raindropio)) to perform some bulk operations through a simple command-line interface. However, the API available was incomplete and didn't contain any user-interface. Thus, this is a _fork_ and significant extension of [python-raindropio](https://github.com/atsuoishimoto/python-raindropio) (ht [Atsuo Ishimoto](https://github.com/atsuoishimoto)).

This package includes:

-   An API providing access to the Raindrop environment. For instance: create, update, delete link/file-based Raindrops; create, update delete Raindrop collections, tags etc.
-   A terminal-based user-interface that both tests the API as well as providing (me) a fast, simple interface to my Raindrop collections.

## Status

As the API layer is based on a fork of an existing package, it's reasonably stable. However, the command-line interface (CLI) is brand new (and lacks tests, i.e. "works for me!" ;-).

## Requirements

Requires Python 3.10 or later (well, at least I'm developing against 3.10.9).

## Install

```shell
[.venv] python -m pip install raindrop-io-py
```

## Setup

To use this package, besides your own account on [Raindrop](https://raindrop.io), you'll need to create an `integration app` on the Raindrop.io site from which you can create API token(s).

-   Go to [<https://app.draindrop.api/settings/integrations>](https://app.raindrop.io/settings/integrations) and select `+ create new app`.

-   Give it a descriptive name and then select the app you just created.

-   Select `Create test token` and copy the token provided. Note that the basis for calling it a _test_ token is that it only gives you access to bookmarks within *your own account*. Raindrop allows you to use their API against other people's environments using oAuth (see untested/unsupported `flask_oauth.py` file in /examples)

-   Save your token into your environment (we use python-dotenv so a simple .env/.envrc file containing your token should suffice), for example:

```shell
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

```shell
[.venv] % python examples/list_collections.py
```

or a wrapper script is available to run all of them, in logical order with a small wait to be nice to Raindrop's API:

```shell
[.venv] % python examples/RUN_ALL.py
```

### API Examples

Here are a few examples of API usage. Note that I don't have testing for the examples below (yet), but *DO* for those in the examples folder!

#### Display All Collections and **Unsorted** Bookmarks:

This example shows the intended usage of the API as a context-manager, from which any number of calls can be made:

```python
import os

from dotenv import load_dotenv

from raindropiopy import API, Collection, CollectionRef, Raindrop

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:

    print("Current Collections:"
    for collection in Collection.get_collections(api):
        print(collection.title)

    print("\nUnsorted Raindrop Bookmarks:"
    for item in Raindrop.search(api, collection=CollectionRef.Unsorted):
        print(item.title)
```

#### Create a New Raindrop Bookmark to a URL

```python
import os

from dotenv import load_dotenv

from raindropiopy import API, Raindrop

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:
    link, title = "https://www.python.org/", "Our Benevolent Dictator's Creation"
    print(f"Creating Raindrop to: '{link}' with title: '{title}'...", flush=True, end="")
    raindrop = Raindrop.create_link(api, link=link, title=title, tags=["abc", "def"])
    print(f"Done, id={raindrop.id}")

```

(after this has executed, go to your Raindrop.io environment (site or app) and you should see this Raindrop to python.org available)

#### Create a New Raindrop Collection

```python
import os
import sys
from datetime import datetime
from getpass import getuser

from dotenv import load_dotenv

from raindropiopy import API, Collection

load_dotenv()

with API(os.environ["RAINDROP_TOKEN"]) as api:
    title = f"TEST Collection ({getuser()}@{datetime.now():%Y-%m-%dT%H:%M:%S})"
    print(f"Creating collection: '{title}'...", flush=True, end="")
    collection = Collection.create(api, title=title)
    print(f"Done, {collection.id=}.")
```

(after this has executed, go to your Raindrop.io environment (site or app) and you should see this collection available)

## Command-Line Interface Usage

```shell
[.venv] % raindropiopy
```

Note: remember to setup `RAINDROP-TOKEN` in your environment!

## Documentation

We use [Sphinx](https://www.sphinx-doc.org/en/master/index.html) with [Google-style docstrings](https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html) to document our API. Documentation is hosted by [ReadTheDocs](https://readthedocs.org/) and can be found [here](https://raindrop-io-py.readthedocs.io/en/latest/).

## Acknowledgments

[python-raindropio](https://github.com/atsuoishimoto/python-raindropio) from [Atsuo Ishimoto](https://github.com/atsuoishimoto).

## License

The project is licensed under the MIT License.

## Release History

### Unreleased

### v0.1.8 - 2023-10-03

- FIXED: Addressed error in README.md (ht to @superkeyor in [issue #7](https://github.com/PBorocz/raindrop-io-py/issues/7).
- CHANGED: `SystemCollections.get_status` has been renamed to `SystemCollections.get_counts` to more accurately reflect that it only returns the counts of Raindrops in the 3 SystemCollections only.
- ADDED: `SystemCollections.get_meta` to return the current "state" of your environment, in particular: the date-time associated with the last Raindrop change; if your account is Pro level also the number of "broken" and/or "duplicated" Raindrops in your account. 
- ADDED: Reduced CLI startup time as CLI now keeps cached lists of Collections and Tags in conventional (but platform-specific) application state directory. If no changes to the Raindrop environment have occurred since last invocation (determined by the `get_meta` method above), previous state will be used.
- SECURITY: Addressed `gitpython` vulnerabilities (CVE-2023-40590 and CVE-2023-41040). The former is primarily a Windows issue but `gitpython` is only used in the poetry _dev_ group for release support.
- SECURITY: Addressed `urllib3` vulnerability (CVE-2023-43804) inherited from requests library. Similar to above, this is also only used in poetry _dev_ group for release support (thus, will attempt to segregate a bit more strongly).

### v0.1.7 - 2023-08-22

- SECURITY: Another `tornado` update to address vulnerability in parsing Content-Length from header (has a CVE now ➡ `GHSA-qppv-j76h-2rpx`).


### v0.1.6 - 2023-08-17

- SECURITY: Update `tornado` to address vulnerability in parsing Content-Length from header (moderate severity, no CVE).

### v0.1.5 - 2023-08-17

- SECURITY: Update `certifi` to address potential security vulnerability (CVE-2023-37920) (second release attempt)

### v0.1.4 - 2023-08-17

- SECURITY: Update `certifi` to address potential security vulnerability (CVE-2023-37920).

### v0.1.3 - 2023-07-20

- SECURITY: Update `pygments` to 2.15.1 to address potential security vulnerability.
- CHANGED: Moved to py 3.11.3.

### v0.1.2 - 2023-07-08

- FIXED: Per Issue #5, cache `size` may come back from Raindrop as 0 in some cases, relax pydantic type from PositiveInt to `int` (Didn't hear anything back from Rustem regarding the cases in which this can (or should?) occur).

### v0.1.1 - 2023-06-06

- CHANGED: `Raindrop.search` now only takes a single search string (instead of word, tag or important), leaving search string blank results in correct wildcard search behaviour, addresses issue #4.

### v0.1.0 - 2023-02-16

- CHANGED: `Raindrop.create_file` to handle `collection` argument consistent with `Raindrop.create_link`, specifically, either a `Collection`, `CollectionRef` or direct integer collection_id.
- ADDED: Beginning of documentation suite on Read-The-Docs.

### v0.0.15 - 2023-02-11

- CHANGED: `Raindrop.search_paged` is now hidden (can't see a reason to explicitly use it over `Raindrop.search`)
- CHANGED: Several attributes that, while allowed to be set by RaindropIO's API, are now *not* able to be set by this API. For example, you shouldn't be able to change "time" by setting `created` or `last_update` fields on a Raindrop or Collection.
- CHANGED: The `Collection`, `Raindrop` and `Tag` "remove" method is now "delete" to more accurately match with RaindropIO's API).

### v0.0.14 - 2023-02-09

- FIXED: `Raindrop.cache.size` and `Raindrop.cache.created` attributes are now optional (RaindropIO's API doesn't always provide them).
- FIXED: README examples corrected to reflect simpler Raindrop.search call.

### v0.0.13 - 2023-02-07

- CHANGED: Cross-referenced the fields available from the Raindrop API with our API; most available but several optional ones skipped for now.
- CHANGED: (Internal) Remove dependency on ["jashin"](https://github.com/sojin-project/jashin) library by moving to [pydantic](https://docs.pydantic.dev/) for all Raindrop API models.

### v0.0.12 - 2023-02-06

- CHANGED: (Internal) Move from README.org to README.md to allow PyPI to display project information correctly.

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

```python
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

```python
from raindroiopy.api import API
```

- FIXED: Sample file upload specification in `examples/create_raindrop_file.py` is now correct.

.. |docs| image:: https://readthedocs.org/projects/docs/badge/?version=latest
    :alt: Documentation Status
    :scale: 100%
    :target: https://docs.readthedocs.io/en/latest/?badge=latest
