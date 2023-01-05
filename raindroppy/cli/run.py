#!/usr/bin/env python
"""Entry point for primary CLI interaction.."""

import fire

# Define our project root for imports
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from cli.models import CLI
from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":

    # from beaupy import DefaultKeys as dk
    # from yakh import get_key
    # from yakh.key import Keys

    # key = ''
    # while key not in ['q', Keys.ENTER]:
    #     key = get_key()
    #     # if key.is_printable:
    #     print(key.key_codes)

    fire.Fire(CLI, name="RaindropPY CLI")
