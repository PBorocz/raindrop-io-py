"""Top level project __init__."""
from importlib import metadata


def version():
    """Return the canonical version from pyproject.toml used to package this particular release.

    Our version number only appears in a single, canonical location: pyproject.toml. Thus, we
    supply this utility method to make it visible within code.
    """
    return metadata.version("raindrop_io_py")
