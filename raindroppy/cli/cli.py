"""Top level command-line interface controller."""
from io import StringIO
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import FileHistory
from pyfiglet import Figlet
from rich.console import Console

from raindroppy.cli import PROMPT_STYLE, cli_prompt, make_italic, options_as_help
from raindroppy.cli.models import RaindropState


# Utility method to return the command-history file path for the user
# (creating directories if necessary)
def _get_user_history_path() -> Path:
    history_path = Path("~/.config/raindroppy").expanduser()
    history_path.mkdir(parents=True, exist_ok=True)

    history_file = history_path / Path(".cli_history")
    if not history_file.exists():
        open(history_file, "a").close()
    return history_file


class CLI:
    """Top-level command-line interface controller/command-loop."""

    text_goodbye = (
        "[italic]Thanks, Gracias, Merci, Danka, ありがとう, спасибо, Köszönöm...!\n[/]"
    )

    def _display_startup_banner(self) -> None:
        banner: str = "RaindropPY"
        welcome: str = (
            f"""Welcome to RaindropPY!\n"""
            f"""{make_italic('<tab>')} to complete; """
            f"""{make_italic('help')} for help; """
            f"""{make_italic('Ctrl-D')} or {make_italic('q')} to exit."""
        )
        # We can't use self.console.print as the special characters will be interpreted by Rich.
        print(Figlet(font="standard").renderText(banner))
        self.console.print(welcome)

    def __init__(self, capture: StringIO = None) -> None:
        """Setup our interface components and show our our startup banner.

        For testing, allow for an internal capture of Console output through the respective arg.
        """
        self.console = Console(file=capture)
        self.session = PromptSession(history=FileHistory(_get_user_history_path()))
        self.state: None  # Will be populated when we start our event loop.
        self._display_startup_banner()

    def iteration(self):
        """Run a single iteration of our command/event-loop."""
        options = ["search", "create", "manage", "exit", "quit", "."]

        self.console.print(options_as_help(options))

        response = self.session.prompt(
            cli_prompt(),
            completer=WordCompleter(options),
            style=PROMPT_STYLE,
            complete_while_typing=True,
            enable_history_search=False,
        )

        if response.casefold() in ("exit", "bye", "quit", "."):
            raise KeyboardInterrupt  # Quick way out...

        elif response.casefold() in ("?",):
            # FIXME: This should be a longer help text here
            # (since we print the options at the top of each
            # iteration already)
            self.console.print(options_as_help(options))
            return

        # We have a valid command, bring in the right module (yes, statically)
        # and dispatch appropriately.
        process_method = None
        if response.casefold() in ("help",):
            from raindroppy.cli.commands.help import process as process_method

        elif response.casefold() in ("search",):
            from raindroppy.cli.commands.search import process as process_method

        elif response.casefold() == "create":
            from raindroppy.cli.commands.create import process as process_method

        elif response.casefold() == "manage":
            from raindroppy.cli.commands.manage import process as process_method

        else:
            # Else case here doesn't matter as if process_method isn't set,
            # we'll simply show the list of commands at the top of the next
            # iteration.
            return

        process_method(self)

    def event_loop(self, state: RaindropState) -> None:
        """Save state and run the top-level menu/event loop prompts."""
        self.state = state

        while True:
            try:
                self.iteration()
            except (KeyboardInterrupt, EOFError):
                self.console.print(CLI.text_goodbye)
                break
