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


def _create_link(api: API, request: CreateRequest, debug: bool) -> None:
    """Create a URL/link-based Raindrop."""
    if debug:
        print(request)
    else:
        Raindrop.create_link(api, request.url, title=request.title, tags=request.tags, collection=request.collection)


def _read_files(path_: Path) -> list[Path]:
    """Make sure the inbound directory is good and return all PDF's in it."""
    assert path_.exists(), f"Sorry, '{path_}' doesn't exist!"
    return list(path_.glob("*.pdf"))


def _prompt_for_request(
    cli: CLI, type_: RaindropType, dir_path: Optional[Path] = Path("~/Downloads/Raindrop")
) -> Optional[CreateRequest]:
    """Prompt for create new Raindrop request (either link or url).

    Returns request or None (if not confirmed).
    """
    request = CreateRequest(type_=type_)

    # Prompts differ whether or not we're creating a file or link-based Raindrop.
    if request.type_ == RaindropType.URL:
        request.url = prompt("What URL?:")
        request.title = prompt("What Title?:")

    elif request.type_ == RaindropType.FILE:
        files: dict[str, Path] = {path.name: path for path in _read_files(dir_path.expanduser())}
        fn_selected = select(sorted(list(files.keys())))
        request.file_path = files.get(fn_selected)
        request.title = prompt("What Title?:", initial_value=request.file_path.stem)

    # These are the same across raindrop types:
    request.collection = select(list(cli.state.get_collection_titles()))
    request.tags = select_multiple(list(cli.state.tags))

    # Confirm the values that we just received:
    if request.type_ == RaindropType.URL:
        cli.console.print(f"URL           : {request.url}")
    elif request.type_ == RaindropType.FILE:
        cli.console.print(f"File to send  : {request.file_path.name}")
    cli.console.print(f"With title    : {request.title}")
    cli.console.print(f"To collection : {request.collection}")
    cli.console.print(f"With tags     : {request.tags}")

    if confirm("\nIs this correct?"):
        return request
    return None


def _add_single(
    cli: CLI, type_: RaindropType, request: CreateRequest = None, interstitial: int = 1, debug: bool = False
) -> bool:
    """Create either a link or file-based Raindrop, if we don't have a request yet, get one."""

    assert type_ or request, "Sorry, either a RaindropType or an existing request is required"
    if not request:
        request: CreateRequest = _prompt_for_request(cli, type_)
        if not request:
            return False  # User requested that we could still get out..

    # Convert from /name/ of collection user entered to an instance of
    # the Collection itself, creating a new one through the respective
    # API if necessary.
    request.collection = find_or_add_collection(cli.state.api, request.collection)

    # Push it up!
    msg = f"Adding Raindrop -> {request.name()}..."
    spinner = Spinner(DOTS, msg)
    spinner.start()

    if request.type_ == RaindropType.URL:
        _create_link(cli.state.api, request, debug)

    elif request.type_ == RaindropType.FILE:
        _create_file(cli.state.api, request, debug)

    spinner.stop()

    # Be nice to raindrop.io and wait a bit..
    if interstitial:
        sleep(interstitial)

    return True


def _validate_request(cli: CLI, request: CreateRequest) -> bool:
    """Return True iff the request is valid."""

    # Error Check: Validate the existence of the specified file for
    if request.file_path:
        if not request.file_path.exists():
            cli.console.print(f"Sorry, no file with name '{request.file_path}' exists.\n")
            return False

        # Validate the file type
        if request.file_path.suffix not in CONTENT_TYPES:
            cli.console.print(f"Sorry, file type {request.file_path.suffix} isn't yet supported by Raindrop.io.\n")
            return False

    # Error Check: Validate the URL provided
    if request.url:
        ...  # FIXME

    # Error Check: Validate any tags associated with the request
    if request.tags:
        for tag in request.tags:
            if tag.casefold() not in cli.state.tags:
                cli.console.print(f"Sorry, {tag=} does not currently exist.\n")
                return False

    # Warning only: check for collection existence
    if request.collection:
        if cli.state.find_collection(request.collection) is None:
            cli.console.print(
                f"Collection '{request.collection}' doesn't exist " "in Raindrop, we'll be adding it from scratch.\n"
            )

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


def _add_bulk(cli: CLI) -> None:

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
            return sum([_add_single(cli, None, request) for request in requests])

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
            _add_single(cli, type_)

        elif type_ in (RaindropType.BULK,):
            # Add any number of Raindrop bookmarks from a file specification
            _add_bulk(cli)
