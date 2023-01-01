#!/usr/bin/env python
"""Entry point for primary CLI interaction.."""
import os
import sys
from pathlib import Path

import fire
from beaupy import console, select
from dotenv import load_dotenv

from raindroppy.api import API
from raindroppy.cli.commands.add import do_add
from raindroppy.cli.commands.create import do_create

load_dotenv()


def add(api: API, debug: bool = False, dir_path: str = "~/Downloads") -> None:
    """Interactively create a new file-based Raindrop bookmark."""
    do_add(api, dir_path=Path(dir_path), debug=debug)


def create(api: API, create_toml: str = None, debug: bool = False):
    """Bulk create one or more Raindrops based on a TOML file specification."""
    do_create(api, create_toml=create_toml, validate=True, debug=debug)


class CLI:
    """asdfasdfasdf."""

    def __init__(self):
        """asdfasdfasdf."""
        console.print("Welcome!")
        self.api = API(os.environ["RAINDROP_TOKEN"])
        self.loop()

    def loop(self):
        """adsfasdfasdf."""
        while 1:
            console.clear()
            action = select(["Add", "Create", "Exit"])
            if action == "Add":
                do_add(self.api)

            elif action == "Create":
                do_create(self.api)

            elif action == "Exit":
                console.print("\nThanks/Gracias/Merci/Danka/ありがとう/спасибо/Köszönöm!\n")
                sys.exit(0)


if __name__ == "__main__":
    fire.Fire(CLI, name="RaindropPY CLI")
    # fire.Fire(
    #     {
    #         "add": add,
    #         "create": create,
    #     }
    # )
