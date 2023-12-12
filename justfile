set dotenv-load

# The list of available targets
default:
    @just --list

################################################################################
# Build/Release environment management
################################################################################
# Refresh the version of 'manage' we have installed in our venv from github.
refresh_manage:
    @poetry remove manage --group dev
    @poetry add git+https://github.com/PBorocz/manage --group dev

################################################################################
# Development...
################################################################################
# Run the build/release management interface
manage *args:
    @manage {{args}}

# Run tests
test *args:
    @python -m pytest {{args}}

# Build docs
docs *args:
    # Note: We don't need to copy this in either a github workflow OR our 'manage' environment for releases
    # since ReadTheDocs is configured to auto-rebuild our docs *upon each commit to our trunk branch*!
    # This is for local use only to test out documentation updates/changes
    sphinx-build -v -W -b html "docs" "docs/_build" {{args}}

# Pre-commit - Run all
pre-commit-all *args:
    @pre-commit run --all-files {{args}}
    @echo "Running vulture..."
    @vulture

# Pre-commit - Update to a new pre-commit configuration and run
pre-commit-update *args:
    @pre-commit install
    @git add .pre-commit-config.yaml
    @just pre-commit-all {{args}}

# Run fawltydeps to assess package usage vs. installation.
fawltydeps *args:
    time fawltydeps --detailed {{args}}

# In lieu of a formal integration test suite, run samples against live Raindrop environment.
examples:
    # Listed in order of complexity, list_* are read-only, rest make changes.
    # We try to be nice to Raindrop by resting between each file.
    python examples/RUN_ALL.py
