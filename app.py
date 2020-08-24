import io
import tempfile
from werkzeug.utils import secure_filename
from apiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import datetime

import functools
import json
import os
import flask
from flask_cors import CORS, cross_origin
import google.oauth2.credentials
import googleapiclient.discovery

import uuid
import requests
from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session
import msal
import app_config

from auth import google_auth
from auth import google_drive
from auth import google_calendar
from auth import google_email

from auth import md_auth

app = flask.Flask(__name__)

app.secret_key = os.environ.get("FN_FLASK_SECRET_KEY", default=False)
app.register_blueprint(google_auth.app)
app.register_blueprint(google_drive.app)
app.register_blueprint(google_calendar.app)
app.register_blueprint(google_email.app)
app.register_blueprint(md_auth.app)

app.config.from_object(app_config)
Session(app)

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def ms_user():
    token = _get_token_from_cache(app_config.SCOPE)
    response = requests.get(app_config.USER_ENDPOINT, headers={'Authorization': 'Bearer ' + token['access_token']},).json()
    data = {
        "name": response['displayName'],
        "picture": ""
    }
    return data

@app.route('/test')
def test():
    token = _get_token_from_cache(app_config.SCOPE)
    response = requests.get(app_config.USER_ENDPOINT, headers={'Authorization': 'Bearer ' + token['access_token']},).json()
    return json.dumps(response)

@app.route('/login')
def login():
    return flask.render_template('login.html')

@app.route('/logout')
def logout():
    if google_auth.is_logged_in():
        return flask.redirect(url_for('google_auth.google_logout'), code=302)
    else:
        token = _get_token_from_cache(app_config.SCOPE)
        if not token:
            return redirect(url_for('login'))
        else:
            return flask.redirect(url_for('md_auth.microsoft_logout'), code=302)

@app.route('/')
def index():
    if google_auth.is_logged_in():
        return flask.render_template('index.html', user_info=google_auth.get_user_info())
    else:
        token = _get_token_from_cache(app_config.SCOPE)
        if not token:
            return redirect(url_for('login'))
        else:
            return flask.render_template('index.html', user_info=ms_user())

@app.route('/drive')
def drive():
    if google_auth.is_logged_in():
        drive_fields = "files(id,name,mimeType,createdTime,modifiedTime,shared,webContentLink)"
        items = google_drive.build_drive_api_v3().list(
                        pageSize=20, orderBy="folder", q='trashed=false',
                        fields=drive_fields
                    ).execute()
        return flask.render_template('drive.html', files=items['files'], user_info=google_auth.get_user_info())
    else:
        token = _get_token_from_cache(app_config.SCOPE)
        if not token:
            return redirect(url_for('login'))
        else:
            response = requests.get(app_config.DRIVE_ENDPOINT, headers={'Authorization': 'Bearer ' + token['access_token']},).json()
            drive_id = response['owner']['user']['id']
            response = requests.get(app_config.DRIVE_ENDPOINT + "/root/children", headers={'Authorization': 'Bearer ' + token['access_token']},).json()
            files = []
            for value in response['value']:
                if 'file' in value:
                    temp_file = {
                        "mimeType" : value['file']['mimeType'],
                        "id" : value['id'],
                        "drive_id": drive_id,
                        "name" : value['name'],
                        "createdTime" : value['fileSystemInfo']['createdDateTime'],
                        "modifiedTime" : value['fileSystemInfo']['lastModifiedDateTime'],
                        "webContentLink" : value['webUrl']
                    }
                    files.append(temp_file)
            return flask.render_template('drivems.html', files=files, user_info=ms_user())

