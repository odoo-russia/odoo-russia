#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import httplib2

# sudo pip install --upgrade google-api-python-client
# sudo easy_install --upgrade google-api-python-client
from apiclient.discovery import build
from apiclient.http import MediaInMemoryUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

# Путь к файлу с токенами, формат json
token_file = 'token.txt'

CLIENT_ID = '540902438052-raqdgrlpdvnuu0b2mujim6qo9hb55vnu.apps.googleusercontent.com'
CLIENT_SECRET = 'S9xhrET8DGz_v2DWuoe2uhf7'
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive.file'
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

def create_token_file(token_file):
    flow = OAuth2WebServerFlow(
        CLIENT_ID,
        CLIENT_SECRET,
        OAUTH_SCOPE,
        REDIRECT_URI
        )
    authorize_url = flow.step1_get_authorize_url()
    # TODO: получать секретный код из базы?
    print('Go to the following link in your browser: ' + authorize_url)
    code = raw_input('Enter verification code: ').strip()
    credentials = flow.step2_exchange(code)
    storage = Storage(token_file)
    storage.put(credentials)
    return storage


def authorize(token_file, storage):
    if storage is None:
        storage = Storage(token_file)
    credentials = storage.get()
    http = httplib2.Http()
    credentials.refresh(http)
    http = credentials.authorize(http)
    return http


def upload_file(file_data, file_name, mime='application/octet-stream'):
    try:
        open(token_file)
    except IOError:
        http = authorize(token_file, create_token_file(token_file))
    http = authorize(token_file, None)
    drive_service = build('drive', 'v2', http=http)
    file_data = base64.b64decode(file_data)
    media_body = MediaInMemoryUpload(file_data,
                                 mimetype=mime,
                                 resumable=True)
    body = {
      'title': file_name,
      'description': 'File from OpenERP',
      'mimeType': mime,
    }
    permissions = {
      'role': 'reader',
      'type': 'anyone',
      'value': None,
      'withLink': True
    }
# Заливаем файл
    file = drive_service.files().insert(body=body, media_body=media_body).execute()
# Устанавливаем ему права
    drive_service.permissions().insert(fileId=file['id'], body=permissions).execute()
# Получаем инстанс файла и линк на скачку
    file = drive_service.files().get(fileId=file['id']).execute()
    download_url = file.get('webContentLink')
    return download_url

#download_link = upload_file('SGVsbG8gd29ybGQgbG9s', 'имя_файла')
#print download_link
