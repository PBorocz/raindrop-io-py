#!/usr/bin/env python
"""Startup/entry point for command-line interface.."""
from dotenv import load_dotenv

from raindroppy.cli.cli import CLI

load_dotenv()

if __name__ == "__main__":
    CLI()
