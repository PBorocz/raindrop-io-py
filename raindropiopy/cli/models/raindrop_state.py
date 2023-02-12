"""Abstract data types to support Raindrop CLI."""
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, TypeVar

from rich import print

from raindropiopy import (
    API,
    Collection,
    CollectionRef,
    SystemCollection,
    Tag,
    User,
)
from raindropiopy.cli.models.spinner import Spinner

RaindropState = TypeVar(
    "RaindropState",
)  # In py3.11, we'll be able to do 'from typing import Self' instead


@dataclass
class RaindropState:
    """Encapsulate all aspects for current state of the Raindrop environment."""

    api: API
    user: User
    created: datetime = datetime.utcnow()
    collections: list[Collection] = None
    tags: list[str] = None
    refreshed: datetime = None

    def get_collection_titles(
        self,
        exclude_unsorted=False,
        casefold=False,
    ) -> list[str]:
        """Return a sorted list of Collection titles, with or without 'Unsorted' and either casefolded or not."""
        if exclude_unsorted:
            titles = [
                collection.title
                for collection in self.collections
                if collection.id > 0 and collection.title
            ]
        else:
            titles = [
                collection.title for collection in self.collections if collection.title
            ]

        if casefold:
            titles = [title.casefold() for title in titles if title]

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

    def refresh(self) -> bool:
        """Refresh the current state of this Raindrop environment (ie. current collections and tags available)."""

        def __refresh_collections():
            """Gather and set the *COLLECTIONS* associated with the current API user."""
            # This get's us both "root" and "children" collections:
            collections: list[Collection] = Collection.get_collections(self.api)

            # Add the "Unsorted" system collection (we don't care about "Trash" or "All" here)
            for collection in SystemCollection.get_status(self.api):
                if collection.id == CollectionRef.Unsorted.id:
                    unsorted_collection = Collection(
                        _id=collection.id,
                        count=collection.count,
                        title=collection.title,
                        user=self.user,
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
    def factory(cls) -> RaindropState:
        """Log into Raindrop and return a new, refreshed RaindropState instance."""
        with Spinner("Logging into Raindrop..."):
            api: API = API(
                os.environ["RAINDROP_TOKEN"],
            )  # Setup our connection to Raindrop
            try:
                user = User.get(api)  # What user are we currently defined "for"?
            except Exception:
                print(
                    "[red]Sorry, unable to get query Raindrop.IO for the user requested!",
                )
                sys.exit(1)
        state = RaindropState(api=api, user=user)
        state.refresh()
        return state
