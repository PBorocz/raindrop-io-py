
# This list of available targets
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
# Test
test:
    python -m pytest

# Run our pre-commit checks manually
pre-commit *args:
    pre-commit run --all-files {{args}}
