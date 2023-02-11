"""Configuration file for the Sphinx documentation builder."""
import os
import sys

# Do this to allow autodoc to actually FIND our raindropiopy package..
sys.path.insert(0, os.path.abspath("."))

project = "Raindrop-IO-py"
copyright = "2023, Peter Borocz"
author = "Peter Borocz"

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon"]

napoleon_google_docstring = False
napoleon_use_param = False
napoleon_use_ivar = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# html_theme = "sphinx_rtd_theme"
html_theme = "default"
html_static_path = ["_static"]


# List of zero or more Sphinx-specific warning categories to be squelched (i.e.,
# suppressed, ignored).
# https://github.com/sphinx-doc/sphinx/issues/4961#issuecomment-1269463169
suppress_warnings = [
    # FIXME: *THIS IS TERRIBLE.* Generally speaking, we do want Sphinx to inform
    # us about cross-referencing failures. Remove this hack entirely after Sphinx
    # resolves this open issue:
    #    https://github.com/sphinx-doc/sphinx/issues/4961
    # Squelch mostly ignorable warnings resembling:
    #     WARNING: more than one target found for cross-reference 'TypeHint':
    #     beartype.door._doorcls.TypeHint, beartype.door.TypeHint
    #
    # Sphinx currently emits *HUNDREDS* of these warnings against our
    # documentation. All of these warnings appear to be ignorable. Although we
    # could explicitly squelch *SOME* of these warnings by canonicalizing
    # relative to absolute references in docstrings, Sphinx emits still others
    # of these warnings when parsing PEP-compliant type hints via static
    # analysis. Since those hints are actual hints that *CANNOT* by definition
    # by canonicalized, our only recourse is to squelch warnings altogether.
    "ref.python",
]
