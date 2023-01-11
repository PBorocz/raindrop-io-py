"""Display help"""
from cli._cli import CLI


def process(cli: CLI) -> None:
    """Display help"""
    cli.console.print("Help is here, never fear!")
