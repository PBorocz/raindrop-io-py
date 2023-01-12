"""Create a new Raindrop bookmark."""
from pathlib import Path
from time import sleep
from typing import Any, Final, Optional
from urllib.parse import urlparse

from prompt_toolkit.completion import WordCompleter
from tomli import load

from raindroppy.api import API, Collection, Raindrop
from raindroppy.cli import CONTENT_TYPES, PROMPT_STYLE, cli_prompt, options_as_help
from raindroppy.cli.cli import CLI
from raindroppy.cli.models import CreateRequest, RaindropType
from raindroppy.cli.spinner import Spinner


def _create_file(api: API, request: CreateRequest) -> bool:
    """Create a FILE-based Raindrop."""

    args: dict[str, Any] = {}
    if request.title:
        args["title"] = request.title
    if request.tags:
        args["tags"] = request.tags

    Raindrop.create_file(
        api,
        request.file_path,
        content_type=CONTENT_TYPES.get(request.file_path.suffix),
        collection=request.collection,
        **args,
    )
    return True


def _create_link(api: API, request: CreateRequest) -> None:
    """Create a URL/link-based Raindrop."""
    Raindrop.create_link(api, request.url, title=request.title, tags=request.tags, collection=request.collection)


def _read_files(path_: Path) -> list[Path]:
    """Make sure the inbound directory is good and return all PDF's in it."""
    assert path_.exists(), f"Sorry, '{path_}' doesn't exist!"
    return list(path_.glob("*.pdf"))


def __validate_url(url: str) -> Optional[str]:
    """Validate the url provided, returning a message if invalid, None otherwise"""
    if not url:
        return "Sorry, you need to specify a valid URL, e.g. https://www.slate.com"
    try:
        parts = urlparse(url)
        if all([parts.scheme, parts.netloc]):
            return None
    except ValueError:
        return f"Sorry, URL provided {url} isn't valid."


def __get_url(cli: CLI) -> Optional[str]:
    prompt = cli_prompt(("create", "url", "url?"))
    while True:
        try:
            response = cli.session.prompt(prompt, style=PROMPT_STYLE)
            if response == "?":
                cli.console.print("We need a valid URL here, eg. https://www.python.org")
            elif response == "q":
                return None
            else:
                if (msg := __validate_url(response)) is None:
                    return response
                else:
                    cli.console.print(msg)
                    # And go back up for another try..
        except (KeyboardInterrupt, EOFError):
            return None


def __get_title(cli: CLI) -> Optional[str]:
    prompt = cli_prompt(("create", "url", "title?"))
    while True:
        try:
            response = cli.session.prompt(prompt, style=PROMPT_STYLE)
            if response == "?":
                cli.console.print("We need a Bookmark title here, eg. 'This is an interesting bookmark'")
            elif response == "q":
                return None
            else:
                return response
        except (KeyboardInterrupt, EOFError):
            return None


def __get_file(cli: CLI) -> Optional[str]:
    prompt = cli_prompt(("create", "bulk", "upload file?"))
    while True:
        try:
            response = cli.session.prompt(prompt, style=PROMPT_STYLE)
            if response == "?":
                cli.console.print("We need a path to a valid, TOML upload file, eg. '/Users/me/Download/upload.toml'")
            elif response == "q":
                return None
            else:
                return response
        except (KeyboardInterrupt, EOFError):
            return None


def __get_from_list(cli: CLI, prompt: str, options: list[str]) -> Optional[str]:
    prompt = cli_prompt(("create", "url", f"{prompt}?"))
    completer: Final = WordCompleter(options)
    while True:
        try:
            response = cli.session.prompt(
                prompt, completer=completer, style=PROMPT_STYLE, complete_while_typing=True, enable_history_search=False
            )
            if response == "?":
                cli.console.print(", ".join(options))
            else:
                break
        except (KeyboardInterrupt, EOFError):
            return None
    return response


def __get_from_files(cli: CLI, options: list[Path]) -> Optional[str]:
    prompt = cli_prompt(("create", "url", "file #?"))
    names = [fp_.name for fp_ in options]
    completer: Final = WordCompleter(names)
    for ith, fp_ in enumerate(options):
        cli.console.print(f"{ith:2d} {fp_.name}")
    while True:
        try:
            response = cli.session.prompt(
                prompt, completer=completer, style=PROMPT_STYLE, complete_while_typing=True, enable_history_search=False
            )
            if response == "?":
                cli.console.print(", ".join(options))
            else:
                break
        except (KeyboardInterrupt, EOFError):
            return None

    return options[int(response)]


def __get_confirmation(cli: CLI, prompt: str) -> bool:
    prompt: Final = [("class:prompt", "\nIs this correct? ")]
    options: Final = ["yes", "Yes", "No", "no"]
    completer: Final = WordCompleter(options)
    try:
        response = cli.session.prompt(
            prompt, completer=completer, style=PROMPT_STYLE, complete_while_typing=True, enable_history_search=False
        )
        if response == "q":
            return None
        else:
            if response.lower() in ["yes", "y", "ye"]:
                return True
            return False
    except (KeyboardInterrupt, EOFError):
        return False


