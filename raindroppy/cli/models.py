"""Abstract data types to support Rainddrop CLI."""
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from api import API, Collection, Tag, User
from beaupy import Config, DefaultKeys, console, select
from beaupy.spinners import DOTS, Spinner
from yakh.key import Keys

# Yay and thou shall give us Emacs...
DefaultKeys.down.append(Keys.CTRL_N)
DefaultKeys.up.append(Keys.CTRL_P)
DefaultKeys.escape.append(Keys.CTRL_Q)


@dataclass
class RaindropState:
    """Encapsulate all aspects for current state of the Raindrop environment using the API connection provided."""

    collections: list[str]
    last_refresh: datetime
    tags: list[str]
    user: User


def get_current_state(api: API, casefold: bool = True, verbose: bool = False) -> RaindropState:
    """Return the current state of the Raindrop environment (ie. current collections and tags available)."""

    def _cf(casefold: bool, string: str) -> str:
        if casefold:
            return string.casefold()
        return string

    if verbose:
        msg = "Getting current state of Raindrop environment..."
        spinner = Spinner(DOTS, msg)
        spinner.start()

    # What user are we currently defined "for"?
    user = User.get(api)

    # What collections do we currently have on Raindrop?
    collections: set[str] = set([_cf(casefold, root.title) for root in Collection.get_roots(api)])
    collections.union([_cf(casefold, child.title) for child in Collection.get_childrens(api)])

    # What tags we currently have available on Raindrop across *all* collections?
    tags: set[str] = set([_cf(casefold, tag.tag) for tag in Tag.get(api)])

    if verbose:
        spinner.stop()

    return RaindropState(
        user=user, collections=list(sorted(collections)), tags=list(sorted(tags)), last_refresh=datetime.utcnow()
    )


################################################################################
class RaindropType(Enum):
    URL = 1
    FILE = 2


@dataclass
class CreateRequest:
    """Encapsulate parameters required to create a *file*-based Raindrop bookmark."""

    title: str = None  # Bookmark title on Raindrop, eg. "Please Store Me"
    collection: str = None  # Name of collection to store bookmark, eg. "My Documents"
    tags: list[str] = None  # Optional list of tags to associate, eg. ["'aTag", "Another Tag"]

    # One of the following needs to be specified:
    type_: RaindropType = RaindropType.URL
    url: str = None  # *URL* of link-based Raindrop to create.
    file_path: Path = None  # *Path* to file to be created, eg. /home/me/Documents/foo.pdf


################################################################################
class CLI:
    """Command-line interface controller."""

    def __init__(self):
        """Setup connection to Raindrop and run the ui event loop."""
        console.print("Welcome!")
        self.api = API(os.environ["RAINDROP_TOKEN"])
        self.state: RaindropState = None  # Set when we need it.
        self.loop()

    def loop(self):
        """Menu/event loop."""
        Config.raise_on_interrupt = True

        while 1:
            console.clear()
            action = select(["Status", "Add", "Create", "Exit"])
            if action == "Add":
                self.add()

            elif action == "Create":
                self.create()

            elif action == "Exit":
                break  # Say Goodnight, Gracie!

            elif action == "Status":
                self.status()

        console.print("\nThanks, Gracias, Merci, Danka, ありがとう, спасибо, Köszönöm...!\n")

    def add(self, debug: bool = False) -> None:
        """Interactively create a new Raindrop bookmark (for either link or files)"""
        from cli.commands.add import do_add

        do_add(self, debug=debug)

    def create(self, create_toml: str = None, debug: bool = False):
        """Bulk create one or more Raindrops based on a TOML file specification."""
        from cli.commands.create import do_create

        do_create(self, create_toml=create_toml, validate=True, debug=debug)

    def status(self, create_toml: str = None, debug: bool = False):
        """Bulk create one or more Raindrops based on a TOML file specification."""
        from cli.commands.status import do_status

        do_status(self)
