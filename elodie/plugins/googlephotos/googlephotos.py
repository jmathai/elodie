"""
Google Photos plugin object.
This plugin will queue imported photos into the plugin's database file.
Using this plugin should have no impact on performance of importing photos.

In order to upload the photos to Google Photos you need to run the following command.

```
    ./elodie.py batch
```

That command will execute the batch() method on all plugins, including this one.
This plugin's batch() function reads all files from the database file and attempts to 
    upload them to Google Photos.
This plugin does not aim to keep Google Photos in sync.
Once a photo is uploaded it's removed from the database and no records are kept thereafter.

Upload code adapted from https://github.com/eshmu/gphotos-upload

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function

import json

from os.path import basename, isfile

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import AuthorizedSession
from google.oauth2.credentials import Credentials

from elodie import constants
from elodie.media.photo import Photo
from elodie.media.video import Video
from elodie.plugins.plugins import PluginBase

class GooglePhotos(PluginBase):
    """A class to execute plugin actions.
       
       Requires a config file with the following configurations set.
       secrets_file:
            The full file path where to find the downloaded secrets.
       auth_file:
            The full file path where to store authenticated tokens.
    
    """

    __name__ = 'GooglePhotos'

    def __init__(self):
        super(GooglePhotos, self).__init__()
        self.upload_url = 'https://photoslibrary.googleapis.com/v1/uploads'
        self.media_create_url = 'https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate'
        self.scopes = ['https://www.googleapis.com/auth/photoslibrary.appendonly']
        
        self.secrets_file = None
        if('secrets_file' in self.config_for_plugin):
            self.secrets_file = self.config_for_plugin['secrets_file']
        # 'client_id.json'
        self.auth_file = None
        if('auth_file' in self.config_for_plugin):
            self.auth_file = self.config_for_plugin['auth_file']
        self.session = None

    def after(self, file_path, destination_folder, final_file_path, metadata):
        extension = metadata['extension']
        if(extension in Photo.extensions or extension in Video.extensions):
            self.log(u'Added {} to db.'.format(final_file_path))
            self.db.set(final_file_path, metadata['original_name'])
        else:
            self.log(u'Skipping {} which is not a supported media type.'.format(final_file_path))

    def batch(self):
        queue = self.db.get_all()
        status = True
        count = 0
        for key in queue:
            this_status = self.upload(key)
            if(this_status):
                # Remove from queue if successful then increment count
                self.db.delete(key)
                count = count + 1
                self.display('{} uploaded successfully.'.format(key))
            else:
                status = False
                self.display('{} failed to upload.'.format(key))
        return (status, count)

    def before(self, file_path, destination_folder):
        pass

    def set_session(self):
        # Try to load credentials from an auth file.
        # If it doesn't exist or is not valid then catch the 
        #  exception and reauthenticate.
        try:
            creds = Credentials.from_authorized_user_file(self.auth_file, self.scopes)
        except:
            try:
                flow = InstalledAppFlow.from_client_secrets_file(self.secrets_file, self.scopes)
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

                # Store the returned authentication tokens to the auth_file.
                with open(self.auth_file, 'w') as f:
                    f.write(json.dumps(cred_dict))
            except:
                return

        self.session = AuthorizedSession(creds)
        self.session.headers["Content-type"] = "application/octet-stream"
        self.session.headers["X-Goog-Upload-Protocol"] = "raw"

    def upload(self, path_to_photo):
        if constants.dry_run:
            print(f"[DRY-RUN][GooglePhotos] Would upload photo: {path_to_photo}")
            return True
            
        self.set_session()
        if(self.session is None):
            self.log('Could not initialize session')
            return None

        self.session.headers["X-Goog-Upload-File-Name"] = basename(path_to_photo)
        if(not isfile(path_to_photo)):
            self.log('Could not find file: {}'.format(path_to_photo))
            return None

        with open(path_to_photo, 'rb') as f:
            photo_bytes = f.read()

        upload_token = self.session.post(self.upload_url, photo_bytes)
        if(upload_token.status_code != 200 or not upload_token.content):
            self.log('Uploading media failed: ({}) {}'.format(upload_token.status_code, upload_token.content))
            return None

        create_body = json.dumps({'newMediaItems':[{'description':'','simpleMediaItem':{'uploadToken':upload_token.content.decode()}}]}, indent=4)
        resp = self.session.post(self.media_create_url, create_body).json()
        if(
            'newMediaItemResults' not in resp or
            'status' not in resp['newMediaItemResults'][0] or
            'message' not in resp['newMediaItemResults'][0]['status'] or
            (
                resp['newMediaItemResults'][0]['status']['message'] != 'Success' and # photos
                resp['newMediaItemResults'][0]['status']['message'] != 'OK' # videos
            )

        ):
            self.log('Creating new media item failed: {}'.format(json.dumps(resp)))
            return None
        
        return resp['newMediaItemResults'][0]
