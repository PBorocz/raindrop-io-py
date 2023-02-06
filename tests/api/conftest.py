"""Provide all shared test fixtures."""
import os

import dotenv
import pytest

from raindropiopy.api import API

dotenv.load_dotenv()


@pytest.fixture
def api():
    """Fixture to return a valid API instance."""
    yield API(os.environ["RAINDROP_TOKEN"])