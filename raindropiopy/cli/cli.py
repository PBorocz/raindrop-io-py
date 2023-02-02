"""Startup/entry point for command-line interface."""
# This is meant to be packaged up as a module-level executable, thus, no hash-bang here.
# Still can be run directly though as: python raindropiopy/cli/cli.py
import os
import sys

from dotenv import load_dotenv

from raindropiopy.cli.models.eventLoop import EventLoop
from raindropiopy.cli.models.raindropState import RaindropState


def main():
    """Driver to kick off command-line interface."""
    load_dotenv()

    # Check that we have Raindrop connection token defined and available.
    if not os.getenv("RAINDROP_TOKEN"):
        sys.stderr.print(
            "Sorry, we need an environment variable (RAINDROP_TOKEN) to connect to the Raindrop.io service.\n",
        )
        sys.exit(1)

    EventLoop().go(RaindropState.factory())


if __name__ == "__main__":
    main()
