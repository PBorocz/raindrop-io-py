"""Startup/entry point for command-line interface.."""
from dotenv import load_dotenv

from raindroppy.cli.models.eventLoop import EventLoop
from raindroppy.cli.models.raindropState import RaindropState


def main():
    """Driver to kick off CLI."""
    load_dotenv()
    EventLoop().go(RaindropState.factory())


if __name__ == "__main__":
    main()
