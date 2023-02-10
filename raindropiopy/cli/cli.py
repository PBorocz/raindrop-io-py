"""Startup/entry point for command-line interface."""
# This is meant to be packaged up as a module-level executable, thus, no hash-bang here.
# Still can be run directly though as: python raindropiopy/cli/cli.py
import argparse
import os
import sys
from pathlib import Path

import vcr  # Used when we run in "testing" mode only
from dotenv import load_dotenv
from rich import print

import raindropiopy
from raindropiopy.cli.models.event_loop import EventLoop
from raindropiopy.cli.models.raindrop_state import RaindropState


def _parse_args():
    """Parse and return all command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="RaindropIoPy",
        description="Command-line interface to the RaindropIO Bookmark Manager.",
    )

    parser.add_argument(
        "--testing",
        help="Run in 'test' mode, ie. dumb terminal, replayed raindrop interaction",
        action="store_true",
        default=False,
    )
    parser.add_argument("-v", "--verbose", action="store_true", default=False)

    args = parser.parse_args()
    return args


def main():
    """Driver to kick off command-line interface."""
    load_dotenv()

    # Check that we have Raindrop connection token defined and available.
    if not os.getenv("RAINDROP_TOKEN"):
        sys.stderr.print(
            "Sorry, we need an environment variable (RAINDROP_TOKEN) to connect to the Raindrop.io service.\n",
        )
        sys.exit(1)

    # Parse any/all command-line arguments...
    args = _parse_args()

    # Run our event loop!
    if not args.testing:
        EventLoop(args).go(RaindropState.factory())
    else:
        # Run within the VCR decorator provided:
        root = Path(raindropiopy.__file__).parent.parent
        cassette = root / Path("tests/cli/cassettes/test_cli_pexpect.yaml")
        assert cassette.parent.exists()
        print(f"Running in TEST MODE!: {cassette=}")
        with vcr.use_cassette(str(cassette), filter_headers=["Authorization"]):
            EventLoop(args).go(RaindropState.factory())


if __name__ == "__main__":
    main()
