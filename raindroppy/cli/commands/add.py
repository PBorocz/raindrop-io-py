"""Add/Create a new file-based bookmark to Raindrop."""
from pathlib import Path
from time import sleep
from typing import Optional

from api import API, Raindrop
from beaupy import confirm, prompt, select, select_multiple
from beaupy.spinners import DOTS, Spinner
from cli.commands import CONTENT_TYPES
from cli.models import CLI, CreateRequest, RaindropType
from tomli import load
from utilities import find_or_add_collection


def _create(api: API, request: CreateRequest, interstitial: int = 1, debug: bool = False) -> bool:
    """Create either a link or file-based Raindrop given a request."""

    def _create_file(api: API, request: CreateRequest, debug: bool) -> bool:
        """Create a FILE-based Raindrop."""
        if debug:
            print(request)
        else:
            raindrop = Raindrop.create_file(
                api,
                request.file_path,
                content_type=CONTENT_TYPES.get(request.file_path.suffix),
                collection=request.collection,
            )

        # The Raindrop API's create Raindrop from file does not allow
        # us to set other attributes, thus, we need to check if any
        # need to be set and do so explicitly:
        args = {}
        if request.title:
            args["title"] = request.title
        if request.tags:
            args["tags"] = request.tags
        if args:
            if debug:
                print(f"Update Raindrop {args!s}")
            else:
                Raindrop.update(api, raindrop.id, **args)

        return True

    # Get (or create a new) collection (changing the representation in
    # the request from a string to a collection object)
    request.collection = find_or_add_collection(api, request.collection)

    # Push it up!
    msg = "Adding to Raindrop..."
    spinner = Spinner(DOTS, msg)
    spinner.start()

    if request.type_ == RaindropType.URL:
        if debug:
            print(request)
        else:
            Raindrop.create_link(
                api, request.url, title=request.title, tags=request.tags, collection=request.collection
            )

    elif request.type_ == RaindropType.FILE:
        _create_file(api, request, debug)

    spinner.stop()

    # Be nice to raindrop.io and wait a bit..
    if interstitial:
        sleep(interstitial)

    return True


def _read_files(path_: Path) -> list[Path]:
    """Make sure the inbound directory is good and return all PDF's in it."""
    assert path_.exists(), f"Sorry, '{path_}' doesn't exist!"
    return list(path_.glob("*.pdf"))


def _prompt_for_request(cli: CLI, type_: RaindropType, dir_path: Optional[Path]) -> Optional[CreateRequest]:
    """Prompt for create new Raindrop request (either link or url).

    Returns request or None (if not confirmed).
    """
    create_request = CreateRequest(type_=type_)

    # Prompts differ whether or not we're creating a file or link-based Raindrop.
    if create_request.type_ == RaindropType.URL:
        create_request.url = prompt("What URL?:")
        create_request.title = prompt("What Title?:")

    elif create_request.type_ == RaindropType.FILE:
        files: list[Path] = [path.name for path in _read_files(dir_path.expanduser())]
        create_request.file_path = select(files)
        create_request.title = prompt("What Title?:", initial_value=create_request.file_path.stem)

    # These are the same across raindrop types:
    create_request.collection = select(list(cli.state.get_collection_titles()))
    create_request.tags = select_multiple(list(cli.state.tags))

    # Confirm the values that we just received:
    if create_request.type_ == RaindropType.URL:
        cli.console.print(f"URL           : {create_request.url}")
    elif create_request.type_ == RaindropType.FILE:
        cli.console.print(f"File to send  : {create_request.file_path.name}")

    cli.console.print(f"With title    : {create_request.title}")
    cli.console.print(f"To collection : {create_request.collection}")
    cli.console.print(f"With tags     : {create_request.tags}")

    if confirm("\nIs this correct?"):
        return create_request
    return None


def _validate_request(cli: CLI, request: CreateRequest) -> bool:
    """Return True iff the request is valid."""

    if not request.file_path and not request.url:
        cli.console.print("Sorry, at least 'file_path' or 'url' must be populated for each entry.\n")
        return False

    # Validate the existence of the specified file
    if request.file_path:
        if not request.file_path.exists():
            cli.console.print(f"Sorry, no file with name '{request.file_path}' exists.\n")
            return False

        # Validate the file type
        if request.file_path.suffix not in CONTENT_TYPES:
            cli.console.print(
                f"Sorry, file type {request.file_path.suffix} needs to be mapped to a valid Content-Type.\n"
            )
            return False

    # Validate the URL provided
    if request.url:
        ...  # FIXME

    # Validate the collection requested (if requested)
    if request.collection:
        if cli.state.find_collection(request.collection) is None:
            cli.console.print(
                f"Sorry, collection '{request.collection}' doesn't exist "
                "in Raindrop, please add or correct Collection name.\n"
            )
            return False

    # Validate any tags associated with the request
    if request.tags:
        for tag in request.tags:
            if tag.casefold() not in cli.state.tags:
                cli.console.print(f"Sorry, {tag=} does not currently exist.\n")
                return False

    return True


def RequestFactory(entry: dict) -> CreateRequest:
    """Return an new instance of CreateRequest based on an inbound dict (ie. from toml)."""
    request: CreateRequest = CreateRequest(
        collection=entry.get("collection"),
        tags=entry.get("tags"),
    )
    # Are we getting a specification for a file-based Raindrop or a URL-based one?
    if entry.get("file_path"):
        request.type_ = RaindropType.FILE
        request.file_path = Path(entry.get("file_path"))
        # Get default title from the file name if we don't have a title provided in the inbound dict:
        request.title = entry.get("title", request.file_path.stem)
    elif entry.get("url"):
        request.type_ = RaindropType.URL
        request.url = entry.get("url")
        request.title = entry.get("title")
    return request


def _do_bulk(cli: CLI) -> None:

    while True:  # ie, until we get a valid file..
        fn_request: str = prompt("TOML Upload File", initial_value="./upload.toml")
        fp_request: Path = Path(fn_request)
        if not fp_request.exists():
            cli.console.print(f"Sorry, unable to find request_toml file: '{fn_request}'\n")
            continue

        with open(fp_request, "rb") as fh_request:
            requests: list[CreateRequest] = [RequestFactory(entry) for entry in load(fh_request).get("requests", [])]

        # Filter down to only valid entries:
        requests: list[CreateRequest] = [req for req in requests if _validate_request(cli, req)]
        if not requests:
            cli.console.print("Sorry, no valid requests found.\n")
            break

        # Confirm that we're good to go and add these requests..
        if confirm(f"\nReady to create {len(requests)} valid requests, Ok?"):
            return sum([_create(cli.state.api, request) for request in requests])

        return None


def do_add(cli: CLI) -> None:
    """Top-level UI Controller for adding bookmarks from the terminal."""
    while True:
        options = ["Add a URL", "Add a File", "Bulk Add (from a file)", "Back"]
        response = select(options)
        if response == options[0]:
            type_ = RaindropType.URL

        elif response == options[1]:
            type_ = RaindropType.FILE

        elif response == options[2]:
            type_ = RaindropType.BULK

        elif response == options[3]:
            return None

        else:
            cli.console.print("Sorry, invalid response received!")

        if type_ in (RaindropType.URL, RaindropType.FILE):
            # Add a *single* Raindrop bookmark
            if create_request := _prompt_for_request(cli, type_, dir_path=Path("~/Downloads/Raindrop")):
                _create(cli.state.api, create_request)

        elif type_ in (RaindropType.BULK,):
            # Add any number of Raindrop bookmarks from a file specification
            _do_bulk(cli)
