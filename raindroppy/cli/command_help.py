"""Display help"""
from ._cli import CLI


def process(cli: CLI) -> None:
    """Controller to display help"""
    cli.console.print("Help is here, never fear!")
