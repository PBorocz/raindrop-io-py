from unittest.mock import patch

from raindroppy.api import API, Tag, Collection

tag = {
    "tag": "a Sample Tag",
    "count": 1
}


def test_get() -> None:
    api = API("dummy")
    with patch("raindroppy.api.api.OAuth2Session.request") as m:
        m.return_value.json.return_value = {"items": [tag]}

        tags = Tag.get(api)

        assert len(tags) == 1
        assert tags[0].tag == "a Sample Tag"
        assert tags[0].count == 1
