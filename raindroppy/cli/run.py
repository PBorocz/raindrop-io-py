#!/usr/bin/env python
"""Startup/entry point for command-line interface.."""
from dotenv import load_dotenv

from raindroppy.cli.cli import CLI
from raindroppy.cli.models import RaindropState

load_dotenv()

if __name__ == "__main__":
    cli = CLI()
    state = RaindropState.factory()
    cli.event_loop(state)
