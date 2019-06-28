"""
Plugin object.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function
from builtins import object


class GooglePhotos(object):
    """A class to execute plugin actions."""
    pass

"""

import json

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials

scopes = [
"https://www.googleapis.com/auth/photoslibrary",
"https://www.googleapis.com/auth/photoslibrary.appendonly",
"https://www.googleapis.com/auth/photoslibrary.sharing"
]

auth_file = 'client_id.json'

try:
    creds = Credentials.from_authorized_user_file(auth_file, scopes)
except:
    print('no creds')
    #flow = InstalledAppFlow.from_client_secrets_file('/Users/jaisen/Downloads/client_secret_1004259275591-5g51kj0feetbet88o8le5i16hbr3ucb6.apps.googleusercontent.com-3.json', scopes)
    flow = InstalledAppFlow.from_client_secrets_file('/Users/jaisen/Downloads/client_secret_1004259275591-ogsk179e96cs0h126qj590mofk86gdqo.apps.googleusercontent.com.json', scopes)
    creds = flow.run_local_server()
    cred_dict = {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'id_token': creds.id_token,
        'scopes': creds.scopes,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret
    }

    with open(auth_file, 'w') as f:
        f.write(json.dumps(cred_dict))

session = AuthorizedSession(creds)



session.headers["Content-type"] = "application/octet-stream"
session.headers["X-Goog-Upload-Protocol"] = "raw"
session.headers["X-Goog-Upload-File-Name"] = 'foo.jpg' #os.path.basename(photo_file_name)

photo_file = open("/Users/jaisen/Downloads/test.png", mode='rb')
photo_bytes = photo_file.read()

upload_token = session.post('https://photoslibrary.googleapis.com/v1/uploads', photo_bytes)
if (upload_token.status_code == 200) and (upload_token.content):
    create_body = json.dumps({"newMediaItems":[{"description":"","simpleMediaItem":{"uploadToken":upload_token.content.decode()}}]}, indent=4)
    resp = session.post('https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate', create_body).json()
    print(resp)
    if "newMediaItemResults" in resp:
        status = resp["newMediaItemResults"][0]["status"]
        print(status)"""
