"""Top level project/package init."""
from importlib import metadata


def version():
    """Return the canonical version from pyproject.toml used to package this particular release."""
    return metadata.version("raindrop_io_py")
