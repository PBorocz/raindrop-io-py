"""Display current status of Raindrop API connection."""
from datetime import datetime

from humanize import naturaltime
from run import CLI  # Typing


def do_status(cli: CLI) -> None:
    """UI Controller for displaying current status."""
    human_diff = naturaltime(datetime.utcnow() - cli.state.last_refresh)
    cli.console.print(f"Active User : {cli.state.user.fullName}")
    cli.console.print(f"Collections : {len(cli.state.collections):3d}")
    cli.console.print(f"Tags        : {len(cli.state.tags):3d}")
    cli.console.print(f"As Of       : {human_diff}")
