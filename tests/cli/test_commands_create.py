from raindroppy.cli.commands.create import __validate_url


################################################################################
# Test our ability to validate URL's provided, both syntactically and the actual sites
################################################################################
def test_validate_url_validation():
    assert __validate_url("https://www.python.org") is None
    assert __validate_url("asdfasdf://www.python.org") is not None
    assert __validate_url("asdfasdf:/www.python.org") is not None
    assert __validate_url("dsfkl32434jkds89234dsmnewr") is not None
    assert __validate_url("asdf") is not None
