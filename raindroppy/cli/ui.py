"""Top level command-line interface controller."""
from beaupy import Config, DefaultKeys, console, select
from cli.models import RaindropState
from pyfiglet import Figlet
from yakh.key import Keys

# Configure the Beaupy environment, specifically for Emacs support.
DefaultKeys.down.append(Keys.CTRL_N)
DefaultKeys.up.append(Keys.CTRL_P)
DefaultKeys.escape.append(Keys.CTRL_Q)

Config.raise_on_interrupt = True


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

        commands = {
            "Create A New Raindrop Bookmark": self.create,
            "Manage Your Raindrop Environment": self.manage,
            "Exit": None,
        }
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

    def create(self, debug: bool = False) -> None:
        """Interactively create one or more new Raindrop bookmarks."""
        from cli.command_create import process

        process(self)
        self.new_screen()

    def manage(self, debug: bool = False) -> None:
        """Connection environment related functions."""
        from cli.command_manage import process

        process(self)
        self.new_screen()
