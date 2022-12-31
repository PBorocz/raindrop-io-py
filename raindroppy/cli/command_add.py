"""Add/Create a new file-based bookmark to Raindrop."""
from pathlib import Path
from typing import Optional

from beaupy import confirm, console, prompt, select, select_multiple
from beaupy.spinners import DOTS, Spinner
from command_upload import do_upload
from models import RaindropState, UploadRequest
from utilities import get_current_state

from raindroppy.api import API

CURSOR_STYLE = "red"


def _read_files(path_: Path) -> list[Path]:
    """Confirm that inbound directory is good and return all PDF's in it."""
    assert path_.exists(), f"Sorry, '{path_}' doesn't exist!"
    return list(path_.glob("*.pdf"))


def _prompt_for_upload(raindrop_state, files) -> Optional[UploadRequest]:
    """Prompt for an upload and return request or None (if not confirmed)."""
    # Gather parameters for upload
    upload_request = UploadRequest()
    upload_request.file_path = select(files)
    upload_request.title = prompt("Title:", initial_value=upload_request.file_path.stem)
    upload_request.collection = select(list(raindrop_state.collections))
    upload_request.tags = select_multiple(list(raindrop_state.tags))

    # Print summary for user confirmation
    console.print(f"File to upload : {upload_request.file_path.name}")
    console.print(f"With title     : {upload_request.title}")
    console.print(f"To collection  : {upload_request.collection}")
    console.print(f"With tags      : {upload_request.tags}")

    # Are we good to go?
    if confirm("\nIs this correct?"):
        return upload_request
    return None


def do_add(api: API, dir_path: Path, debug: bool = False) -> None:
    """UI Controller for adding any number of file-based bookmarks from the terminal."""
    # Read the current set of collections and tags available.
    raindrop_state: RaindropState = get_current_state(api, casefold=False, debug=debug)

    # Read the set of files available for upload from the directory specified.
    files: list[Path] = _read_files(dir_path.expanduser())

    while True:
        if upload_request := _prompt_for_upload(raindrop_state, files):

            msg = "Uploading to Raindrop..."
            if debug:
                console.print(msg)
            else:
                spinner = Spinner(DOTS, msg)
                spinner.start()

            count_uploaded: int = do_upload(api, upload_request, validate=False)

            if not debug:
                spinner.stop()

            msg: str = "Successfully uploaded!" if count_uploaded == 1 else "Sorry, something didn't work..."
            console.print(msg)

        if not confirm("\nWould you like to upload another?"):
            break
