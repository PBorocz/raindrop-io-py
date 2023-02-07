"""Provide all shared test fixtures for CLI tests."""
from pathlib import Path

from vcr import VCR


# Define once for "from tests.cli.conftest import vcr" in every test where we touch Raindrop.
vcr = VCR(
    cassette_library_dir=str(Path(__file__).parent / Path("cassettes")),
    filter_headers=["Authorization"],
)
