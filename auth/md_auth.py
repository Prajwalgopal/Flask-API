import functools
import os
import base64
import flask
import email
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery
from flask import flash, request, render_template, redirect, url_for
import uuid
import requests
from flask import Flask, session
from flask_session import Session
import msal
import app_config

app = flask.Blueprint('md_auth', __name__)
BASE_URI = os.environ.get("FN_BASE_URI", default=False)

def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache

def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()



def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app_config.CLIENT_ID, authority=authority or app_config.AUTHORITY,
        client_credential=app_config.CLIENT_SECRET, token_cache=cache)

def _build_auth_url(authority=None, scopes=None, state=None):
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("md_auth.authorized", _external=True))


@app.route('/microsoft/login')
def mslogin():
    session["state"] = str(uuid.uuid4())
    auth_url = _build_auth_url(scopes=app_config.SCOPE, state=session["state"])
    return redirect(auth_url)

@app.route(app_config.REDIRECT_PATH)
def authorized():
    if request.args.get('state') != session.get("state"):
        return redirect(url_for("index"))
    if "error" in request.args:  
        return render_template("auth_error.html", result=request.args)
    if request.args.get('code'):
        cache = _load_cache()
        result = _build_msal_app(cache=cache).acquire_token_by_authorization_code(
            request.args['code'],
            scopes=app_config.SCOPE,  # Misspelled scope would cause an HTTP 400 error here
            redirect_uri=url_for("md_auth.authorized", _external=True))
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        _save_cache(cache)
    return redirect(url_for("index"))
    # return "working"

@app.route("/microsoft/logout")
def microsoft_logout():
    session.clear()
    return flask.redirect(BASE_URI, code=302)
