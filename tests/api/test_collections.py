"""Test all the methods in the Raindrop Collection API."""
import pytest
from getpass import getuser

import requests

from raindropiopy.api import Collection, CollectionRef, SystemCollection
from tests.api.conftest import vcr


@vcr.use_cassette()
def test_get_collections(api) -> None:
    """Test that we can get collections currently defined using all 3 methods in api/models.py.

    (Note: we can't check on the contents since they're dependent on whose running the test!).
    """
    count_roots = 0
    for collection in Collection.get_roots(api):
        assert collection.id
        assert collection.title
        count_roots += 1

    count_children = 0
    for collection in Collection.get_childrens(api):
        assert collection.id
        assert collection.title
        count_children += 1

    assert count_roots + count_children == len(Collection.get_collections(api))


@vcr.use_cassette()
def test_system_collections(api) -> None:
    """Test that we can information on the "system" collections."""
    system = SystemCollection.get_status(api)
    assert system
    assert isinstance(system, list)
    assert 3 == len(system), "Sorry, we expect to always have *3* system collections!"

    for collection in system:
        assert (
            collection.title
        )  # models.py adds titles for us, make sure they come through
        if collection.id == CollectionRef.All.id:
            assert collection.title == "All"
        if collection.id == CollectionRef.Trash.id:
            assert collection.title == "Trash"
        if collection.id == CollectionRef.Unsorted.id:
            assert collection.title == "Unsorted"


@vcr.use_cassette()
def test_collection_lifecycle(api) -> None:
    """Test that we can roundtrip a collection, ie. create, update, get and delete."""
    title = f"TEST Collection ({getuser()}"

    # Step 1: Create!
    collection = Collection.create(api, title=title)
    assert collection
    assert collection.id
    assert collection.title == title

    # Step 2: Edit...

    title = title.replace("TEST Collection", "EDITED TEST Collection")
    Collection.update(api, id=collection.id, title=title)
    collection = Collection.get(api, collection.id)
    assert collection.title == title

    # Step 3: Delete...
    Collection.remove(api, id=collection.id)
    with pytest.raises(requests.exceptions.HTTPError):
        Collection.get(api, collection.id)
