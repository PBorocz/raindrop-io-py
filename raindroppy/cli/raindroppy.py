#!/usr/bin/env py
"""Entry point for primary CLI interaction.."""
import os
import sys

import fire
from beaupy import console
from dotenv import load_dotenv
from loguru import logger as log
from raindropio import API

from .command_add import do_add
from .command_upload import do_upload

load_dotenv()

API = API(os.environ["RAINDROP_TOKEN"])


def add() -> None:
    """Interactively upload a file to create a new bookmark."""
    do_add(API)


def upload(upload_toml: str = None):
    """Bulk upload one or more files based on a TOML file specification."""
    do_upload(API, upload_toml=upload_toml, validate=True)


if __name__ == "__main__":

    # Setup logging...
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
    console.print("\nThanks/Gracias/Merci/Danka/ありがとう/спасибо/Köszönöm!")
