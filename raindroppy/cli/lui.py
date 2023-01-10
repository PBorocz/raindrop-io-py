"""Top level command-line interface controller."""
from typing import Final

from cli.models import RaindropState
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from pyfiglet import Figlet
from rich.console import Console
from utilities import get_user_history_path


def _italic(str_):
    return f"[italic]{str_}[/italic]"


################################################################################
class LI:
    """Command-line interface controller."""

    def __init__(self, local: bool = True):
        """Setup connection to Raindrop and run the ui event loop."""
        self.local = local
        self.console = Console()
        self.session = PromptSession(history=FileHistory(get_user_history_path()))
        self.state: RaindropState = None
        self.loop()

    def banner(self):
        banner = "Raindrop-PY"
        text_intro = (
            f"""Welcome to RaindropPY!\n{_italic('Ctrl-D')} or {_italic('q')} to exit, {_italic('help')} for help."""
        )

        self.console.print(Figlet(font="standard").renderText(banner))
        self.console.print(text_intro)

    def loop(self):
        """Menu/event loop."""

        text_goodbye = "\n[italic]Thanks, Gracias, Merci, Danka, ありがとう, спасибо, Köszönöm...!\n[/]"

        self.banner()

        # Setup our connection *after* displaying the banner.
        self.state = RaindropState.factory(self)

        general_prompt: Final = [
            ("class:prompt", "> "),
        ]
        style: Final = Style.from_dict(
            {
                "prompt": "#00ffff",  # Prompt is cyan
                "": "#00ff00",  # User input  is green
            }
        )
        top_completer: Final = WordCompleter(
            [
                "search",
                "create",
                "manage",
                "exit",
            ]
        )
        while True:
            try:
                response = self.session.prompt(
                    general_prompt,
                    completer=top_completer,
                    style=style,
                    complete_while_typing=True,
                    enable_history_search=False,
                )

                if response.casefold() in ("exit", "bye", "quit"):
                    raise KeyboardInterrupt
                elif response.casefold() == "help":
                    self.help()
                elif response.casefold() == "create":
                    self.create()
                elif response.casefold() == "manage":
                    self.manage()
            except (KeyboardInterrupt, EOFError):
                self.console.print(text_goodbye)
                break

    def help(self, debug: bool = False) -> None:
        """Display help"""
        from cli.command_help import process

        process(self)

    def create(self, debug: bool = False) -> None:
        """Interactively create one or more new Raindrop bookmarks."""
        from cli.command_create import process

        process(self)

    def manage(self, debug: bool = False) -> None:
        """Connection environment related functions."""
        from cli.command_manage import process

        process(self)
