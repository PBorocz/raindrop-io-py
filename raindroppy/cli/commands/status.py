"""Display current status of Raindrop API connection."""
from datetime import datetime

from beaupy import console
from cli.models import get_current_state
from humanize import naturaltime
from models import RaindropState  # Typing
from run import CLI  # Typing


def do_status(cli: CLI) -> None:
    """UI Controller for displaying current status."""
    if not cli.state:
        cli.state: RaindropState = get_current_state(cli.api, casefold=False, verbose=True)

    console.print(f"Active User : {cli.state.user.fullName}")
    console.print(f"Collections : {len(cli.state.collections):3d}")
    console.print(f"Tags        : {len(cli.state.tags):3d}")

    diff = datetime.utcnow() - cli.state.last_refresh
    console.print(f"Last Refreshed : {naturaltime(diff)}")

    input("\npress any key to continue...")
