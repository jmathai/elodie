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
    flow = InstalledAppFlow.from_client_secrets_file('/Users/jaisen/Downloads/client_secret_1004259275591-5g51kj0feetbet88o8le5i16hbr3ucb6.apps.googleusercontent.com-3.json', scopes)
    #creds = tools.run_flow(flow, store)
    creds = flow.run_local_server(host='localhost',
                                  port=8080,
                                  authorization_prompt_message="",
                                  success_message='The auth flow is complete; you may close this window.',
                                  open_browser=True)
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


"""google_photos = build('photoslibrary', 'v1', http=creds.authorize(Http()))
results = google_photos.mediaItems().list().execute()
items = results.get('mediaItems', [])
print(items)"""

session.headers["Content-type"] = "application/octet-stream"
session.headers["X-Goog-Upload-Protocol"] = "raw"
session.headers["X-Goog-Upload-File-Name"] = 'foo.jpg' #os.path.basename(photo_file_name)

photo_file = open("/Users/jaisen/Downloads/test.png", mode='rb')
photo_bytes = photo_file.read()

print(photo_bytes)

upload_token = session.post('https://photoslibrary.googleapis.com/v1/uploads', photo_bytes)
if (upload_token.status_code == 200) and (upload_token.content):
    create_body = json.dumps({"newMediaItems":[{"description":"","simpleMediaItem":{"uploadToken":upload_token.content.decode()}}]}, indent=4)
    resp = session.post('https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate', create_body).json()
    print(resp)
    if "newMediaItemResults" in resp:
        status = resp["newMediaItemResults"][0]["status"]
        print(status)
