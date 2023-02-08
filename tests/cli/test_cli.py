"""Starting point to test our CLI (nothing much here yet)."""
from io import StringIO

import pytest
import rich
from prompt_toolkit import PromptSession

from raindropiopy.cli.commands import (
    create,  # ie. the modules themselves
    manage,  # "
    search,  # "
)
from raindropiopy.cli.models.eventLoop import EventLoop


@pytest.fixture
def el():
    """Set a test fixture of a EventLoop that captures all interaction internally."""
    return EventLoop(capture=StringIO())


def tst_setup(el):
    """Did we get our console setup correctly and our banner out?."""
    assert el.console and isinstance(el.console, rich.console.Console)
    console_output = el.console.file.getvalue()
    assert "Welcome to Raindropiopy" in console_output


mock_command_process_method_called = False


def test_event_loop(el, monkeypatch):
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

    def mock_command_process_method(el):
        global mock_command_process_method_called
        mock_command_process_method_called = True

    ################################################################################
    # Test exit conditions
    ################################################################################
    with pytest.raises(KeyboardInterrupt):
        monkeypatch.setattr(PromptSession, "prompt", mock_session_response_exit)
        el.iteration()

    with pytest.raises(KeyboardInterrupt):
        monkeypatch.setattr(PromptSession, "prompt", mock_session_response_quit)
        el.iteration()

    ################################################################################
    # Test help
    ################################################################################
    monkeypatch.setattr(PromptSession, "prompt", mock_session_response_help)
    el.iteration()
    assert "Help is here" in el.console.file.getvalue()

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
        el.iteration()
        assert mock_command_process_method_called
