import datetime
from unittest.mock import patch

from raindroppy.api import API, Collection, View

collection = {
    "_id": 1000,
    "access": {"draggable": True, "for": 10000, "level": 4, "root": False},
    "author": True,
    "count": 0,
    "cover": [],
    "created": "2020-01-01T00:00:00Z",
    "creatorRef": {"_id": 10000, "fullName": "user name"},
    "expanded": False,
    "lastUpdate": "2020-01-02T00:00:00Z",
    "parent": {"$db": "", "$id": 100, "$ref": "collections"},
    "public": False,
    "sort": 3000,
    "title": "child",
    "user": {"$db": "", "$id": 10000, "$ref": "users"},
    "view": "list",
}


def test_get_roots() -> None:
    api = API("dummy")
    with patch("raindroppy.api.api.OAuth2Session.request") as m:
        m.get().json.return_value = {"items": [collection]}
        for c in Collection.get_roots(api):
            assert c.id == 1000
            assert c.access.level == AccessLevel.owner
            assert c.access.draggable is True
            assert c.collaborators is None
            assert c.color is None
            assert c.count == 0
            assert c.cover == []
            assert c.created == datetime.datetime(
                2020, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc
            )
            assert c.expanded is False
            assert c.lastUpdate == datetime.datetime(
                2020, 1, 2, 0, 0, 0, tzinfo=datetime.timezone.utc
            )
            assert c.parent
            assert c.parent.id == 100
            assert c.public is False
            assert c.sort == 3000
            assert c.title == "child"
            assert c.user.id == 10000
            assert c.view == View.list


def test_get_childrens() -> None:
    api = API("dummy")
    with patch("raindroppy.api.api.OAuth2Session.request") as m:
        m.get().json.return_value = {"items": [collection]}
        for c in Collection.get_childrens(api):
            assert c.id == 1000


def test_get() -> None:
    api = API("dummy")
    with patch("raindroppy.api.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"item": collection}
        c = Collection.get(api, 1000)
        assert c.id == 1000


def test_update() -> None:
    api = API("dummy")
    with patch("raindroppy.api.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"item": collection}
        title = str(datetime.datetime.now())
        c = Collection.update(api, id=1000, title=title, view=View.list)
        assert c.id == 1000


def test_create() -> None:
    api = API("dummy")
    with patch("raindroppy.api.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"item": collection}
        c = Collection.create(api, title="abcdef")
        assert c.id == 1000


def test_delete() -> None:
    api = API("dummy")
    with patch("raindroppy.api.api.OAuth2Session.request") as m:
        Collection.remove(api, id=1000)
        assert m.call_args[0] == (
            "DELETE",
            "https://api.raindrop.io/rest/v1/collection/1000",
        )
