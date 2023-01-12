from io import StringIO

import pytest
import rich

from raindroppy.cli.cli import CLI


@pytest.fixture
def cli():
    """Setup a test fixture of a CLI that captures all interaction internally"""
    return CLI(capture=StringIO())


@pytest.fixture
def api():
    """Setup a test fixture of a Raindrop API"""
    return ""


def test_setup(cli):
    """Did we get our console setup correctly and our banner out?"""
    assert cli.console and isinstance(cli.console, rich.console.Console)
    console_output = cli.console.file.getvalue()
    assert "Welcome to RaindropPY" in console_output


def test_event_loop(cli, api):
    """To come"""
    ...
