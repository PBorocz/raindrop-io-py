"""Create a new Raindrop bookmark."""
from http.client import HTTPConnection
from pathlib import Path
from time import sleep
from typing import Any, Final, Optional
from urllib.parse import urlparse

from prompt_toolkit.completion import WordCompleter
from tomli import load

from raindroppy.api import API, Collection, Raindrop
from raindroppy.cli import (
    CONTENT_TYPES,
    PROMPT_STYLE,
    cli_prompt,
    options_as_help,
)
from raindroppy.cli.cli import CLI
from raindroppy.cli.commands import get_from_list
from raindroppy.cli.models import CreateRequest
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
    Raindrop.create_link(
        api,
        request.url,
        title=request.title,
        tags=request.tags,
        collection=request.collection,
    )


def _read_files(path_: Path) -> list[Path]:
    """Make sure the inbound directory is good and return all PDF's in it."""
    assert path_.exists(), f"Sorry, '{path_}' doesn't exist!"
    return list(path_.glob("*.pdf"))


def __validate_url(url: str) -> Optional[str]:
    """Validate the url provided, returning a message if invalid, None otherwise."""

    def is_url_invalid(url: str) -> Optional[str]:
        try:
            parts = urlparse(url)
            if all([parts.scheme, parts.netloc]):
                if parts.scheme.lower() not in ("http", "https"):
                    return f"Sorry, URL provided {url} isn't valid (bad protocol)"
                return None
        except ValueError:
            ...
        return "Sorry, that URL isn't in a valid format."

    def is_site_invalid(url, timeout=2) -> Optional[str]:
        """Validate that the url provided actually goes to a live site, return message if not."""
        error = Exception("Sorry, unknown error encountered.")
        parser = urlparse(url)
        host = parser.netloc or parser.path.split("/")[0]
        for port in (80, 443):
            connection = HTTPConnection(host=host, port=port, timeout=timeout)
            try:
                connection.request("HEAD", "/")
                return None
            except Exception as e:
                error = e
            finally:
                connection.close()
        return f"Sorry, that URL isn't running now or doesn't exist, can you get to it in a browser? {error}"

    with Spinner("Validating URL..."):
        if msg := is_url_invalid(url):
            return msg
        if msg := is_site_invalid(url):
            return msg
        return None


def __get_url(cli: CLI) -> Optional[str]:
    prompt = cli_prompt(("create", "url?"))
    while True:
        url = cli.session.prompt(prompt, style=PROMPT_STYLE)
        if url == "?" or url == "" or url is None:
            cli.console.print(
                "We need a valid URL here, eg. https://www.python.org",
            )
        elif url == "q":
            return None
        else:
            if msg := __validate_url(url):
                cli.console.print(msg)
            else:
                return url


def __get_title(cli: CLI) -> Optional[str]:
    prompt = cli_prompt(("create", "title?"))
    while True:
        title = cli.session.prompt(prompt, style=PROMPT_STYLE)
        if title == "?":
            cli.console.print(
                "We need a Bookmark title here, eg. 'This is an interesting bookmark'",
            )
        elif title == "q":
            return None
        else:
            return title


def __get_file(cli: CLI) -> Optional[str]:
    prompt = cli_prompt(("create", "bulk", "upload file?"))
    while True:
        file_ = cli.session.prompt(prompt, style=PROMPT_STYLE)
        if file_ == "?":
            cli.console.print(
                "We need a path to a valid, TOML upload file, eg. '/Users/me/Download/upload.toml'",
            )
        elif file_ == "q":
            return None
        else:
            return file_


def __get_from_files(cli: CLI, options: list[Path]) -> Optional[str]:
    prompt = cli_prompt(("create", "url", "file #?"))
    names = [fp_.name for fp_ in options]
    completer: Final = WordCompleter(names)
    for ith, fp_ in enumerate(options):
        cli.console.print(f"{ith:2d} {fp_.name}")
    while True:
        response = cli.session.prompt(
            prompt,
            completer=completer,
            style=PROMPT_STYLE,
            complete_while_typing=True,
            enable_history_search=False,
        )
        if response == "?":
            cli.console.print(", ".join(options))
        else:
            break

    return options[int(response)]


def __get_confirmation(cli: CLI, prompt: str) -> bool:
    prompt: Final = [("class:prompt", "\nIs this correct? ")]
    options: Final = ["yes", "Yes", "No", "no"]
    completer: Final = WordCompleter(options)
    response = cli.session.prompt(
        prompt,
        completer=completer,
        style=PROMPT_STYLE,
        complete_while_typing=True,
        enable_history_search=False,
    )
    if response == "q":
        return None
    else:
        if response.lower() in ["yes", "y", "ye"]:
            return True
        return False


