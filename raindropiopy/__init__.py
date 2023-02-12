"""Top level project __init__."""
from importlib import metadata

__all__ = (
    "API",
    "Access",
    "AccessLevel",
    "BrokenLevel",
    "Collection",
    "CollectionRef",
    "FontColor",
    "Group",
    "Raindrop",
    "RaindropSort",
    "RaindropType",
    "SystemCollection",
    "Tag",
    "User",
    "UserConfig",
    "UserFiles",
    "UserRef",
    "View",
    "version",
)

from .api import API
from .models import (
    Access,
    AccessLevel,
    BrokenLevel,
    Collection,
    CollectionRef,
    FontColor,
    Group,
    Raindrop,
    RaindropSort,
    RaindropType,
    SystemCollection,
    Tag,
    User,
    UserConfig,
    UserFiles,
    UserRef,
    View,
)


def version():
    """Return the canonical version from pyproject.toml used to package this particular release.

    Our version number only appears in a single, canonical location: pyproject.toml. Thus, we
    supply this utility method to make it visible within code.
    """
    return metadata.version("raindrop_io_py")
