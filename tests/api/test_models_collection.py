"""Test all the methods in the Raindrop Collection API."""
import datetime
from unittest.mock import patch, Mock

from raindropiopy import AccessLevel, Collection, SystemCollection, View

COLLECTION = {
    "_id": 1000,
    "access": {"draggable": True, "for": 10000, "level": 4, "root": False},
    "author": True,
    "count": 0,
    "cover": ["https://www.aRandomCover.org"],
    "created": "2020-01-01T00:00:00Z",
    "creatorRef": {"_id": 10000, "full_name": "user name"},
    "expanded": False,
    "last_update": "2020-01-02T00:00:00Z",
    "public": False,
    "sort": 3000,
    "title": "aCollectionTitle",
    "user": {"$db": "", "$id": 10000, "$ref": "users"},
    "view": "list",
    # Note: NO parent attribute here as this is a root level collection.
}

SUB_COLLECTION = {  # Parent is the collection above..
    "_id": 1001,
    "access": {"draggable": True, "for": 10000, "level": 4, "root": False},
    "author": True,
    "count": 0,
    "cover": ["https://www.aRandomCover.org"],
    "created": "2020-01-01T00:00:00Z",
    "creatorRef": {"_id": 10000, "full_name": "user name"},
    "expanded": False,
    "last_update": "2020-01-02T00:00:00Z",
    "public": False,
    "sort": 3000,
    "title": "aSubCollectionTitle",
    "user": {"$db": "", "$id": 10000, "$ref": "users"},
    "view": "list",
    # Difference from above, *this* now is the sub-collection and refers to the parent above!
    "parent": {"$db": "", "$id": 1000, "$ref": "collections"},
}

system_collection = {
    "_id": -1,  # Must be one of [0, -1, -99]
    "count": 5,
}


def test_get_root_collections(mock_api) -> None:
    """Test that we can get the "root" collections."""
    with patch("requests_oauthlib.OAuth2Session.get") as patched_request:
        mock_response = Mock(headers={"X-RateLimit-Limit": "100"})
        mock_response.json.return_value = {"items": [COLLECTION]}
        patched_request.return_value = mock_response

        # Test
        collections = Collection.get_root_collections(mock_api)

        # Confirm
        assert collections
        assert len(collections) == 1
        collection = collections[0]

        assert collection.id == 1000
        assert collection.access.level == AccessLevel.owner
        assert collection.access.draggable is True
        assert collection.collaborators == []
        assert collection.color is None
        assert collection.count == 0
        assert collection.cover == ["https://www.aRandomCover.org"]
        assert collection.created == datetime.datetime(
            2020,
            1,
            1,
            0,
            0,
            0,
            tzinfo=datetime.UTC,
        )
        assert collection.expanded is False
        assert collection.last_update == datetime.datetime(
            2020,
            1,
            2,
            0,
            0,
            0,
            tzinfo=datetime.UTC,
        )
        assert collection.parent is None  # This IS the parent collection, thus, it has no parent itself!
        assert collection.public is False
        assert collection.sort == 3000
        assert collection.title == "aCollectionTitle"
        assert collection.user.id == 10000
        assert collection.view == View.list


def test_get_child_collections(mock_api) -> None:
    """Test that we can get the "children" collections."""
    with patch("requests_oauthlib.OAuth2Session.get") as patched_request:
        mock_response = Mock(headers={"X-RateLimit-Limit": "100"})
        mock_response.json.return_value = {"items": [SUB_COLLECTION]}
        patched_request.return_value = mock_response

        # Test
        collections = Collection.get_child_collections(mock_api)

        # Confirm
        assert collections
        assert len(collections) == 1
        collection = collections[0]

        assert collection.id == 1001
        assert collection.parent == 1000


def test_get(mock_api) -> None:
    """Test that we can get a specific collection."""
    with patch("requests_oauthlib.OAuth2Session.request") as patched_request:
        mock_response = Mock(headers={"X-RateLimit-Limit": "100"})
        mock_response.json.return_value = {"item": COLLECTION}
        patched_request.return_value = mock_response

        # Test
        c = Collection.get(mock_api, 1000)

        # Confirm
        assert c.id == 1000


def test_delete(mock_api) -> None:
    """Test that we can delete an existing collection.

    FIXME: Add test for trying to delete a non-existent collection
    """
    with patch("requests_oauthlib.OAuth2Session.request") as patched_request:
        Collection.delete(mock_api, id=1000)
        assert patched_request.call_args[0] == (
            "DELETE",
            "https://api.raindrop.io/rest/v1/collection/1000",
        )


def test_get_system_collection_status(mock_api) -> None:
    """Test the call to the "get_counts" method."""
    with patch("requests_oauthlib.OAuth2Session.request") as patched_request:
        patched_request.return_value.json.return_value = {"items": [system_collection]}
        assert SystemCollection.get_counts(mock_api)[0].id == -1
        assert SystemCollection.get_counts(mock_api)[0].title == "Unsorted"
        assert SystemCollection.get_counts(mock_api)[0].count == 5


# FIXME: Need to figure out how to mock better, as is, this test is meaningless.
def tst_update(mock_api) -> None:
    """Test that we can update an existing collection.

    FIXME: Add test for trying to update non-existent collection
    """
    with patch("requests_oauthlib.OAuth2Session.request") as patched_request:
        mock_response = Mock(headers={"X-RateLimit-Limit": "100"})
        mock_response.json.return_value = {"item": COLLECTION}
        patched_request.return_value = mock_response

        # Test
        title = str(datetime.datetime.now())
        c = Collection.update(mock_api, id=1000, title=title, view=View.list)

        # Confirm
        assert c.id == 1000
        assert c.title == title


# FIXME: Need to figure out how to mock better, as is, this test is meaningless.
def tst_create(mock_api) -> None:
    """Test that we can create a new collection.

    FIXME: Add test for trying to create a collection that's already there.
    """
    with patch("requests_oauthlib.OAuth2Session.request") as patched_request:
        mock_response = Mock(headers={"X-RateLimit-Limit": "100"})
        mock_response.json.return_value = {"item": COLLECTION}
        patched_request.return_value = mock_response

        # Test
        c = Collection.create(mock_api, title="abcdef")

        # Confirm
        assert c.id == 1000
