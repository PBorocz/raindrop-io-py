"""Configuration file for the Sphinx documentation builder."""
import os
import sys

# Do this to allow autodoc to actually FIND our raindropiopy package..
sys.path.insert(0, os.path.abspath("."))

project = "Raindrop-IO-py"
copyright = "2023, Peter Borocz"
author = "Peter Borocz"
# version = release = PACKAGE_VERSION = metadata.version("raindrop_io_py")

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autodoc.typehints",
    "sphinx.ext.napoleon",
]

napoleon_google_docstring = True
napoleon_use_param = False
napoleon_use_ivar = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

if os.environ.get("READTHEDOCS") == "True":
    from pathlib import Path

    PROJECT_ROOT = Path(__file__).parent.parent
    PACKAGE_ROOT = PROJECT_ROOT / "raindropiopy"

    def run_apidoc(_):
        """Run the Sphinx AutoDoc to actually *parse* our code."""
        from sphinx.ext import apidoc

        apidoc.main(
            [
                "--force",
                "--implicit-namespaces",
                "--module-first",
                "--separate",
                "--output-dir",
                str(PROJECT_ROOT / "docs"),
                str(PROJECT_ROOT),
            ],
        )

    def setup(app):
        """Plug-into the RtD's build process with our method."""
        app.connect("builder-inited", run_apidoc)
