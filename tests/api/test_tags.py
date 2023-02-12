"""Test the only easy method in the Raindrop Tag API."""
from raindropiopy import CollectionRef, Tag
from tests.api.conftest import vcr


@vcr.use_cassette()
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
