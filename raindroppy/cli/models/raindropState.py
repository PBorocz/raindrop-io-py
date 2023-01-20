"""Abstract data types to support Raindrop CLI."""
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TypeVar

from raindroppy.api import (
    API,
    Access,
    Collection,
    CollectionRef,
    SystemCollection,
    Tag,
    User,
)
from raindroppy.cli.models.spinner import Spinner

RaindropState = TypeVar(
    "RaindropState",
)  # In py3.11, we'll be able to do 'from typing import Self' instead


@dataclass
class RaindropState:
    """Encapsulate all aspects for current state of the Raindrop environment."""

    api: API
    created: datetime
    user: User
    collections: list[Collection] = None
    tags: list[str] = None
    refreshed: datetime = None

    def get_collection_titles(self, exclude_unsorted=False) -> list[str]:
        """Return a sorted list of Collection titles, with or without 'Unsorted'."""
        if exclude_unsorted:
            titles = [
                collection.title for collection in self.collections if collection.id > 0
            ]
        else:
            titles = [collection.title for collection in self.collections]
        return sorted(titles)

    def find_collection(self, title: str) -> Optional[Collection]:
        """Find the actual Collection object with the title provided."""
        for collection in self.collections:
            if title.casefold() == collection.title.casefold():
                return collection
        return None

    def find_collection_by_id(self, id: int) -> Optional[Collection]:
        """Find the actual Collection object with the *id* provided."""
        for collection in self.collections:
            if collection.id == id:
                return collection
        return None

    def refresh(self, verbose: bool = True) -> bool:
        """Refresh the current state of this Raindrop environment (ie. current collections and tags available)."""

        def __refresh_collections():
            """Gather and set the *COLLECTIONS* associated with the current API user."""
            # This get's us both "root" and "children" collections:
            collections: list[Collection] = Collection.get_collections(self.api)

            # Add the "Unsorted" system collection (we don't care about "Trash" or "All" here)
            for collection in SystemCollection.get_status(self.api):
                if collection.id == CollectionRef.Unsorted.id:
                    unsorted_collection = Collection(
                        {
                            "_id": CollectionRef.Unsorted.id,
                            "count": collection.count,
                            "title": SystemCollection.CollectionRefsTitles[
                                CollectionRef.Unsorted.id
                            ],
                            "access": Access({"level": 4}),
                        },
                    )
                    collections.append(unsorted_collection)

            # Leave our collections in a presentable order, ie. by Title.
            self.collections = sorted(
                collections,
                key=lambda collection: getattr(collection, "title", ""),
            )

        def __refresh_tags():
            """Gather and set the *TAGS* associated with the current API user."""
            # use set to get rid of potential duplicates
            tags: set[str] = set([tag.tag for tag in Tag.get(self.api)])
            self.tags = list(sorted(tags))

        ################################################################################
        with Spinner("Refreshing Raindrop Status..."):
            __refresh_collections()
            __refresh_tags()
            self.refreshed = datetime.utcnow()

        return True

    @classmethod
    def factory(cls, verbose: bool = True) -> RaindropState:
        """Log into Raindrop and return a new, refreshed RaindropState instance."""
        with Spinner("Logging into Raindrop..."):
            api: API = API(
                os.environ["RAINDROP_TOKEN"],
            )  # Setup our connection to Raindrop
            user = User.get(api)  # What user are we currently defined "for"?
        state = RaindropState(api=api, user=user, created=datetime.utcnow())
        state.refresh()
        return state
