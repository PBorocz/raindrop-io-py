
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
# Run samples against live Raindrop environment (assumes RAINDROP_TOKEN in env!)
samples:
    # Listed in order of complexity, list_* are read-only, rest make changes.
    python samples/list_authorised_user.py
    python samples/list_collections.py
    python samples/list_tags.py
    python samples/create_collection.py
    python samples/edit_collection.py
    python samples/create_raindrop_file.py
    python samples/create_raindrop_link.py
    python samples/edit_raindrop.py
    python samples/search_raindrop.py

# Test
test:
    python -m pytest

# Run our pre-commit checks manually
pre-commit *args:
    pre-commit run --all-files {{args}}
