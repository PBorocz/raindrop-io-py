"""Low-level API interface to Raindrop, no application semantics, mostly core HTTP verbs.

Except for instantiating, methods in this class are **not** intended for direct use, they serve as the underlying HTTPS
abstraction layer for calls available for the Core Classes, ie. Collection, Raindrop etc.
"""
import datetime
import enum
import json
from pathlib import Path
from typing import Any, Final, TypeVar

import requests
from requests_oauthlib import OAuth2Session

# Support for generic oauth2 authentication *on behalf of another user*
# (ie. instead of using Raindrop.IO's TEST_TOKEN)
URL_AUTHORIZE: Final = "https://raindrop.io/oauth/authorize"
URL_ACCESS_TOKEN: Final = "https://raindrop.io/oauth/access_token"
URL_REFRESH: Final = "https://raindrop.io/oauth/access_token"

# In py3.11, we'll be able to do 'from typing import Self' instead
T_API = TypeVar("API")


class API:
    """Provides communication to the Raindrop.io API server.

    Parameters:
        token: Either a string representing a valid RaindropIO Token.
            This is either a TEST_TOKEN or a CLIENT token for use in OAuth in
            which case the client_id and client_secret must also be provided.

        token_type: Token type to be used on behalf of an oAuth connection.

    Examples:
        Can either be used directly as a context manager:

        >>> api = API(token="yourTestTokenFromRaindropIO"):
        >>> collections = Collection.get_collections(api)
        >>> # ...

        or

        >>> with API(token="yourTestTokenFromRaindropIO") as api:
        >>>     user = User.get(api)
        >>>     # ...
    """

    def __init__(
        self,
        token: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        token_type: str = "Bearer",
    ) -> None:
        """Instantiate an API connection to Raindrop using the token (and optional client information) provided."""
        self.token = token
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_type = token_type
        self.session = None

        # If rate limiting is in effect, set here (UNTESTED!)
        self.ratelimit: int | None = None
        self.ratelimit_remaining: int | None = None
        self.ratelimit_reset: int | None = None

        self.open()

    def _create_session(self) -> OAuth2Session:
        """Handle the creation and/or authentication with oAuth handshake."""
        extra: dict[str, Any] | None
        if self.client_id and self.client_secret:
            extra = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
        else:
            extra = None

        def update_token(newtoken: str) -> None:
            self.token = newtoken

        token = {"access_token": self.token} if isinstance(self.token, str) else self.token

        return OAuth2Session(
            self.client_id,
            token=token,
            auto_refresh_kwargs=extra,
            auto_refresh_url=URL_REFRESH,
            token_updater=update_token,
        )

    def open(self) -> None:
        """Open a new connection to Raindrop.

        If there's an existing connection already, it'll be closed first.
        """
        self.close()
        self.session = self._create_session()

    def close(self) -> None:
        """Close an existing Raindrop connection.

        Safe to call even if a new session hasn't been created yet.
        """
        if self.session:
            self.session.close()
            self.session = None

    def _json_unknown(self, obj: Any) -> Any:
        if isinstance(obj, enum.Enum):
            return obj.value
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        raise TypeError(
            f"Object of type {obj.__class__.__name__} is not JSON serializable",
        )

    def _to_json(self, obj: Any) -> str | None:
        """Handle JSON serialisation with a custom serialiser to handle enums and datetimes."""
        if obj is not None:
            return json.dumps(obj, default=self._json_unknown)
        else:
            return None

    def _on_resp(self, resp: Any) -> None:
        """Handle a RaindropIO API response, first pulling rate-limiting parms in effect due to high activity levels."""

        def get_int(name: str) -> int | None:
            value = resp.headers.get(name, None)
            if value is not None:
                return int(value)
            return None

        v = get_int("X-RateLimit-Limit")
        if v is not None:
            self.ratelimit = v

        v = get_int("X-RateLimit-Remaining")
        if v is not None:
            self.ratelimit_remaining = v

        v = get_int("X-RateLimit-Reset")
        if v is not None:
            self.ratelimit_reset = v

        resp.raise_for_status()  # Let requests library handle HTTP error codes returned.

    def _request_headers_json(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
        }

    def get(
        self,
        url: str,
        params: dict[Any, Any] | None = None,
    ) -> requests.models.Response:
        """Send a GET request.

        Parameters:
            url: The url to send the request to.

            params: Optional dictionary of payload to be sent for the :class:`Request`.

        Returns:
            :class:`requests.Response` object.
        """
        assert self.session
        ret = self.session.get(url, headers=self._request_headers_json(), params=params)
        self._on_resp(ret)
        return ret

    def put(self, url: str, json: Any = None) -> requests.models.Response:
        """Low-level call to perform a PUT method against our present connection.

        Parameters:
            url: The url to send the PUT request to.

            json: JSON object to be sent.

        Returns:
            :class:`requests.Response` object.
        """
        json = self._to_json(json)

        assert self.session
        ret = self.session.put(url, headers=self._request_headers_json(), data=json)
        self._on_resp(ret)
        return ret

    def put_file(
        self,
        url: str,
        path: Path,
        data: dict,
        files: dict,
    ) -> requests.models.Response:
        """Upload a file by a PUT request.

        Parameters:
            url: The url to send the PUT request to.

            path: Path to file to be uploaded.

            data: Dictionary, payload to be sent for the :class:`Request`, e.g. {"collectionId" : aCollection.id}

            files: Dictionary, request library "files" object to be sent for the :class:`Request`,
                e.g. {'file': (aFileName, aFileLikeObj, aContentType)}

        Returns:
            :class:`requests.Response` object.
        """
        assert self.session
        ret = self.session.put(url, data=data, files=files)
        self._on_resp(ret)
        return ret

    def post(self, url: str, json: Any = None) -> requests.models.Response:
        """Low-level call to perform a POST method against our present connection.

        Parameters:
            url: The url to send the POST request to.

            json: JSON object to be sent.

        Returns:
            :class:`requests.Response` object.
        """
        json = self._to_json(json)
        assert self.session
        ret = self.session.post(url, headers=self._request_headers_json(), data=json)
        self._on_resp(ret)
        return ret

    def delete(self, url: str, json: Any = None) -> requests.models.Response:
        """Low-level call to perform a DELETE method against our present connection.

        Parameters:
            url: The url to send the DELETE request to.

            json: JSON object to be sent.

        Returns:
            :class:`requests.Response` object.
        """
        json = self._to_json(json)

        assert self.session
        ret = self.session.delete(url, headers=self._request_headers_json(), data=json)
        self._on_resp(ret)
        return ret

    def __enter__(self) -> T_API:  # Note: Py3.11 upgrade to "self"
        """Context manager use: if we don't have an active session open yet, open one!."""
        if not self.session:
            self.open()
        return self

    def __exit__(self, _type, _value, _traceback) -> None:  # type: ignore
        """Context manager use: once we're done with this API's scope, close connection off."""
        if self.session:
            self.close()
