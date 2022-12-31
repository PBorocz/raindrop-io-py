"""Bulk upload one or more files to create new file-based bookmark on Raindrop."""
import sys
from pathlib import Path
from time import sleep

from loguru import logger as log
from models import RaindropState, UploadRequest
from tomli import load
from utilities import find_or_add_collection, get_current_state

from raindroppy.api import API, Raindrop

CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".py": "text/plain",
    ".txt": "text/plain",
    ".org": "text/plain",
}


def _validate_request(raindrop_state: RaindropState, request: UploadRequest) -> bool:
    """Return True iff the request is valid."""
    # Validate the existence of the specified file
    if not request.file_path.exists():
        log.error(f"Sorry, no file with name '{request.file_path}' exists.\n")
        return False

    # Validate the file type
    if request.file_path.suffix not in CONTENT_TYPES:
        log.error(f"Sorry, file type {request.file_path.suffix} needs to be mapped to a valid Content-Type.\n")
        return False

    # Validate the collection requested (if requested)
    if request.collection:
        if request.collection.casefold() not in raindrop_state.collections:
            log.error(
                f"Sorry, collection '{request.collection}' doesn't exist "
                "in Raindrop, please add or correct Collection name.\n"
            )
            return False

    # Validate any tags associated with the request
    if request.tags:
        for tag in request.tags:
            if tag.casefold() not in raindrop_state.tags:
                log.error(f"Sorry, {tag=} does not currently exist.\n")
                return False

    return True


def _upload(api: API, request: UploadRequest, interstitial: int = 1, debug: bool = False) -> bool:

    # Get (or create) the collection
    collection = find_or_add_collection(api, request.collection)

    # Push it up!
    raindrop = Raindrop.upload(api, request.file_path, CONTENT_TYPES.get(request.file_path.suffix), collection)

    # Do we need to set any other attributes on the newly created entry?
    args = {}
    if request.title:
        args["title"] = request.title
    if request.tags:
        args["tags"] = request.tags
    if args:
        raindrop = Raindrop.update(api, raindrop.id, **args)

    # Be nice to raindrop.io!
    if interstitial:
        sleep(interstitial)
    return True


def _map_to_request(entry: dict) -> UploadRequest:
    return UploadRequest(
        file_path=Path(entry.get("file_path")),
        collection=entry.get("collection"),
        title=entry.get("title"),
        tags=entry.get("tags"),
    )


def do_upload(
    api: API, upload_request: UploadRequest = None, upload_toml: str = None, validate: bool = True, debug: bool = False
) -> int:
    """Controller for uploading file(s) based on TOML file.

    File includes specification of what files to load and with what attributes.
    """
    if not upload_request and not upload_toml:
        raise RuntimeError("Sorry, at least one of 'upload_toml' or 'upload_request' arguments are required!")

    # Build the list of items to processed, either as provided directly or from a file..
    if upload_toml:
        fp_config = Path(upload_toml)
        if not fp_config.exists():
            log.error(f"Sorry, unable to find upload_toml file: '{fp_config}'")
            sys.exit(1)
        requests: list[UploadRequest] = [_map_to_request(entry) for entry in load(upload_toml).get("requests", [])]
    else:
        requests: list[UploadRequest] = [upload_request]

    # If requested, filter down to only valid entries:
    if validate:
        raindrop_state: RaindropState = get_current_state(api)
        requests: list[UploadRequest] = [req for req in requests if _validate_request(raindrop_state, req)]
        if not requests:
            return 0

    return sum([_upload(api, request, debug) for request in requests])
