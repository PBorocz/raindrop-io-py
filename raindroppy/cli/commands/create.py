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
    options_as_help,
    prompt,
)
from raindroppy.cli.commands import get_from_list
from raindroppy.cli.models.createRequest import CreateRequest
from raindroppy.cli.models.eventLoop import EventLoop
from raindroppy.cli.models.spinner import Spinner


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


def __get_url(el: EventLoop) -> Optional[str]:
    ev_prompt = prompt(("create", "url?"))
    while True:
        url = el.session.prompt(ev_prompt, style=PROMPT_STYLE)
        if url == "?" or url == "" or url is None:
            el.console.print(
                "We need a valid URL here, eg. https://www.python.org",
            )
        elif url == "q":
            return None
        else:
            if msg := __validate_url(url):
                el.console.print(msg)
            else:
                return url


def __get_title(el: EventLoop) -> Optional[str]:
    ev_prompt = prompt(("create", "title?"))
    while True:
        title = el.session.prompt(ev_prompt, style=PROMPT_STYLE)
        if title == "?":
            el.console.print(
                "We need a Bookmark title here, eg. 'This is an interesting bookmark'",
            )
        elif title == "q":
            return None
        else:
            return title


def __get_file(el: EventLoop) -> Optional[str]:
    el_prompt = prompt(("create", "bulk", "upload file?"))
    while True:
        file_ = el.session.prompt(el_prompt, style=PROMPT_STYLE)
        if file_ == "?":
            el.console.print(
                "We need a path to a valid, TOML upload file, eg. '/Users/me/Download/upload.toml'",
            )
        elif file_ == "q":
            return None
        else:
            return file_


def __get_from_files(el: EventLoop, options: list[Path]) -> Optional[str]:
    el_prompt = prompt(("create", "url", "file #?"))
    names = [fp_.name for fp_ in options]
    completer: Final = WordCompleter(names)
    for ith, fp_ in enumerate(options):
        el.console.print(f"{ith:2d} {fp_.name}")
    while True:
        response = el.session.prompt(
            el_prompt,
            completer=completer,
            style=PROMPT_STYLE,
            complete_while_typing=True,
            enable_history_search=False,
        )
        if response == "?":
            el.console.print(", ".join(options))
        else:
            break

    return options[int(response)]


def __get_confirmation(el: EventLoop, prompt: str) -> bool:
    el_prompt: Final = [("class:prompt", "\nIs this correct? ")]
    options: Final = ["yes", "Yes", "No", "no"]
    completer: Final = WordCompleter(options)
    response = el.session.prompt(
        el_prompt,
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


def _is_request_valid(el: EventLoop, request: CreateRequest) -> bool:
    """Return True iff the request is valid."""
    # Error Check: Validate the existence of the specified file for
    if request.file_path:
        if not request.file_path.exists():
            el.console.print(
                f"Sorry, no file with name '{request.file_path}' exists.\n",
            )
            return False

        # Validate the file type
        if request.file_path.suffix not in CONTENT_TYPES:
            el.console.print(
                f"Sorry, file type {request.file_path.suffix} isn't yet supported by Raindrop.io.\n",
            )
            return False

    # Error Check: Validate any tags associated with the request
    if request.tags:
        for tag in request.tags:
            if tag.casefold() not in el.state.tags:
                el.console.print(f"Sorry, {tag=} does not currently exist.\n")
                return False

    # Warning only: check for collection existence
    if request.collection:
        if el.state.find_collection(request.collection) is None:
            el.console.print(
                f"Collection '{request.collection}' doesn't exist "
                "in Raindrop, we'll be adding it from scratch.\n",
            )

    return True


def _prompt_for_request(
    el: EventLoop,
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
        request.url = __get_url(el)
        if request.url is None:
            return None
        if not _is_request_valid(el, request):
            return None
    else:
        files = _read_files(dir_path.expanduser())
        request.file_path = __get_from_files(
            el,
            sorted(files, key=lambda fp_: fp_.name),
        )

    # Get a Title:
    request.title = __get_title(el)
    if request.title is None:
        return None

    # These are the same across raindrop types:
    request.collection = get_from_list(
        el,
        ("create", "collection"),
        list(el.state.get_collection_titles(exclude_unsorted=True)),
    )
    if request.collection is None:
        return None

    request.tags = get_from_list(el, ("create", "tag(s)"), list(el.state.tags))
    if request.tags is None:
        return None

    # Confirm the values that we just received are good to go...
    request.print(el.console.print)
    if __get_confirmation(el, "Is this correct?"):
        return request
    return None


def _add_single(
    el: EventLoop,
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
        request: CreateRequest = _prompt_for_request(el, file=file, url=url)
        if not request:
            return False  # User might have requested that we could still get out..

    # Convert from /name/ of collection user entered to an /instance/
    # of a Collection; if necessary, creating a new one through the
    # respective Raindrop API.
    request.collection = Collection.get_or_create(el.state.api, request.collection)

    # Push it up!
    with Spinner(f"Adding Raindrop -> {request.name()}..."):
        create_method = _create_link if url else _create_file
        create_method(el.state.api, request)

    # Be nice to raindrop.io and wait a bit..
    if interstitial:
        sleep(interstitial)

    return True


def _add_bulk(el: EventLoop) -> None:

    while True:  # ie, Until we get a valid file..
        fn_request = __get_file(el)
        if fn_request is None:
            return None

        fp_request: Path = Path(fn_request).expanduser()
        if not fp_request.exists():
            el.console.print(
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
            req for req in requests if _is_request_valid(el, req)
        ]
        if not requests:
            el.console.print("Sorry, no valid requests found.\n")
            break

        # Confirm that we're good to go
        if not __get_confirmation(
            el,
            f"Ready to create {len(requests)} valid requests, Ok?",
        ):
            return None

        # Add em!
        return sum([_add_single(el, None, request) for request in requests])


def iteration(el: EventLoop) -> bool:
    """Run a single iteration of our command/event-loop.

    Returns True if we're done, otherwise, keep asking for 'create's.
    """
    options: Final = ["(u)rl", "(f)ile", "(m)ultiple", "(b)ack or ."]
    el.console.print(options_as_help(options))
    response = el.session.prompt(
        prompt(("create",)),
        completer=WordCompleter(options),
        style=PROMPT_STYLE,
        complete_while_typing=True,
        enable_history_search=False,
    )

    if response.casefold() in ("back", "b", "."):
        return False

    elif response.casefold() in ("?",):
        el.console.print(options_as_help(options))
        return True

    elif response.casefold() in ("url", "u"):
        _add_single(el, url=True)
        return True

    elif response.casefold() in ("file", "f"):
        _add_single(el, file=True)
        return True

    elif response.casefold() in ("multiple", "m"):
        _add_bulk(el)
        return True

    else:
        el.console.print(f"Sorry, must be one of {', '.join(options)}.")


def process(el: EventLoop) -> None:
    """Controller for adding bookmark(s) from the terminal."""
    while iteration(el):
        ...
