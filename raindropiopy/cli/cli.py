"""Startup/entry point for command-line interface.."""
import os
import sys

from dotenv import load_dotenv

from raindropiopy.cli.models.eventLoop import EventLoop
from raindropiopy.cli.models.raindropState import RaindropState


def main():
    """Driver to kick off interface."""
    load_dotenv()

    # Check that we have Raindrop connection token defined and available.
    if not os.getenv("RAINDROP_TOKEN"):
        print(
            "Sorry, we need an environment variable (RAINDROP_TOKEN) to connect to the Raindrop.io service.",
        )
        sys.exit(1)

    EventLoop().go(RaindropState.factory())


if __name__ == "__main__":
    main()
