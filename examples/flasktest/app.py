"""Sample minimal Flask app demonstrating oAuth credential handling."""
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

from dotenv import load_env
from flask import Flask, redirect, render_template_string, request
from werkzeug import Response

from raindroppy.api import API, Collection, create_oauth2session

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


@app.route("/approved")
def approved() -> str:
    oauth = create_oauth2session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    code = request.args.get("code")
    token = oauth.fetch_token(
        API.URL_ACCESS_TOKEN,
        code=code,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        include_client_id=True,
    )

    with API(token, client_id=CLIENT_ID, client_secret=CLIENT_SECRET) as CNXN:
        collections = Collection.get_roots(CNXN)

    return render_template_string(COLLECTIONS, collections=collections)


@app.route("/login")
def login() -> Response:
    oauth = create_oauth2session(CLIENT_ID, redirect_uri=REDIRECT_URI)
    authorization_url, _ = oauth.authorization_url(API.URL_AUTHORIZE)
    return redirect(authorization_url)


@app.route("/")
def index() -> str:
    return render_template_string(INDEX)


if __name__ == "__main__":
    app.run(debug=True)
