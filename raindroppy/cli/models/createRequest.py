"""Abstract data types to support Raindrop CLI."""
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, TypeVar, Union

from raindroppy.api import Collection

CreateRequest = TypeVar(
    "CreateRequest",
)  # In py3.11, we'll be able to do 'from typing import Self' instead


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