def _is_request_valid(cli: CLI, request: CreateRequest) -> bool:
    """Return True iff the request is valid."""
    # Error Check: Validate the existence of the specified file for
    if request.file_path:
        if not request.file_path.exists():
            cli.console.print(
                f"Sorry, no file with name '{request.file_path}' exists.\n",
            )
            return False

        # Validate the file type
        if request.file_path.suffix not in CONTENT_TYPES:
            cli.console.print(
                f"Sorry, file type {request.file_path.suffix} isn't yet supported by Raindrop.io.\n",
            )
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
                f"Collection '{request.collection}' doesn't exist "
                "in Raindrop, we'll be adding it from scratch.\n",
            )

    return True


def _prompt_for_request(
    cli: CLI,
    file: bool = False,
    url: bool = False,
    dir_path: Optional[Path] = Path("~/Downloads/Raindrop"),
) -> Optional[CreateRequest]:
    """Prompt for create new Raindrop request (either link or url).

    Returns request or None (if not confirmed).
    """
    request = CreateRequest()

    # Prompts differ whether or not we're creating a file or link-based Raindrop.
    if url:
        request.url = __get_url(cli)
        if request.url is None:
            return None
        if not _is_request_valid(cli, request):
            return None
    else:
        files = _read_files(dir_path.expanduser())
        request.file_path = __get_from_files(
            cli,
            sorted(files, key=lambda fp_: fp_.name),
        )

    # Get a Title:
    request.title = __get_title(cli)
    if request.title is None:
        return None

    # These are the same across raindrop types:
    request.collection = get_from_list(
        cli,
        ("create", "collection"),
        list(cli.state.get_collection_titles(exclude_unsorted=True)),
    )
    if request.collection is None:
        return None

    request.tags = get_from_list(cli, ("create", "tag(s)"), list(cli.state.tags))
    if request.tags is None:
        return None

    # Confirm the values that we just received are good to go...
    request.print(cli.console.print)
    if __get_confirmation(cli, "Is this correct?"):
        return request
    return None


def _add_single(
    cli: CLI,
    file: bool = False,
    url: bool = False,
    request: CreateRequest = None,
    interstitial: int = 1,
) -> bool:
    """Create either a link or file-based Raindrop, if we don't have a request yet, get one."""
    assert (
        file or url
    ) or request, "Sorry, either a file/url flag or an create request is required"
    if not request:
        request: CreateRequest = _prompt_for_request(cli, file=file, url=url)
        if not request:
            return False  # User might have requested that we could still get out..

    # Convert from /name/ of collection user entered to an /instance/
    # of a Collection; if necessary, creating a new one through the
    # respective Raindrop API.
    request.collection = Collection.get_or_create(cli.state.api, request.collection)

    # Push it up!
    with Spinner(f"Adding Raindrop -> {request.name()}..."):
        create_method = _create_link if url else _create_file
        create_method(cli.state.api, request)

    # Be nice to raindrop.io and wait a bit..
    if interstitial:
        sleep(interstitial)

    return True


def _add_bulk(cli: CLI) -> None:

    while True:  # ie, Until we get a valid file..
        fn_request = __get_file(cli)
        if fn_request is None:
            return None

        fp_request: Path = Path(fn_request).expanduser()
        if not fp_request.exists():
            cli.console.print(
                f"Sorry, unable to find request_toml file: '{fp_request}'\n",
            )
            continue

        with open(fp_request, "rb") as fh_request:
            requests: list[CreateRequest] = [
                CreateRequest.factory(entry)
                for entry in load(fh_request).get("requests", [])
            ]

        # Filter down to only valid entries:
        requests: list[CreateRequest] = [
            req for req in requests if _is_request_valid(cli, req)
        ]
        if not requests:
            cli.console.print("Sorry, no valid requests found.\n")
            break

        # Confirm that we're good to go
        if not __get_confirmation(
            cli,
            f"Ready to create {len(requests)} valid requests, Ok?",
        ):
            return None

        # Add em!
        return sum([_add_single(cli, None, request) for request in requests])


def iteration(cli: CLI) -> bool:
    """Run a single iteration of our command/event-loop.

    Returns True if we're done, otherwise, keep asking for 'create's.
    """
    options: Final = ["url", "file", "bulk", "back", "."]
    cli.console.print(options_as_help(options))
    response = cli.session.prompt(
        cli_prompt(("create",)),
        completer=WordCompleter(options),
        style=PROMPT_STYLE,
        complete_while_typing=True,
        enable_history_search=False,
    )

    if response.casefold() in ("back", "."):
        return False

    elif response.casefold() in ("?",):
        cli.console.print(options_as_help(options))
        return True

    elif response.casefold() == "bulk":
        _add_bulk(cli)
        return True

    elif response.casefold() == "file":
        _add_single(cli, file=True)
        return True

    elif response.casefold() == "url":
        _add_single(cli, url=True)
        return True

    else:
        cli.console.print(f"Sorry, must be one of {', '.join(options)}.")


def process(cli: CLI) -> None:
    """Controller for adding bookmark(s) from the terminal."""
    while iteration(cli):
        ...
