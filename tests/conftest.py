"""Provide shared test fixtures across *all* test suites."""
import os

import dotenv
import pytest

from raindropiopy import API

dotenv.load_dotenv()


@pytest.fixture
def api():
    """Fixture to return a valid API instance."""
    yield API(os.environ["RAINDROP_TOKEN"])
