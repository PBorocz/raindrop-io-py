"""Test all the core methods of the Raindrop API."""
import datetime
from pathlib import Path
from unittest.mock import patch

from raindropiopy import API, Raindrop, RaindropType, CollectionRef

raindrop = {
    "_id": 2000,
    # "collection": -1,
    "collection": {"$db": "", "$id": -1, "$ref": "collections"},
    "cover": "",
    "created": "2020-01-01T00:00:00.000Z",
    "creatorRef": 3000,
    "domain": "www.example.com",
    "excerpt": "excerpt text",
    "important": False,
    "lastUpdate": "2020-01-01T01:01:01Z",
    "link": "https://www.example.com/",
    "media": [],
    "pleaseParse": {"weight": 1},
    "sort": 3333333,
    "tags": ["abc", "def"],
    "title": "title",
    "type": "link",
    "user": {"$id": 3000, "$user": "users"},
}


def test_get() -> None:
    """Test get method."""
    api = API("dummy")
    with patch("raindropiopy.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"item": raindrop}

        c = Raindrop.get(api, 2000)

        assert c.id == 2000
        assert c.collection.id == -1
        assert c.cover == ""
        assert c.created == datetime.datetime(
            2020,
            1,
            1,
            0,
            0,
            0,
            tzinfo=datetime.timezone.utc,
        )
        assert c.domain == "www.example.com"
        assert c.excerpt == "excerpt text"
        assert c.last_update == datetime.datetime(
            2020,
            1,
            1,
            1,
            1,
            1,
            tzinfo=datetime.timezone.utc,
        )
        assert c.link == "https://www.example.com/"
        assert c.media == []
        assert c.tags == ["abc", "def"]
        assert c.title == "title"
        assert c.type == RaindropType.link
        assert c.user.id == 3000


def test_search() -> None:
    """Test search method."""
    api = API("dummy")
    with patch("raindropiopy.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"items": [raindrop]}
        found = Raindrop._search_paged(api)
        assert found[0].id == 2000


def test_create_link() -> None:
    """Test ability to create a link-based Raindrop."""
    api = API("dummy")
    with patch("raindropiopy.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"item": raindrop}
        item = Raindrop.create_link(api, link="https://example.com")
        assert item.id == 2000


def test_create_file() -> None:
    """Test ability to create a file-based Raindrop."""
    api = API("dummy")
    content_type = "text/plain"
    with patch("raindropiopy.api.OAuth2Session.request") as m:

        # FIXME: Note that for now, we're *not* testing the ability to
        #        set either a title or tags on the following
        #        file-based create call (even though the capability is
        #        exists).
        Raindrop.create_file(api, Path(__file__), content_type=content_type)

        assert m.call_args[0] == (
            "PUT",
            "https://api.raindrop.io/rest/v1/raindrop/file",
        )
        assert "data" in m.call_args[1]
        assert m.call_args[1]["data"] == {
            "collectionId": str(CollectionRef.Unsorted.id),
        }  # ie. Default is collection isn't specified is Unsorted

        assert "files" in m.call_args[1]
        assert "file" in m.call_args[1]["files"]

        assert type(m.call_args[1]["files"]["file"]) == tuple
        file_ = m.call_args[1]["files"]["file"]
        assert len(file_) == 3

        fn_, fh_, ct_ = file_
        assert fn_ == Path(__file__).name
        assert ct_ == content_type


def test_update() -> None:
    """Test ability to update an existing Raindrop."""
    api = API("dummy")
    with patch("raindropiopy.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"item": raindrop}
        item = Raindrop.update(api, id=2000, link="https://example.com")
        assert item.id == 2000


def test_delete() -> None:
    """Test ability to delete a Raindrop."""
    api = API("dummy")
    with patch("raindropiopy.api.OAuth2Session.request") as m:
        Raindrop.delete(api, id=2000)

        assert m.call_args[0] == (
            "DELETE",
            "https://api.raindrop.io/rest/v1/raindrop/2000",
        )
