"""Abstract data types to support Rainddrop CLI."""
import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

from api import API, Collection, Tag, User

# from beaupy import Config, DefaultKeys, console, select
from prompt_toolkit import PromptSession

# from beaupy.spinners import DOTS, Spinner
from prompt_toolkit.history import FileHistory
from pyfiglet import Figlet
from rich.console import Console
from rich.spinner import Spinner

# from yakh.key import Keys

# Yay and thou shall give us Emacs...
# DefaultKeys.down.append(Keys.CTRL_N)
# DefaultKeys.up.append(Keys.CTRL_P)
# DefaultKeys.escape.append(Keys.CTRL_Q)


def _italic(str_):
    return f"[italic]{str_}[/italic]"


INTRODUCTION = f"""Welcome to RaindropPY! {_italic('Ctrl-D')} or {_italic('.exit')}/{_italic('.quit')} to exit, {_italic('.help')} for help."""
GOODBYE = """\n[italic]Thanks, Gracias, Merci, Danka, ありがとう, спасибо, Köszönöm...!\n[/]"""
PROMPT = "> "


@dataclass
class RaindropState:
    """Encapsulate all aspects for current state of the Raindrop environment."""

    api: API
    user: User
    collections: list[Collection]
    tags: list[str]
    last_refresh: datetime

    def get_collection_titles(self):
        return sorted([collection.title for collection in self.collections])

    def find_collection(self, title):
        for collection in self.collections:
            if title.casefold() == collection.title.casefold():
                return collection
        return None

    @classmethod
    def refresh(cls, casefold: bool = True, verbose: bool = False):
        """Return the current state of the Raindrop environment (ie. current collections and tags available)."""

        def _cf(casefold: bool, string: str) -> str:
            if casefold:
                return string.casefold()
            return string

        # if verbose:
        #     msg = "Logging into Raindrop..."
        #     spinner = Spinner(DOTS, msg)
        #     spinner.start()

        # Setup our connection to Raindrop
        api: API = API(os.environ["RAINDROP_TOKEN"])

        # if verbose:
        #     spinner.stop()

        # if verbose:
        #     msg = "Getting current state of Raindrop environment..."
        #     spinner = Spinner(DOTS, msg)
        #     spinner.start()

        # What user are we currently defined "for"?
        user = User.get(api)

        # What collections do we currently have on Raindrop?
        collections: list[Collection] = [root for root in Collection.get_roots(api)]
        collections.extend([child for child in Collection.get_childrens(api)])

        # What tags we currently have available on Raindrop across *all* collections?
        tags: set[str] = set([_cf(casefold, tag.tag) for tag in Tag.get(api)])

        # if verbose:
        #     spinner.stop()

        return RaindropState(
            api=api, user=user, collections=collections, tags=list(sorted(tags)), last_refresh=datetime.utcnow()
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


def get_user_history_path():
    history_path = Path("~/.config/raindroppy").expanduser()
    history_path.mkdir(parents=True, exist_ok=True)

    history_file = history_path / Path(".cli_history")
    if not history_file.exists():
        open(history_file, "a").close()
    return history_file


################################################################################
class CLI:
    """Command-line interface controller."""

    def __init__(self):
        """Setup connection to Raindrop and run the ui event loop."""
        self.console = Console()
        self.session = PromptSession(history=FileHistory(get_user_history_path()))
        self.state: RaindropState = None
        self.loop()

    def loop(self):
        """Menu/event loop."""

        # Config.raise_on_interrupt = True
        print(Figlet(font="standard").renderText("Raindrop-PY"))
        self.console.print(INTRODUCTION)

        # Setup our connection *after* displaying the banner.
        self.console.print("Connecting to Raindrop...", end="")
        self.state = RaindropState.refresh()
        self.console.print("Done")

        while True:
            try:
                response = self.session.prompt(PROMPT)
            except (KeyboardInterrupt, EOFError):
                self.console.print(GOODBYE)
                break

            if response.lower() in (".exit", ".quit"):
                self.console.print(GOODBYE)
                break

            if response:  # As Ahhhnold would say...DOO EET!
                self.execute(response)

    def execute(self, response: str) -> None:
        if response.casefold() == "add":
            self.add()

        elif response.casefold() == "create":
            self.create()

        elif response.casefold() == "status":
            self.status()

    def add(self, debug: bool = False) -> None:
        """Interactively create a new Raindrop bookmark (for either link or files)"""
        from cli.commands.add import do_add

        do_add(self, debug=debug)

    def create(self, create_toml: str = None, debug: bool = False):
        """Bulk create one or more Raindrops based on a TOML file specification."""
        from cli.commands.create import do_create

        do_create(self, create_toml=create_toml, validate=True, debug=debug)

    def status(self, create_toml: str = None, debug: bool = False):
        """Display the more recent status of our connection with Raindrop."""
        from cli.commands.status import do_status

        do_status(self)
