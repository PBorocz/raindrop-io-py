#!/usr/bin/env python
"""Entry point for primary CLI interaction.."""
import os
import sys
from pathlib import Path

import fire
from beaupy import console
from dotenv import load_dotenv
from loguru import logger as log

from raindroppy.api import API
from raindroppy.cli.command_add import do_add
from raindroppy.cli.command_upload import do_upload

load_dotenv()

CNXN = API(os.environ["RAINDROP_TOKEN"])


def add(debug: bool = False, dir_path: str = "~/Downloads") -> None:
    """Interactively upload a file to create a new bookmark."""
    do_add(CNXN, dir_path=Path(dir_path), debug=debug)


def upload(upload_toml: str = None, debug: bool = False):
    """Bulk upload one or more files based on a TOML file specification."""
    do_upload(CNXN, upload_toml=upload_toml, validate=True, debug=debug)


if __name__ == "__main__":

    # Setup logging (which may or may not be used)
    log.remove()
    log.add(
        sys.stderr,
        colorize=True,
        format="<green>{time:HH:mm:ss}</> | <cyan>{level}</> | <le>{file}:{line}</> | {message}",
    )

    # ..and dispatch
    fire.Fire(
        {
            "add": add,
            "upload": upload,
        }
    )
    console.print("Thanks/Gracias/Merci/Danka/ありがとう/спасибо/Köszönöm\n")
