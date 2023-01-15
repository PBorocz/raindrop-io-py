"""Startup/entry point for command-line interface.."""
from dotenv import load_dotenv

from raindroppy.cli.cli import CLI
from raindroppy.cli.models import RaindropState

if __name__ == "__main__":
    load_dotenv()
    CLI().event_loop(RaindropState.factory())
