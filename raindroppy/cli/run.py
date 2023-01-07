#!/usr/bin/env python
"""Entry point for primary CLI interaction.."""
# import fire
from cli.models import CLI
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    CLI()
    # fire.Fire(CLI, name="RaindropPY CLI")
