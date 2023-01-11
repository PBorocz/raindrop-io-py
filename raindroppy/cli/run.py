#!/usr/bin/env python
"""Startup/entry point for command-line interface.."""
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

from cli._cli import CLI

load_dotenv()

if __name__ == "__main__":
    CLI()
