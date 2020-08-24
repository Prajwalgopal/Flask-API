import io
import tempfile
import datetime
import flask
import base64
import email
from apiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import googleapiclient.discovery
from auth import google_auth

app = flask.Blueprint('google_email', __name__)

def build_gmail_api_v1():
    credentials = google_auth.build_credentials()
    return googleapiclient.discovery.build('gmail', 'v1', credentials=credentials)

def parse_msg(message, service):
    unique_id = message['id']
    temp_file_name = '/tmp/email/' + message['id'] + '.html'
    snippet = message['snippet']
    mime_type = message['payload']['mimeType']
    msg_from = ""
    msg_subject = ""
    msg_sender = ""
    msg_date = ""
    for header in message['payload']['headers']:
        if header['name'] == "From":
            msg_from = header['value']
        elif header['name'] == "Sender":
            msg_sender = header['value']
        elif header['name'] == "Subject":
            msg_subject = header['value']
        elif header['name'] == "Date":
            msg_date = header = header['value']
    if mime_type == "text/plain":
        f = open(temp_file_name,'w')
        body = base64.urlsafe_b64decode(message['payload']['body']['data'].encode("ASCII")).decode("utf-8")
        f.write(body)
        f.close()
    elif mime_type == "text/html":
        f = open(temp_file_name,'w')
        body = base64.urlsafe_b64decode(message['payload']['body']['data'].encode("ASCII")).decode("utf-8")
        f.write(body)
        f.close()
    elif mime_type == "multipart/mixed":
        for part in message['payload']['parts']:
            for header in part['headers']:
                if header['name'] == "Content-Transfer-Encoding":
                    if header['value'] != '8bit':
                        part_mime_type = part['mimeType']
                        if part_mime_type == "text/plain" or part_mime_type == "text/html":
                            f = open(temp_file_name,'w')
                            body = base64.urlsafe_b64decode(part['body']['data'].encode("ASCII")).decode("utf-8")
                            f.write(body)
                            f.close()
                        else:
                            if(part['filename'] and part['body'] and part['body']['attachmentId']):
                                attachment = service.users().messages().attachments().get(id=part['body']['attachmentId'], userId='me', messageId=unique_id).execute()
                                file_data = base64.urlsafe_b64decode(attachment['data'].encode('utf-8'))
                                path = ''.join(['/tmp/email/ ', part['filename']])
                                f = open(path, 'wb')
                                f.write(file_data)
                                f.close()
    elif mime_type == "multipart/alternative":
        for part in message['payload']['parts']:
            for header in part['headers']:
                if header['name'] == "Content-Transfer-Encoding":
                    if header['value'] != '8bit':
                        part_mime_type = part['mimeType']
                        if part_mime_type == "text/plain" or part_mime_type == "text/html":
                            f = open(temp_file_name,'w')
                            body = base64.urlsafe_b64decode(part['body']['data'].encode("ASCII")).decode("utf-8")
                            f.write(body)
                            f.close()
    return {
        "id": unique_id,
        "from": msg_from,
        "subject": msg_subject,
        "sender": msg_sender,
        "date": msg_date
    }

def get_email():
    service = build_gmail_api_v1()
    results = service.users().messages().list(userId='me').execute()
    messages_minimal = []
    for message in results['messages']:
        result = service.users().messages().get(userId='me', id=message['id']).execute()
        messages_minimal.append(parse_msg(result, service))
    return messages_minimal