"""Test that we can get the currently logged in user (ie. the one associated with the current TOKEN)."""
import pytest

from raindropiopy.api import User


@pytest.mark.vcr
def test_get_user(api) -> None:
    """Test that we can information on the current user.

    (Note: we can't check on the contents since they're dependent on whose running the test!).
    """
    user = User.get(api)
    assert user is not None
    assert isinstance(user, User)
    for attr in ["id", "email", "fullName", "password", "pro", "registered"]:
        assert (
            getattr(user, attr) is not None
        ), f"We expected required attribute '{attr}' to be populated for the current user!"
