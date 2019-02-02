import logging
import os
import uuid

import adal
import flask
from flask import jsonify

import config

app = flask.Flask(__name__)
app.debug = True
app.secret_key = "my secreate key"

PORT = os.getenv("PORT")
AUTHORITY_URL = config.AUTHORITY_HOST_URL + "/" + config.TENANT
REDIRECT_URI = "http://localhost:{}/getAToken".format(PORT)
TEMPLATE_AUTHZ_URL = (
    "https://login.microsoftonline.com/{}/oauth2/authorize?"
    + "response_type=code&client_id={}&redirect_uri={}&"
    + "state={}&resource={}"
)


@app.route("/")
def main():
    login_url = "http://localhost:{}/login".format(PORT)
    resp = flask.Response(status=307)
    resp.headers["location"] = login_url
    return resp


@app.route("/login")
def login():
    auth_state = str(uuid.uuid4())
    flask.session["state"] = auth_state
    authorization_url = TEMPLATE_AUTHZ_URL.format(
        config.TENANT, config.CLIENT_ID, REDIRECT_URI, auth_state, config.RESOURCE
    )
    resp = flask.Response(status=307)
    resp.headers["location"] = authorization_url
    return resp


@app.route("/getAToken")
def main_logic():
    code = flask.request.args["code"]
    state = flask.request.args["state"]
    if state != flask.session["state"]:
        raise ValueError("State does not match")
    auth_context = adal.AuthenticationContext(AUTHORITY_URL)
    token_response = auth_context.acquire_token_with_authorization_code(
        code, REDIRECT_URI, config.RESOURCE, config.CLIENT_ID, config.CLIENT_SECRET
    )
    # It is recommended to save this to a database when using a production app.
    flask.session["access_token"] = token_response["accessToken"]

    return flask.redirect("/privateurl")


@app.route("/privateurl")
def privateurl():
    if "access_token" not in flask.session:
        return flask.redirect(flask.url_for("login"))

    token = flask.session.get("access_token")
    logging.info(f"Token: {token}")

    return jsonify({"token": token})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=os.getenv("PORT"))