def _prompt_for_request(
    cli: CLI, type_: RaindropType, dir_path: Optional[Path] = Path("~/Downloads/Raindrop")
) -> Optional[CreateRequest]:
    """Prompt for create new Raindrop request (either link or url).

    Returns request or None (if not confirmed).
    """
    request = CreateRequest(type_=type_)

    # Prompts differ whether or not we're creating a file or link-based Raindrop.
    if request.type_ == RaindropType.URL:
        request.url = __get_url(cli)
        if request.url is None:
            return None

    elif request.type_ == RaindropType.FILE:
        files = _read_files(dir_path.expanduser())
        request.file_path = __get_from_files(cli, sorted(files, key=lambda fp_: fp_.name))

    # Get a Title:
    request.title = __get_title(cli)
    if request.title is None:
        return None

    # These are the same across raindrop types:
    request.collection = __get_from_list(cli, "collection", list(cli.state.get_collection_titles()))
    if request.collection is None:
        return None

    request.tags = __get_from_list(cli, "tag(s)", list(cli.state.tags))
    if request.tags is None:
        return None

    # Confirm the values that we just received are good to go...
    request.print(cli.console.print)
    if __get_confirmation(cli, "Is this correct?"):
        return request
    return None


def _add_single(cli: CLI, type_: RaindropType, request: CreateRequest = None, interstitial: int = 1) -> bool:
    """Create either a link or file-based Raindrop, if we don't have a request yet, get one."""

    assert type_ or request, "Sorry, either a RaindropType or an existing request is required"
    if not request:
        request: CreateRequest = _prompt_for_request(cli, type_)
        if not request:
            return False  # User requested that we could still get out..

    # Convert from /name/ of collection user entered to an /instance/
    # of a Collection; if necessary, creating a new one through the
    # respective Raindrop API.
    request.collection = Collection.get_or_create(cli.state.api, request.collection)

    # Push it up!
    with Spinner(f"Adding Raindrop -> {request.name()}..."):

        if request.type_ == RaindropType.URL:
            _create_link(cli.state.api, request)

        elif request.type_ == RaindropType.FILE:
            _create_file(cli.state.api, request)

    # Be nice to raindrop.io and wait a bit..
    if interstitial:
        sleep(interstitial)

    return True


def __validate_site(url: str) -> Optional[str]:
    """Validate that the url provided actually goes to a live site, return message if not."""
    return None
    # FIXME!!


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

    if request.url:
        # Error Check: Validate the URL provided
        if msg := __validate_url(request.url):
            cli.console.print(msg)
            return False

        # Error Check: Validate that the site is actually "there"
        if msg := __validate_site(request.url):
            cli.console.print(msg)
            return False

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


def _add_bulk(cli: CLI) -> None:

    while True:  # ie, Until we get a valid file..
        fn_request = __get_file(cli)
        if fn_request is None:
            return None

        fp_request: Path = Path(fn_request).expanduser()
        if not fp_request.exists():
            cli.console.print(f"Sorry, unable to find request_toml file: '{fp_request}'\n")
            continue

        with open(fp_request, "rb") as fh_request:
            requests: list[CreateRequest] = [
                CreateRequest.factory(entry) for entry in load(fh_request).get("requests", [])
            ]

        # Filter down to only valid entries:
        requests: list[CreateRequest] = [req for req in requests if _validate_request(cli, req)]
        if not requests:
            cli.console.print("Sorry, no valid requests found.\n")
            break

        # Confirm that we're good to go
        if not __get_confirmation(cli, f"Ready to create {len(requests)} valid requests, Ok?"):
            return None

        # Add em!
        return sum([_add_single(cli, None, request) for request in requests])


def process(cli: CLI) -> None:
    """Controller for adding bookmark(s) from the terminal."""
    while True:
        options: Final = ["file", "url", "bulk", "back", "."]
        completer: Final = WordCompleter(options)

        while True:
            try:
                cli.console.print(options_as_help(options))
                response = cli.session.prompt(
                    cli_prompt(("create",)),
                    completer=completer,
                    style=PROMPT_STYLE,
                    complete_while_typing=True,
                    enable_history_search=False,
                )

                if response.casefold() in ("back", "."):
                    return None
                elif response.casefold() in ("?",):
                    cli.console.print(options_as_help(options))
                elif response.casefold() == "bulk":
                    _add_bulk(cli)
                elif response.casefold() == "file":
                    _add_single(cli, RaindropType.FILE)
                elif response.casefold() == "url":
                    _add_single(cli, RaindropType.URL)
                else:
                    cli.console.print(f"Sorry, must be one of {', '.join(options)}.")
            except (KeyboardInterrupt, EOFError):
                return None
