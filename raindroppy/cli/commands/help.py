"""Display help"""
from raindroppy.cli._cli import CLI


def process(cli: CLI) -> None:
    """Controller to display help"""
    cli.console.print("Help is here, never fear!")
