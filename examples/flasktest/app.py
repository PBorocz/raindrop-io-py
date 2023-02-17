"""Sample minimal Flask app demonstrating oAuth credential handling. WARNING: COMPLETELY UNTESTED!!!."""
#
# Note: per Raindrop's API documentation, if you're only accessing
# your own Raindrop environment, you do not need to do this, the
# simple "TEST_TOKEN" approach is completely sufficient.
#
# If you're building tools allowing other people to access THEIR
# Raindrop environment, you'll need to use the oAuth approach.
#
# Ref: https://developer.raindrop.io/v1/authentication/token
#
import os
from typing import Any

from dotenv import load_env
from flask import Flask, redirect, render_template_string, request
from requests_oauthlib import OAuth2Session
from werkzeug import Response

from raindropiopy import API, Collection, URL_AUTHORIZE, URL_ACCESS_TOKEN

load_env()

CLIENT_ID = os.environ["RAINDROP_CLIENT_ID"]
CLIENT_SECRET = os.environ["RAINDROP_CLIENT_SECRET"]
REDIRECT_URI = "http://localhost:5000/approved"

app = Flask(__name__)

INDEX = """
<html>
  <a href="./login">Click here for login.</a>
</html>
"""


COLLECTIONS = """
<html>
  <ul>
    {% for collection in collections %}
      <li>{{collection.title}}
    {% endfor %}
  </ul>
</html>
"""


def create_oauth2session(*args: Any, **kwargs: Any) -> OAuth2Session:
    """Utility method to use requests obo oauth credential handling."""
    session = OAuth2Session(*args, **kwargs)
    #    session.register_compliance_hook("access_token_response", update_expires)
    #    session.register_compliance_hook("refresh_token_response", update_expires)
    return session


@app.route("/approved")
def approved() -> str:
    """Route called upon successful authentication."""
    oauth = create_oauth2session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    code = request.args.get("code")
    token = oauth.fetch_token(
        URL_ACCESS_TOKEN,
        code=code,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        include_client_id=True,
    )

    with API(token, client_id=CLIENT_ID, client_secret=CLIENT_SECRET) as cnxn:
        collections = Collection.get_root_collections(cnxn)

    return render_template_string(COLLECTIONS, collections=collections)


@app.route("/login")
def login() -> Response:
    """Route called once credentials have been gathered."""
    oauth = create_oauth2session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    authorization_url, _ = oauth.authorization_url(URL_AUTHORIZE)
    return redirect(authorization_url)


@app.route("/")
def index() -> str:
    """Top-level route."""
    return render_template_string(INDEX)


if __name__ == "__main__":
    app.run(debug=True)
