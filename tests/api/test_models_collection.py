"""Test all the methods in the Raindrop Collection API."""
import datetime
from unittest.mock import patch

from raindropiopy import API, AccessLevel, Collection, SystemCollection, View

collection = {
    "_id": 1000,
    "access": {"draggable": True, "for": 10000, "level": 4, "root": False},
    "author": True,
    "count": 0,
    "cover": ["https://www.aRandomCover.org"],
    "created": "2020-01-01T00:00:00Z",
    "creatorRef": {"_id": 10000, "fullName": "user name"},
    "expanded": False,
    "lastUpdate": "2020-01-02T00:00:00Z",
    "parent": 100,  # {"$db": "", "$id": 100, "$ref": "collections"},
    "public": False,
    "sort": 3000,
    "title": "child",
    "user": {"$db": "", "$id": 10000, "$ref": "users"},
    "view": "list",
}

system_collection = {
    "_id": -1,  # Must be one of [0, -1, -99]
    "count": 5,
}


def test_get_root_collections() -> None:
    """Test that we can get the "root" collections."""
    api = API("dummy")
    with patch("raindropiopy.api.OAuth2Session.request") as m:
        m.get().json.return_value = {"items": [collection]}
        for c in Collection.get_root_collections(api):
            assert c.id == 1000
            assert c.access.level == AccessLevel.owner
            assert c.access.draggable is True
            assert c.collaborators is None
            assert c.color is None
            assert c.count == 0
            assert c.cover == ["https://www.aRandomCover.org"]
            assert c.created == datetime.datetime(
                2020,
                1,
                1,
                0,
                0,
                0,
                tzinfo=datetime.timezone.utc,
            )
            assert c.expanded is False
            assert c.lastUpdate == datetime.datetime(
                2020,
                1,
                2,
                0,
                0,
                0,
                tzinfo=datetime.timezone.utc,
            )
            assert c.parent
            assert c.parent.id == 100
            assert c.public is False
            assert c.sort == 3000
            assert c.title == "child"
            assert c.user.id == 10000
            assert c.view == View.list


def test_get_child_collections() -> None:
    """Test that we can get the "children" collections."""
    api = API("dummy")
    with patch("raindropiopy.api.OAuth2Session.request") as m:
        m.get().json.return_value = {"items": [collection]}
        for c in Collection.get_child_collections(api):
            assert c.id == 1000


def test_get() -> None:
    """Test that we can get a specific collection."""
    api = API("dummy")
    with patch("raindropiopy.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"item": collection}
        c = Collection.get(api, 1000)
        assert c.id == 1000


def test_update() -> None:
    """Test that we can update an existing collection.

    FIXME: Add test for trying to update non-existent collection
    """
    api = API("dummy")
    with patch("raindropiopy.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"item": collection}
        title = str(datetime.datetime.now())
        c = Collection.update(api, id=1000, title=title, view=View.list)
        assert c.id == 1000


def test_create() -> None:
    """Test that we can create a new collection.

    FIXME: Add test for trying to create a collection that's already there.
    """
    api = API("dummy")
    with patch("raindropiopy.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"item": collection}
        c = Collection.create(api, title="abcdef")
        assert c.id == 1000


def test_delete() -> None:
    """Test that we can delete an existing collection.

    FIXME: Add test for trying to delete a non-existent collection
    """
    api = API("dummy")
    with patch("raindropiopy.api.OAuth2Session.request") as m:
        Collection.delete(api, id=1000)
        assert m.call_args[0] == (
            "DELETE",
            "https://api.raindrop.io/rest/v1/collection/1000",
        )


def test_get_system_collection_status() -> None:
    """Test the call to the "get_status" method."""
    api = API("dummy")
    with patch("raindropiopy.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"items": [system_collection]}
        assert SystemCollection.get_status(api)[0].id == -1
        assert SystemCollection.get_status(api)[0].title == "Unsorted"
        assert SystemCollection.get_status(api)[0].count == 5
