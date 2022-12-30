"""Abstract data types to support Rainddrop CLI."""
from dataclasses import dataclass
from pathlib import Path

from beaupy import console


@dataclass
class RaindropState:
    """Encapsulate all aspects for current state of the Raindrop environment for the specified user."""

    collections: list[str]
    tags: list[str]

    def _print(self):
        """Instead of logging, use console to provide status."""
        console.print(f"{len(self.collections):d} existing collections")
        console.print(f"{len(self.tags):d} existing tags")


@dataclass
class UploadRequest:
    """Encapsulate parameters required to perform an upload and create a file-based bookmark."""

    file_path: Path = None  # Path to file to be uploaded, eg. /home/me/Documents/foo.pdf
    title: str = None  # Bookmark title on Raindrop, eg. "Please Store Me"
    collection: str = None  # Name of collection to store bookmark, eg. "My Uploaded Documents"
    tags: list[str] = None  # Optional list of tags to associate, eg. ["'aTag", "Another Tag"]
