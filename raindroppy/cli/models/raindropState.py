"""Abstract data types to support Raindrop CLI."""
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, TypeVar, Union

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
CreateRequest = TypeVar("CreateRequest")  # "


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
        with Spinner("Refreshing Raindrop Status..."):

            ################################################################################
            # What collections do we currently have on Raindrop?
            # (including the "Unsorted" system collection as well;
            # only an id, title and count)
            ################################################################################

            # Start with the "root" collections at the top level:
            collections: list[Collection] = [
                root for root in Collection.get_roots(self.api) if root.title
            ]

            # Add in the "children" collections at secondary level(s):
            collections.extend([child for child in Collection.get_childrens(self.api)])

            # Finally, add in the "Unsorted" collection
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

            ################################################################################
            # What tags we currently have available on Raindrop across
            # *all* collections? (use set to get rid of potential duplicates)
            ################################################################################
            tags: set[str] = set([tag.tag for tag in Tag.get(self.api)])
            self.tags = list(sorted(tags))
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


@dataclass
class CreateRequest:
    """Encapsulate parameters required to create either a link or file-based Raindrop bookmark."""

    # Bookmark title on Raindrop, eg. "This is a really cool link/doc"
    title: str = None

    # Name of collection (or real) to store bookmark, eg. "My Documents"
    collection: Union[str, Collection] = None

    # Optional list of tags to associate, eg. ["'aTag", "Another Tag"]
    tags: list[str] = None

    # One of the following needs to be specified:
    url: str = None  # URL of link-based Raindrop to create.

    # Absolute path of file to be pushed, eg. /home/me/Documents/foo.pdf
    file_path: Path = None

    def name(self) -> str:
        """Return a user viewable name for request irrespective of type."""
        if self.title:
            return self.title
        if self.url:
            return self.url
        if self.file_path:
            return self.file_path.name
        return "-"

    def print(self, print_method: Callable) -> None:
        """Print the request using the callable provided (used to present back to the user for confirmation)."""
        if self.url:
            print_method(f"URL           : {self.url}")
        elif self.file_path:
            print_method(f'File to send  : "{self.file_path}"')
        print_method(f"With title    : {self.title}")
        print_method(f"To collection : {self.collection}")
        print_method(f"With tags     : {self.tags}")

    @classmethod
    def factory(cls, entry: dict) -> CreateRequest:
        """Return an new instance of CreateRequest based on an inbound dict, ie. from toml."""
        request: CreateRequest = CreateRequest(
            collection=entry.get("collection"),
            tags=entry.get("tags"),
        )

        # Depending on the population of 2 attributes, we conclude
        # what type of Raindrop we're creating, ie. a standard
        # link/url-based one or a "file"-based one.
        if entry.get("file_path"):
            request.file_path = Path(entry.get("file_path"))

            # Get default title from the file name if we don't have a
            # title provided in the inbound dict:
            request.title = entry.get("title", request.file_path.stem)

        elif entry.get("url"):
            request.url = entry.get("url")
            request.title = entry.get("title")

        return request

    def __str__(self):
        """Render a collection as a string (mostly for display)."""
        return_ = list()
        if self.title:
            return_.append(f"Title      : {self.title}")
        if self.url:
            return_.append(f"URL        : {self.url}")
        if self.file_path:
            return_.append(f"File       : {self.file_path}")
        if self.collection:
            return_.append(f"Collection : {self.collection}")
        if self.tags:
            return_.append(f"Tag(s)     : {self.tags}")
        return "\n".join(return_)
