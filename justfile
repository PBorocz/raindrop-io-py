set dotenv-load

# The list of available targets
default:
    @just --list --unsorted

################################################################################
# Usage
################################################################################
# Run our command-line interface
cli:
    python raindroppy/cli/run.py

#(old way:)
#    python raindrop/cli/cli.py {{args}}

################################################################################
# Development support...
################################################################################
# Run local unit tests (fast, no connection or Raindrop.io configuration required)
test *args:
    python -m pytest {{args}}

# Run pre-commit from command-line
pre-commit-all *args:
    pre-commit run --all-files {{args}}

# Update the repo to the most recent .pre-commit-config.yaml and run it.
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
    # Be nice to Raindrop and rest in between each one.
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

################################################################################
# Packaging support...
################################################################################
# Clean our build enviroment:
clean:
    @echo "🚀 Cleaning house..."
    @rm -rf dist

# Build our package..
build:
    @just clean
    @echo "🚀 Patch update to version number..."
    @poetry version patch
    @echo "🚀 Building..."
    @poetry build

# Build and publish
build_and_publish:
    @just build
    @just publish

# Publish our build to *TestPyPi* (args: --dry-run for example)
publish *args:
    poetry publish --repository testpypi --username $PYPI_TEST_USERNAME --password $PYPI_TEST_PASSWORD {{args}}

    # NOTE: To pip install from TestPyPi and get the right packages.
    # pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple raindroppy (or raindroppy==x.y.z)
    # Ref: https://stackoverflow.com/questions/57405014/how-to-fix-no-matching-distribution-found-for-package-name-when-installing-o

# Publish our build to *production* PyPi:
publish_production:
    echo "🚀 Publishing: Dry run..."
    poetry config pypi-token.pypi $(PYPI_TOKEN)
    poetry publish --dry-run
    echo "🚀 Publishing..."
    poetry publish
