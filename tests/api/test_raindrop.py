"""Test all the core methods of the Raindrop API."""
import pytest
import requests

from raindropiopy.api import Raindrop, RaindropType


@pytest.fixture
def sample_raindrop():
    """Fixture to return sample raindrop data."""
    return {
        "cover": "",
        "excerpt": "excerpt/description text",
        "important": True,
        "link": "https://www.google.com/",
        "media": [],
        "tags": ["abc", "def"],
        "title": "a Title",
        "type": "link",
    }


@pytest.mark.vcr
def test_lifecycle_raindrop_link(api, sample_raindrop) -> None:
    """Test that we can roundtrip a raindrop, ie. create, update, get and delete."""
    # Step 1: Create!
    args = {attr: value for attr, value in sample_raindrop.items() if attr != "link"}

    raindrop = Raindrop.create_link(api, sample_raindrop.get("link"), **args)
    assert raindrop is not None
    assert isinstance(raindrop, Raindrop)
    assert raindrop.id
    assert raindrop.important == sample_raindrop.get("important")
    assert raindrop.link == sample_raindrop.get("link")
    assert raindrop.media == sample_raindrop.get("media")
    assert raindrop.tags == sample_raindrop.get("tags")
    assert raindrop.title == sample_raindrop.get("title")
    assert raindrop.type == RaindropType.link

    # Step 2: Edit...
    title = "a NEW/EDITED Title"
    edited_raindrop = Raindrop.update(api, raindrop.id, title=title)
    assert edited_raindrop.title == title

    # # Step 3: Delete...
    Raindrop.remove(api, id=raindrop.id)
    with pytest.raises(requests.exceptions.HTTPError):
        Raindrop.get(api, raindrop.id)
