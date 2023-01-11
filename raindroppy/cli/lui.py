"""Top level command-line interface controller."""
from typing import Final

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from pyfiglet import Figlet
from rich.console import Console
from utilities import get_user_history_path

from cli import PROMPT_STYLE, cli_prompt, make_italic, options_as_help
from cli.models import RaindropState


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
            f"""Welcome to RaindropPY!\n"""
            f"""{make_italic('<tab>')} to complete; """
            f"""{make_italic('help')} for help; """
            f"""{make_italic('Ctrl-D')} or {make_italic('q')} to exit."""
        )
        # We can't use self.console.print as the special characters will be interpreted by Rich.
        print(Figlet(font="standard").renderText(banner))
        self.console.print(text_intro)

    def loop(self):
        """Menu/event loop."""

        text_goodbye = "\n[italic]Thanks, Gracias, Merci, Danka, ありがとう, спасибо, Köszönöm...!\n[/]"

        self.banner()

        # Setup our connection *after* displaying the banner.
        self.state = RaindropState.factory(self)

        options = ["search", "create", "manage", "exit"]
        completer: Final = WordCompleter(options)

        while True:
            try:
                self.console.print(options_as_help(options))
                response = self.session.prompt(
                    cli_prompt(),
                    completer=completer,
                    style=PROMPT_STYLE,
                    complete_while_typing=True,
                    enable_history_search=False,
                )

                if response.casefold() in ("exit", "bye", "quit", "."):
                    raise KeyboardInterrupt
                elif response.casefold() in ("?",):
                    self.console.print(options_as_help(options))
                elif response.casefold() in ("help",):
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
