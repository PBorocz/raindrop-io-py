
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
run_examples:
    # Listed in order of complexity, list_* are read-only, rest make changes.
    # Be nice to Raindrop and rest in between each one.
    python examples/list_authorised_user.py
    sleep 1
    python examples/list_collections.py
    sleep 1
    python examples/list_tags.py
    sleep 1
    python examples/create_collection.py
    sleep 1
    python examples/edit_collection.py
    sleep 1
    python examples/create_raindrop_file.py
    sleep 1
    python examples/create_raindrop_link.py
    sleep 1
    python examples/edit_raindrop.py
    sleep 1
    python examples/search_raindrop.py

# Run our pre-commit checks manually
pre-commit *args:
    pre-commit run --all-files {{args}}
