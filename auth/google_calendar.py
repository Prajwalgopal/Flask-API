import io
import tempfile
import datetime
import flask

from apiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import googleapiclient.discovery
from auth import google_auth

app = flask.Blueprint('google_calendar', __name__)

def build_drive_api_v3():
    credentials = google_auth.build_credentials()
    return googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)


def get_events(max):
    calendar_api = build_drive_api_v3()
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time

    events = calendar_api.events().list(calendarId='primary', timeMin=now, maxResults=max, singleEvents=True, orderBy='startTime').execute()
    # print(events)
    return events

def create_event(title, start, end):
    calendar_api = build_drive_api_v3()
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    payload = {
        "summary": title,
        "start": {
            "timeZone": "Europe/Dublin",
            "dateTime": start + "+00:00"
        },
        "end": {
            "timeZone": "Europe/Dublin",
            "dateTime": end + "+00:00"
        }
    }
    events = calendar_api.events().insert(calendarId='primary', body=payload).execute()
    return events
