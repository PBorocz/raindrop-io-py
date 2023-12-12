"""Provide all shared test fixtures for API tests."""

import pytest
from pathlib import Path

from vcr import VCR

from raindropiopy import API


# Define once for "from tests.api.conftest import vcr" in every test where we touch Raindrop.
vcr = VCR(
    cassette_library_dir=str(Path(__file__).parent / Path("cassettes")),
    filter_headers=["Authorization"],
    path_transformer=VCR.ensure_suffix(".yaml"),
)


@pytest.fixture()
def mock_api():
    """Fixture for a "mock" API instance."""
    yield API("dummy")
