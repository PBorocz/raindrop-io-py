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

        def _cf(casefold: bool, string: str) -> str:
            if casefold:
                return string.casefold()
            return string

        with Spinner("Refreshing Raindrop Status..."):

            # What collections do we currently have on Raindrop?
            # (including the "Unsorted" system collection as well;
            # only an id, title and count)
            collections: list[Collection] = [
                root for root in Collection.get_roots(self.api) if root.title
            ]

            collections.extend([child for child in Collection.get_childrens(self.api)])
            for collection in SystemCollection.get_status(self.api):
                if collection.id == CollectionRef.Unsorted.id:
                    access = Access({"level": 4})
                    unsorted = Collection(
                        {
                            "_id": CollectionRef.Unsorted.id,
                            "count": collection.count,
                            "title": SystemCollection.CollectionRefsTitles[
                                CollectionRef.Unsorted.id
                            ],
                            "access": access,
                        },
                    )
                    collections.append(unsorted)

            self.collections = sorted(
                collections,
                key=lambda collection: getattr(collection, "title", ""),
            )

            # What tags we currently have available on Raindrop across
            # *all* collections? (use set to get rid of potential duplicates)
            tags: set[str] = set([tag.tag for tag in Tag.get(self.api)])
            self.tags = list(sorted(tags))
            self.refreshed = datetime.utcnow()

        return True

    @classmethod
    def factory(cls, verbose: bool = True) -> RaindropState:
        """Factory to log into Raindrop and return a new RaindropState instance."""
        with Spinner("Logging into Raindrop..."):

            # Setup our connection to Raindrop
            api: API = API(os.environ["RAINDROP_TOKEN"])

            # What user are we currently defined "for"?
            user = User.get(api)

        state = RaindropState(api=api, user=user, created=datetime.utcnow())

        # And, do our first refresh.
        state.refresh()

        return state


@dataclass
class CreateRequest:
    """Encapsulate parameters required to create either a link or file-based Raindrop bookmark."""

    title: str = (
        None  # Bookmark title on Raindrop, eg. "This is a really cool link/doc"
    )
    collection: Union[
        str,
        Collection,
    ] = None  # Name of collection (or real) to store bookmark, eg. "My Documents"
    tags: list[
        str
    ] = None  # Optional list of tags to associate, eg. ["'aTag", "Another Tag"]

    # One of the following needs to be specified:
    url: str = None  # URL of link-based Raindrop to create.
    file_path: Path = (
        None  # Absolute path of file to be pushed, eg. /home/me/Documents/foo.pdf
    )

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
        """Print the request (using the callable), used to present back to the user for confirmation."""
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
