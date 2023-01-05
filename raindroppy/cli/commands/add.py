"""Add/Create a new file-based bookmark to Raindrop."""
from pathlib import Path
from typing import Optional

from beaupy import confirm, console, prompt, select, select_multiple
from beaupy.spinners import DOTS, Spinner
from cli.commands.create import do_create
from cli.models import CLI
from models import CreateRequest, RaindropState, get_current_state

CURSOR_STYLE = "red"


def _read_files(path_: Path) -> list[Path]:
    """Confirm that inbound directory is good and return all PDF's in it."""
    assert path_.exists(), f"Sorry, '{path_}' doesn't exist!"
    return list(path_.glob("*.pdf"))


def _prompt_for_link_request(raindrop_state) -> Optional[CreateRequest]:
    """Prompt for a link-based Raindrop create and return request or None (if not confirmed)."""
    create_request = CreateRequest()
    create_request.url = prompt("URL:")
    create_request.title = prompt("Title:")
    create_request.collection = select(list(raindrop_state.collections))
    create_request.tags = select_multiple(list(raindrop_state.tags))

    console.print(f"URL           : {create_request.url}")
    console.print(f"With title    : {create_request.title}")
    console.print(f"To collection : {create_request.collection}")
    console.print(f"With tags     : {create_request.tags}")

    if confirm("\nIs this correct?"):
        return create_request
    return None


def _prompt_for_file_request(raindrop_state, files) -> Optional[CreateRequest]:
    """Prompt for an file-based Raindrop create and return request or None (if not confirmed)."""
    create_request = CreateRequest()
    create_request.file_path = select(files)
    create_request.title = prompt("Title:", initial_value=create_request.file_path.stem)
    create_request.collection = select(list(raindrop_state.collections))
    create_request.tags = select_multiple(list(raindrop_state.tags))

    console.print(f"File to send  : {create_request.file_path.name}")
    console.print(f"With title    : {create_request.title}")
    console.print(f"To collection : {create_request.collection}")
    console.print(f"With tags     : {create_request.tags}")

    if confirm("\nIs this correct?"):
        return create_request
    return None


def do_add(cli: CLI, debug: bool = False) -> None:
    """Top-level UI Controller for adding bookmarks from the terminal."""
    type_ = select(["Add a Link", "Add a File", "(back)"])
    if "back" in type_:
        return None

    # Read the current set of collections and tags available at the moment...
    cli.state: RaindropState = get_current_state(cli.api, casefold=False)

    if "link" in type_.casefold():
        return do_add_link(cli)
    elif "file" in type_.casefold():
        return do_add_file(cli)


def do_add_link(cli: CLI, debug: bool = False) -> None:
    """UI Controller for adding any number of *link-based* bookmarks from the terminal."""
    while True:
        if create_request := _prompt_for_link_request(cli.state):

            msg = "Pushing to Raindrop..."
            if debug:
                console.print(msg)
            else:
                spinner = Spinner(DOTS, msg)
                spinner.start()

            count_done: int = do_create(cli.api, create_request, validate=False)

            if not debug:
                spinner.stop()

            msg: str = "Success!" if count_done == 1 else "Sorry, something didn't work..."
            console.print(msg)

        if not confirm("\nWould you like to create another?"):
            break


def do_add_file(cli: CLI, dir_path: str = "~/Downloads", debug: bool = False) -> None:
    """UI Controller for adding any number of *file-based* bookmarks from the terminal."""
    # Read the current set of collections and tags available at the moment...
    cli.state: RaindropState = get_current_state(cli.api, casefold=False, debug=debug)

    # Read the set of files available from the directory specified.
    files: list[Path] = _read_files(dir_path.expanduser())

    while True:
        if create_request := _prompt_for_file_request(cli.state, files):

            msg = "Pushing to Raindrop..."
            if debug:
                console.print(msg)
            else:
                spinner = Spinner(DOTS, msg)
                spinner.start()

            count_done: int = do_create(cli.api, create_request, validate=False)

            if not debug:
                spinner.stop()

            msg: str = "Success!" if count_done == 1 else "Sorry, something didn't work..."
            console.print(msg)

        if not confirm("\nWould you like to create another?"):
            break
