"""Test out the API using a patched requests module."""
import json
import time
from unittest.mock import patch

from requests import Response

from raindropiopy.api import API


def test_refresh() -> None:
    """Test the refresh method."""
    api = API(
        {
            "access_token": "old",
            "refresh_token": "bbb",
            "expires_at": time.time() - 100000,
        },
    )
    with patch("requests.Session.request") as m:
        resp = Response()
        resp.status_code = 200
        updated = {"access_token": "updated", "expires_at": time.time() + 100000}
        resp._content = json.dumps(updated).encode()

        m.return_value = resp
        api.get("https://localhost", {})

        refresh, local = m.call_args_list
        assert refresh[0] == ("POST", "https://raindrop.io/oauth/access_token")
        assert local[0] == ("GET", "https://localhost")

        assert isinstance(api.token, dict)
        assert api.token["access_token"] == "updated"
