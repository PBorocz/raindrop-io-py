"""Add/Create a new file-based bookmark to Raindrop."""
from pathlib import Path
from typing import Optional

from beaupy import confirm, console, prompt, select, select_multiple
from beaupy.spinners import DOTS, Spinner
from command_upload import do_upload
from models import RaindropState, UploadRequest
from raindropio import api
from utilities import get_existing_state

CURSOR_STYLE = "red"
DEFAULT_DIR = Path("~/Downloads/Raindrop").expanduser()


def _read_files(path_: Path) -> list[Path]:
    """Confirm that inbound directory is good and return all PDF's in it."""
    assert path_.exists(), f"Sorry, '{path_}' doesn't exist!"
    return list(path_.glob("*.pdf"))


def _prompt_for_upload(raindrop_state, files) -> Optional[UploadRequest]:
    """Prompt for an upload and return request or None (if not confirmed)."""
    upload_request = UploadRequest()
    upload_request.file_path = select(files, cursor_style=CURSOR_STYLE)
    upload_request.title = prompt("Title:", initial_value=upload_request.file_path.stem)
    upload_request.collection = select(list(raindrop_state.collections), cursor_style=CURSOR_STYLE)
    upload_request.tags = select_multiple(list(raindrop_state.tags), cursor_style=CURSOR_STYLE)

    # Print summary and confirm if OK
    console.print(f"Uploading file  : {upload_request.file_path.name}")
    console.print(f"With title      : {upload_request.title}")
    console.print(f"To collection   : {upload_request.collection}")
    console.print(f"With tags       : {upload_request.tags}")
    if confirm("\nIs this correct?"):
        return upload_request
    return None


def do_add(api: api.API) -> None:
    """UI Controller for adding any number of bookmarks from the terminal."""
    # Read the current set of collections and tags available.
    raindrop_state: RaindropState = get_existing_state(api, casefold=False)

    # Read the set of files available for upload
    files: list[Path] = _read_files(DEFAULT_DIR)

    while True:
        if upload_request := _prompt_for_upload(raindrop_state, files):

            spinner = Spinner(DOTS, "Uploading to Raindrop...")
            spinner.start()
            count_uploaded: int = do_upload(api, upload_request, validate=False)
            spinner.stop()

            msg: str = "Successfully uploaded!" if count_uploaded == 1 else "Sorry, something didn't work..."
            console.print(msg)

        if not confirm("\nWould you like to upload another?"):
            break
