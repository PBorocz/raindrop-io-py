"""Test the only easy method in the Raindrop Tag API."""
import pytest

from raindropiopy.api import CollectionRef, Tag


@pytest.mark.vcr
def test_get_tags(api) -> None:
    """Test that we can get tags currently defined.

    (Note: we can't check on the contents since they're dependent on whose running the test!).
    """
    all_tags = Tag.get(api, CollectionRef.All.id)
    assert all_tags is not None
    assert isinstance(all_tags, list)
    assert (
        len(all_tags) > 0
    ), "Sorry, we expect to have at least *1* tag for this user?!"
