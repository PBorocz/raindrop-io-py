
# The list of available targets
default:
    @just --list

################################################################################
# Usage
################################################################################
cli *args:
    python raindroppy/cli/cli.py {{args}}

################################################################################
# Development support...
################################################################################
# Run local unit tests (fast, no connection or Raindrop.io configuration required)
test:
    python -m pytest

# Run samples against live Raindrop environment (assumes RAINDROP_TOKEN in env!)
examples:
    # Listed in order of complexity, list_* are read-only, rest make changes.
    python examples/list_authorised_user.py
    python examples/list_collections.py
    python examples/list_tags.py
    python examples/create_collection.py
    python examples/edit_collection.py
    python examples/create_raindrop_file.py
    python examples/create_raindrop_link.py
    python examples/edit_raindrop.py
    python examples/search_raindrop.py

# Run our pre-commit checks manually
pre-commit *args:
    pre-commit run --all-files {{args}}
