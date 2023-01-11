"""Display help"""
from cli.lui import LI


def process(li: LI) -> None:
    """Display help"""
    li.console.print("Help is here, never fear!")
