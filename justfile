set dotenv-load

# The list of available targets
default:
    @just --list

################################################################################
# Packaging...
################################################################################
# Clean our build enviroment
clean:
    @rm -rf build raindroppy.egg-info

# Build our package
build:
    @echo "Building..."
    @just clean
    @poetry build

# Build and Publish
publish *args:
    echo "Publishing..."
    poetry publish --build --username $PYPI_USERNAME --password $PYPI_PASSWORD {{args}}

################################################################################
# Development...
################################################################################
# Run our command-line interface
cli:
    python raindroppy/cli/cli.py

# Run tests
test *args:
    python -m pytest {{args}}

# Pre-commit - Run all
pre-commit-all *args:
    pre-commit run --all-files {{args}}

# Pre-commit - Update new configuration and run
pre-commit-update *args:
    pre-commit install
    git add .pre-commit-config.yaml
    just pre-commit-all {{args}}

sleep:
    @echo "Waiting..."
    @sleep 1

# Run samples against live Raindrop environment (assumes RAINDROP_TOKEN in env!)
run_examples:
    # Listed in order of complexity, list_* are read-only, rest make changes.
    # We try to be nice to Raindrop by resting between each file.
    python examples/list_authorised_user.py
    just sleep
    python examples/list_collections.py
    just sleep
    python examples/list_tags.py
    just sleep
    python examples/create_collection.py
    just sleep
    python examples/edit_collection.py
    just sleep
    python examples/create_raindrop_file.py
    just sleep
    python examples/create_raindrop_link.py
    just sleep
    python examples/edit_raindrop.py
    just sleep
    python examples/search_raindrop.py
