"""Configuration file for the Sphinx documentation builder."""
import os
import sys

# Do this to allow autodoc to actually FIND our raindropiopy package..
sys.path.insert(0, os.path.abspath("."))

project = "Raindrop-IO-py"
copyright = "2023, Peter Borocz"
author = "Peter Borocz"

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
