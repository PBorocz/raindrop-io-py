"""Test all the core methods of the Raindrop API."""
from pathlib import Path

import pytest
import requests

from raindropiopy.api import Raindrop, RaindropType


@pytest.fixture
def sample_raindrop_link():
    """Fixture to return sample raindrop data."""
    return (
        "https://www.google.com/",
        {
            "excerpt": "excerpt/description text",
            "important": True,
            "tags": ["abc", "def"],
            "title": "a Title",
        },
    )


@pytest.fixture
def sample_raindrop_file():
    """Fixture to return sample raindrop data."""
    return (
        "https://www.google.com/",
        {
            "excerpt": "excerpt/description text",
            "important": True,
            "tags": ["abc", "def"],
            "title": "a Title",
        },
    )


@pytest.fixture
def search_raindrops(api):
    """Fixture to setup and teardown 2 link-based raindrops for search testing."""
    link, args = (
        "https://www.google.com/",
        {"title": "ELGOOG 1234567890", "tags": ["ABCDEFG", "HIJKLMO"]},
    )
    raindrop_google = Raindrop.create_link(api, link, **args)

    link, args = (
        "https://www.python.com/",
        {"title": "NOHYYP 1234567890", "tags": ["HIJKLMO", "PQRSTUV"]},
    )
    raindrop_python = Raindrop.create_link(api, link, **args)

    # Before we let the test rip, allow time for asynchronuous indexing on Raindrop's backend to catch-up.
    # time.sleep(5)
    yield

    Raindrop.remove(api, id=raindrop_google.id)
    Raindrop.remove(api, id=raindrop_python.id)


@pytest.mark.vcr
def test_lifecycle_raindrop_link(api, sample_raindrop_link) -> None:
    """Test that we can roundtrip a regular/link-based raindrop, ie. create, update, get and delete."""
    # TEST: Create
    link, args = sample_raindrop_link
    raindrop = Raindrop.create_link(api, link, **args)
    assert raindrop is not None
    assert isinstance(raindrop, Raindrop)
    assert raindrop.id
    assert raindrop.link == link
    assert raindrop.important == args.get("important")
    assert raindrop.tags == args.get("tags")
    assert raindrop.title == args.get("title")
    assert raindrop.excerpt == args.get("excerpt")
    assert raindrop.type == RaindropType.link

    # TEST: Edit...
    title = "a NEW/EDITED Title"
    edited_raindrop = Raindrop.update(api, raindrop.id, title=title)
    assert edited_raindrop.title == title

    # TEST: Delete...
    Raindrop.remove(api, id=raindrop.id)
    with pytest.raises(requests.exceptions.HTTPError):
        Raindrop.get(api, raindrop.id)


@pytest.mark.vcr
def test_lifecycle_raindrop_file(api) -> None:
    """Test that we can roundtrip a *file-base* raindrop, ie. create, update, get and delete."""
    # TEST: Create a link using this test file as the file to upload.
    path_ = Path(__file__).parent / Path("test_raindrop.pdf")

    raindrop = Raindrop.create_file(
        api,
        path_,
        "application/pdf",
        title="A Sample Title",
        tags=["SampleTag"],
    )
    assert raindrop is not None
    assert isinstance(raindrop, Raindrop)
    assert raindrop.id
    assert raindrop.file.name == path_.name
    assert raindrop.type == RaindropType.document

    # TEST: Delete...
    Raindrop.remove(api, id=raindrop.id)
    with pytest.raises(requests.exceptions.HTTPError):
        Raindrop.get(api, raindrop.id)


@pytest.mark.vcr
def test_search(api, search_raindrops) -> None:
    """Test that we can *search* raindrops."""

    def _print(results):
        links = [drop.link for drop in results]
        return ",".join(links)

    # TEST: Can we search by "word"?
    results = Raindrop.search(api, word="ELGOOG")  # Title
    assert (
        len(results) == 1
    ), f"Sorry, expected 1 for 'ELGOOG' but got the following {_print(results)}"

    results = Raindrop.search(api, word="1234567890")
    assert (
        len(results) == 2
    ), f"Sorry, expected 2 for '1234567890' but got the following {_print(results)}"

    # TEST: Can we search by "tag"?
    results = Raindrop.search(api, tag="ABCDEFG")
    assert (
        len(results) == 1
    ), f"Sorry, expected 1 for tag 'ABCDEFG' but got the following {_print(results)}"

    results = Raindrop.search(api, tag="HIJKLMO")
    assert (
        len(results) == 2
    ), f"Sorry, expected 2 for tag 'HIJKLMO' but got the following {_print(results)}"
