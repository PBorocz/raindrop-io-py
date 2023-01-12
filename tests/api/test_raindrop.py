import datetime
from pathlib import Path
from unittest.mock import patch

from raindroppy.api import API, Raindrop, RaindropType

raindrop = {
    "_id": 2000,
    "collection": {"$db": "", "$id": -1, "$ref": "collections"},
    "collectionId": -1,
    "cover": "",
    "created": "2020-01-01T00:00:00.000Z",
    "creatorRef": {"_id": 3000, "fullName": "user name"},
    "domain": "www.example.com",
    "excerpt": "excerpt text",
    "lastUpdate": "2020-01-01T01:01:01Z",
    "link": "https://www.example.com/",
    "media": [],
    "pleaseParse": {"weight": 1},
    "removed": False,
    "sort": 3333333,
    "tags": ["abc", "def"],
    "title": "title",
    "type": "link",
    "user": {"$id": 3000, "$ref": "users"},
}


def test_get() -> None:
    api = API("dummy")
    with patch("raindroppy.api.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"item": raindrop}

        c = Raindrop.get(api, 2000)

        assert c.id == 2000
        assert c.collection.id == -1
        assert c.cover == ""
        assert c.created == datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
        assert c.domain == "www.example.com"
        assert c.excerpt == "excerpt text"
        assert c.lastUpdate == datetime.datetime(2020, 1, 1, 1, 1, 1, tzinfo=datetime.timezone.utc)
        assert c.link == "https://www.example.com/"
        assert c.media == []
        assert c.tags == ["abc", "def"]
        assert c.title == "title"
        assert c.type == RaindropType.link
        assert c.user.id == 3000


def test_search() -> None:
    api = API("dummy")
    with patch("raindroppy.api.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"items": [raindrop]}

        found = Raindrop.search(api)
        assert found[0].id == 2000


def test_create_link() -> None:
    api = API("dummy")
    with patch("raindroppy.api.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"item": raindrop}
        item = Raindrop.create_link(api, link="https://example.com")
        assert item.id == 2000


def test_create_file() -> None:
    api = API("dummy")
    content_type = "text/plain"
    with patch("raindroppy.api.api.OAuth2Session.request") as m:

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
        assert m.call_args[1]["data"] == {"collectionId": "-1"}  # ie. Unsorted collection

        assert "files" in m.call_args[1]
        assert "file" in m.call_args[1]["files"]

        assert type(m.call_args[1]["files"]["file"]) == tuple
        file_ = m.call_args[1]["files"]["file"]
        assert len(file_) == 3

        fn_, fh_, ct_ = file_
        assert fn_ == Path(__file__).name
        assert ct_ == content_type


def test_update() -> None:
    api = API("dummy")
    with patch("raindroppy.api.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"item": raindrop}
        item = Raindrop.update(api, id=2000, link="https://example.com")
        assert item.id == 2000


def test_remove() -> None:
    api = API("dummy")
    with patch("raindroppy.api.api.OAuth2Session.request") as m:
        Raindrop.remove(api, id=2000)

        assert m.call_args[0] == (
            "DELETE",
            "https://api.raindrop.io/rest/v1/raindrop/2000",
        )
