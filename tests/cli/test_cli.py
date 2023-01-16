"""Starting point to test our CLI (nothing much here yet)."""
from io import StringIO

import pytest
import rich
from prompt_toolkit import PromptSession

from raindroppy.cli.cli import CLI
from raindroppy.cli.commands import (
    create,  # ie. the modules themselves
    manage,  # "
    search,  # "
)


@pytest.fixture
def cli():
    """Setup a test fixture of a CLI that captures all interaction internally."""
    return CLI(capture=StringIO())


def tst_setup(cli):
    """Did we get our console setup correctly and our banner out?."""
    assert cli.console and isinstance(cli.console, rich.console.Console)
    console_output = cli.console.file.getvalue()
    assert "Welcome to RaindropPY" in console_output


mock_command_process_method_called = False


def test_event_loop(cli, monkeypatch):
    """Test that event loop returns the right prompt(s)."""

    def mock_session_response_exit(*args, **kwargs):
        return "exit"

    def mock_session_response_quit(*args, **kwargs):
        return "quit"

    def mock_session_response_create(*args, **kwargs):
        return "create"

    def mock_session_response_manage(*args, **kwargs):
        return "manage"

    def mock_session_response_search(*args, **kwargs):
        return "search"

    def mock_session_response_help(*args, **kwargs):
        return "help"

    def mock_command_process_method(cli):
        global mock_command_process_method_called
        mock_command_process_method_called = True

    ################################################################################
    # Test exit conditions
    ################################################################################
    with pytest.raises(KeyboardInterrupt):
        monkeypatch.setattr(PromptSession, "prompt", mock_session_response_exit)
        cli.iteration()

    with pytest.raises(KeyboardInterrupt):
        monkeypatch.setattr(PromptSession, "prompt", mock_session_response_quit)
        cli.iteration()

    ################################################################################
    # Test help
    ################################################################################
    monkeypatch.setattr(PromptSession, "prompt", mock_session_response_help)
    cli.iteration()
    assert "Help is here" in cli.console.file.getvalue()

    ################################################################################
    # Test each of the top level options
    ################################################################################
    for mock_method, process_module in (
        (mock_session_response_manage, manage),
        (mock_session_response_create, create),
        (mock_session_response_search, search),
    ):
        global mock_command_process_method_called
        mock_command_process_method_called = False
        monkeypatch.setattr(PromptSession, "prompt", mock_method)
        monkeypatch.setattr(process_module, "process", mock_command_process_method)
        cli.iteration()
        assert mock_command_process_method_called
