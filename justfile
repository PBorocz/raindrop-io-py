
# This list of available targets
default:
    @just --list

################################################################################
# Development support...
################################################################################
# Test
test:
    python -m pytest

# Run our pre-commit checks manually
pre-commit:
    pre-commit run --all-files