@app.route('/calendar', methods=['GET', 'POST'])
def calendar():
    if request.method == 'POST':
        _title = request.form['title']
        _start = request.form['start']
        _end = request.form['end']
        if google_auth.is_logged_in():
            event = google_calendar.create_event(_title, _start, _end)
            return flask.redirect(url_for('calendar'), code=302)
        else:
            token = _get_token_from_cache(app_config.SCOPE)
            if not token:
                return redirect(url_for('login'))
            else:
                payload = {
                    "subject": _title,
                    "start": {
                            "dateTime": _start,
                            "timeZone": "Pacific Standard Time"
                        },
                    "end": {
                        "dateTime": _end,
                        "timeZone": "Pacific Standard Time"
                    }
                }
                response = requests.post(app_config.EVENT_ENDPOINT, headers={'Authorization': 'Bearer ' + token['access_token']}, json=payload)
                if response.status_code != 201:
                    return response.text
                else:
                    return flask.redirect(url_for('calendar'), code=302)
        return json.dumps(payload)
    elif request.method == 'GET':
        if google_auth.is_logged_in():
            items = google_calendar.get_events(365)
            event = []
            for item in items['items']:
                temp = {
                    "title": item["summary"],
                    "start": item["start"]["dateTime"].split("+")[0] + "Z",
                    "end": item["end"]["dateTime"].split("+")[0] + "Z",
                    "url": item["htmlLink"]
                }
                event.append(temp)
            calendar_data = {
                "today": str(datetime.date.today()),
                "items": event
            }
            return flask.render_template('calendar.html', data=calendar_data, user_info=google_auth.get_user_info())
        else:
            token = _get_token_from_cache(app_config.SCOPE)
            if not token:
                return redirect(url_for('login'))
            else:
                items = requests.get(app_config.EVENT_ENDPOINT, headers={'Authorization': 'Bearer ' + token['access_token']},).json()
                # print(items)
                event = []
                for item in items['value']:
                    temp = {
                        "title": item["subject"],
                        "start": item["start"]["dateTime"].split(".")[0],
                        "end": item["end"]["dateTime"].split(".")[0],
                        "url": item["webLink"]
                    }
                    event.append(temp)
                calendar_data1 = {
                    "today": str(datetime.date.today()),
                    "items": event
            }
                return flask.render_template('calendar.html', data=calendar_data1, user_info=ms_user())
        return 'You are not currently logged in.'

@app.route('/email')
def mail():
    if google_auth.is_logged_in():
        return flask.render_template('email.html', data=google_email.get_email(), user_info=google_auth.get_user_info())
    else:
        token = _get_token_from_cache(app_config.SCOPE)
        if not token:
            return redirect(url_for('login'))
        else:
            token = _get_token_from_cache(app_config.SCOPE)
            response = requests.get(app_config.EMAIL_ENDPOINT, headers={'Authorization': 'Bearer ' + token['access_token']},).json()
            data = []
            for value in response['value']:
                if 'id' in value:
                    print()
                    print(type(value))
                    if 'sender' in value:
                        print(value)
                        temp_data = {
                            "id": value['id'],
                            "from": value['sender']['emailAddress']['address'],
                            "subject": value['subject'],
                            "sender": value['sender']['emailAddress']['name'],
                            "date": value['sentDateTime']
                        }
                        data.append(temp_data)
                        f = open('/tmp/email/'+value['id'] + ".html",'w')
                        f.write(value['body']['content'])
                        f.close()        
            return flask.render_template('email.html', data=data, user_info=ms_user())

@app.route('/email/<id>')
def open_mail(id):
    if google_auth.is_logged_in():
        return flask.send_from_directory('/tmp/email/', id + '.html')
    else:
        token = _get_token_from_cache(app_config.SCOPE)
        if not token:
            return redirect(url_for('login'))
        else:
            return flask.send_from_directory('/tmp/email/', id + '.html')

def _get_token_from_cache(scope=None):
    cache = _load_cache()
    cca = _build_msal_app(cache=cache)
    accounts = cca.get_accounts()
    if accounts:
        result = cca.acquire_token_silent(scope, account=accounts[0])
        _save_cache(cache)
        return result

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

@app.route('/msdrive/view/<file_id>/<drive_id>', methods=['GET'])
def download_file(file_id, drive_id):
    token = _get_token_from_cache(app_config.SCOPE)
    response = requests.get("https://graph.microsoft.com/v1.0/drives/" + drive_id + "/items/" + file_id + "/content", headers={'Authorization': 'Bearer ' + token['access_token']}, allow_redirects=True)
    # if response.status_code == 302:
    with open('/tmp/' + file_id, 'wb') as file:
        file.write(response.content)
    return flask.send_from_directory('/tmp/', file_id)

@app.route('/msdrive/upload', methods=['GET', 'POST'])
def msupload_file():
    token = _get_token_from_cache(app_config.SCOPE)
    if 'file' not in flask.request.files:
        return flask.redirect('/')

    file = flask.request.files['file']
    if (not file):
        return flask.redirect('/')
        
    filename = secure_filename(file.filename)

    fp = tempfile.TemporaryFile()
    ch = file.read()
    fp.write(ch)
    fp.seek(0)

    mime_type = flask.request.headers['Content-Type']
    response = requests.put("https://graph.microsoft.com/v1.0/me/drive/root:/" + filename + ":/content", headers={'Authorization': 'Bearer ' + token['access_token']}, data=fp)
    # return response.text
    return flask.redirect(url_for('drive'), code=302)