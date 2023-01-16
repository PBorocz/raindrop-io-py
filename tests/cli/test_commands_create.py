"""Test a few commands in the create command module."""

from raindroppy.cli.commands.create import __validate_url


def test_validate_url_validation():
    """Test our ability to validate URL's provided, both syntactically and the actual sites."""
    assert __validate_url("https://www.python.org") is None
    assert __validate_url("asdfasdf://www.python.org") is not None
    assert __validate_url("asdfasdf:/www.python.org") is not None
    assert __validate_url("dsfkl32434jkds89234dsmnewr") is not None
    assert __validate_url("asdf") is not None
