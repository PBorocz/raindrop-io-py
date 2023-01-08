"""Abstract data types to support Rainddrop CLI."""
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TypeVar

from api import API, Collection, Tag, User
from beaupy import Config, DefaultKeys, console, select
from beaupy.spinners import DOTS, Spinner
from pyfiglet import Figlet
from yakh.key import Keys

# Yay and thou shall give us Emacs...
DefaultKeys.down.append(Keys.CTRL_N)
DefaultKeys.up.append(Keys.CTRL_P)
DefaultKeys.escape.append(Keys.CTRL_Q)
Config.raise_on_interrupt = True


RaindropState = TypeVar("RaindropState")  # In py3.11, we'll be able to do 'from typing import Self' instead


@dataclass
class RaindropState:
    """Encapsulate all aspects for current state of the Raindrop environment."""

    api: API
    created: datetime
    user: User
    collections: list[Collection] = None
    tags: list[str] = None
    refreshed: datetime = None

    def get_collection_titles(self):
        return sorted([collection.title for collection in self.collections])

    def find_collection(self, title):
        for collection in self.collections:
            if title.casefold() == collection.title.casefold():
                return collection
        return None

    def refresh(self, casefold: bool = True, verbose: bool = True) -> bool:
        """Refresh the current state of this Raindrop environment (ie. current collections and tags available)."""

        def _cf(casefold: bool, string: str) -> str:
            if casefold:
                return string.casefold()
            return string

        if verbose:
            msg = "Refreshing Raindrop Status..."
            spinner = Spinner(DOTS, msg)
            spinner.start()

        # What collections do we currently have on Raindrop?
        collections: list[Collection] = [root for root in Collection.get_roots(self.api)]
        collections.extend([child for child in Collection.get_childrens(self.api)])
        self.collections = sorted(collections, key=lambda collection: getattr(collection, "title", ""))

        # What tags we currently have available on Raindrop across
        # *all* collections? (use set to get rid of potential
        # duplicates)
        tags: set[str] = set([_cf(casefold, tag.tag) for tag in Tag.get(self.api)])
        self.tags = list(sorted(tags))
        self.refreshed = datetime.utcnow()

        if verbose:
            spinner.stop()

        return True

    @classmethod
    def factory(verbose: bool = True) -> RaindropState:
        """Factory to log into Raindrop and return a new Raindrop State instance."""

        if verbose:
            msg = "Logging into Raindrop..."
            spinner = Spinner(DOTS, msg)
            spinner.start()

        # Setup our connection to Raindrop
        api: API = API(os.environ["RAINDROP_TOKEN"])

        # What user are we currently defined "for"?
        user = User.get(api)

        if verbose:
            spinner.stop()

        state = RaindropState(api=api, user=user, created=datetime.utcnow())

        # And, do our first refresh.
        state.refresh()

        return state


################################################################################
class RaindropType(Enum):
    URL = 1  # Create interactively a URL-based Raindrop.
    FILE = 2  # Create interactively a file-based Raindrop.
    BULK = 3  # Get parameters to bulk load Raindrops from a file.


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

    def __str__(self):
        return_ = list()
        if self.title:
            return_.append(f"Title      : {self.title}")
        if self.url:
            return_.append(f"URL        : {self.url}")
        if self.file_path:
            return_.append(f"File       : {self.file_path}")
        if self.collection:
            return_.append(f"Collection : {self.collection}")
        if self.tags:
            return_.append(f"Tag(s)     : {self.tags}")
        return "\n".join(return_)


################################################################################
class CLI:
    """Command-line interface controller."""

    def __init__(self):
        """Setup connection to Raindrop and run the ui event loop."""
        self.console = console
        self.state: RaindropState = None
        self.loop()

    def new_screen(self):
        self.console.clear()
        text_intro = "Welcome to RaindropPY!"
        self.console.print(Figlet(font="standard").renderText("Raindrop-PY"))
        self.console.print(text_intro)

    def loop(self):
        """Menu/event loop."""

        def _italic(str_):
            return f"[italic]{str_}[/italic]"

        text_goodbye = """\n[italic]Thanks, Gracias, Merci, Danka, ありがとう, спасибо, Köszönöm...!\n[/]"""

        self.new_screen()

        # Setup our connection *after* displaying the banner.
        self.state = RaindropState.factory()

        commands = {"Add": self.add, "Show": self.show, ".Refresh": self.refresh, "Exit": None}

        while True:
            try:
                response = select(list(commands.keys()))
                method = commands.get(response)
                if method is None:
                    self.console.print(text_goodbye)  # We're done..
                    break
                method()
            except (KeyboardInterrupt, EOFError):
                self.console.print(text_goodbye)
                break

    def add(self, debug: bool = False) -> None:
        """Interactively create one or more new Raindrop bookmarks."""
        from cli.commands.add import do_add

        do_add(self)
        self.new_screen()

    def show(self, debug: bool = False) -> None:
        """Display selected statistics about our environment."""
        from cli.commands.show import do_show

        do_show(self)
        self.new_screen()

    def refresh(self, debug: bool = False) -> None:
        """Refresh the current connection status"""
        self.state.refresh()
        self.new_screen()
