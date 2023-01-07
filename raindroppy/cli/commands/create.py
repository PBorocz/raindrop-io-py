"""Bulk create one or more Raindrops based on a external file specification."""
import sys
from pathlib import Path
from time import sleep

from api import API, Raindrop
from cli.models import CLI
from models import CreateRequest, RaindropState, RaindropType
from tomli import load
from utilities import find_or_add_collection

CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".py": "text/plain",
    ".txt": "text/plain",
    ".org": "text/plain",
}


def _validate_request(raindrop_state: RaindropState, request: CreateRequest) -> bool:
    """Return True iff the request is valid."""
    # Validate the existence of the specified file
    if not request.file_path.exists():
        sys.stderr.write(f"Sorry, no file with name '{request.file_path}' exists.\n")
        return False

    # Validate the file type
    if request.file_path.suffix not in CONTENT_TYPES:
        sys.stderr.write(f"Sorry, file type {request.file_path.suffix} needs to be mapped to a valid Content-Type.\n")
        return False

    # Validate the collection requested (if requested)
    if request.collection:
        if request.collection.casefold() not in raindrop_state.collections:
            sys.stderr.write(
                f"Sorry, collection '{request.collection}' doesn't exist "
                "in Raindrop, please add or correct Collection name.\n"
            )
            return False

    # Validate any tags associated with the request
    if request.tags:
        for tag in request.tags:
            if tag.casefold() not in raindrop_state.tags:
                sys.stderr.write(f"Sorry, {tag=} does not currently exist.\n")
                return False

    return True


def _create_url(api: API, request: CreateRequest, collection) -> bool:
    """Create a standard URL based Raindrop."""
    Raindrop.create_link(api, link=request.url, title=request.title, tags=request.tags, collection=request.collection)
    return True


def _create_file(api: API, request: CreateRequest, collection) -> bool:
    """Create a FILE-based Raindrop."""
    raindrop = Raindrop.create_file(api, request.file_path, CONTENT_TYPES.get(request.file_path.suffix), collection)

    # Do we need to set any other attributes on the newly created entry?
    args = {}
    if request.title:
        args["title"] = request.title
    if request.tags:
        args["tags"] = request.tags
    if args:
        raindrop = Raindrop.update(api, raindrop.id, **args)

    return True


def _create(api: API, request: CreateRequest, interstitial: int = 1, debug: bool = False) -> bool:
    """Controller for creating either URL or File-based Raindrops."""

    # Get (or create) the collection
    collection = find_or_add_collection(api, request.collection)

    # Push it up depending on the Raindrop "type" to be created
    if request.type_ == RaindropType.URL:
        create_method = _create_url
    elif request.type_ == RaindropType.FILE:
        create_method = _create_file
    else:
        raise RuntimeError(f"Sorry, invalid RaindropType encountered: '{request.type_}'")

    # Push it up!
    create_method(api, request, collection)

    # be nice to raindrop.io and wait a bit..
    if interstitial:
        sleep(interstitial)
    return True


def CreateRequestFactory(entry: dict) -> CreateRequest:
    """Return an new instance of CreateRequest based on an inbound dict (eg. from toml)."""
    return CreateRequest(
        title=entry.get("title"),
        collection=entry.get("collection"),
        tags=entry.get("tags"),
        type_=RaindropType.FILE,
        file_path=Path(entry.get("file_path")),
    )


def do_create(
    cli: CLI, create_request: CreateRequest = None, request_toml: str = None, validate: bool = True, debug: bool = False
) -> int:
    """Controller for creating Raindrops based either on a bulk basis from a TOML file or a directly provided request.

    File includes specification of what file(s) to load and with what attributes.
    """
    if not create_request and not request_toml:
        raise RuntimeError("Sorry, at least one of 'request_toml' or 'create_request' arguments are required!")

    # Build the list of items to processed, either as provided directly or from a file..
    if request_toml:
        fp_config = Path(request_toml)
        if not fp_config.exists():
            sys.stderr.write(f"Sorry, unable to find request_toml file: '{fp_config}'\n")
            sys.exit(1)
        requests: list[CreateRequest] = [
            CreateRequestFactory(entry) for entry in load(request_toml).get("requests", [])
        ]
    else:
        requests: list[CreateRequest] = [create_request]

    # If requested, filter down to only valid entries:
    if validate:
        requests: list[CreateRequest] = [req for req in requests if _validate_request(cli.state, req)]
        if not requests:
            return 0

    return sum([_create(cli.api, request, debug) for request in requests])
