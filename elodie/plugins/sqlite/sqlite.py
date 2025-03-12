"""
SQLite plugin object.
This plugin stores metadata about all media in an sqlite database.

You'll need to include [PluginSQLite] in your config file.
By default, the sqlite database will be created in your application 
    directory. If you want to specify a different path then 
    specify a fully qualified `database_file` path.

```
[PluginSQLite]
database_file=/path/to/database.db

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function

import json
import os
import sqlite3
import time
#import json

#from google_auth_oauthlib.flow import InstalledAppFlow
#from google.auth.transport.requests import AuthorizedSession
#from google.oauth2.credentials import Credentials

from elodie.geolocation import place_name
from elodie.localstorage import Db
from elodie.media.base import Base, get_all_subclasses
from elodie.plugins.plugins import PluginBase

class SQLite(PluginBase):
    """A class to execute plugin actions.
       
       Requires a config file with the following configurations set.
       database_file:
            The full path to the SQLite database (.db).
    
    """

    __name__ = 'SQLite'

    def __init__(self):
        super(SQLite, self).__init__()
        
        # Default the database file to be in the application plugin directory.
        # Override with value from config file.
        self.database_file = '{}/plugins/{}/elodie.db'.format(
            self.application_directory,
            __name__.lower()
        )
        if('database_file' in self.config_for_plugin):
            self.database_file = self.config_for_plugin['database_file']

        self.con = sqlite3.connect(self.database_file)
        self.con.row_factory = sqlite3.Row
        self.cursor = self.con.cursor()
        if(not self._validate_schema()):
            self._create_schema()

    def after(self, file_path, destination_folder, final_file_path, metadata):
        self._upsert(file_path, destination_folder, final_file_path, metadata)

    def batch(self):
        pass

    def before(self, file_path, destination_folder):
        pass

    def generate_db(self):
        db = Db()
        for checksum, file_path in db.all():
            subclasses = get_all_subclasses()
            media = Base.get_class_by_file(file_path, get_all_subclasses())
            media.set_checksum(
                db.checksum(file_path)
            )
            metadata = media.get_metadata()
            destination_folder = os.path.dirname(file_path)
            final_file_path = '{}{}'.format(os.path.sep, os.path.basename(file_path))
            self._upsert(file_path, destination_folder, final_file_path, metadata)

    def _create_schema(self):
        self.database_schema = '{}{}{}'.format(
            os.path.dirname(os.path.realpath(__file__)),
            os.sep,
            'schema.sql'
        )

        with open(self.database_schema, 'r') as fp_schema:
            sql_statement = fp_schema.read()
            self.cursor.executescript(sql_statement)

    def _insert_row_sql(self, final_path, metadata):
        path = '{}/{}.{}'.format(
                    metadata['directory_path'],
                    metadata['base_name'],
                    metadata['extension']
                )
        return (
                """INSERT INTO `metadata` (
                    `hash`, `path`, `album`, `camera_make`, `camera_model`,
                    `date_taken`, `latitude`, `location_name`, `longitude`,
                    `original_name`, `title`, `_modified`)
                    VALUES (
                    :hash, :path, :album, :camera_make, :camera_model,
                    :date_taken, :latitude, :location_name, :longitude,
                    :original_name, :title, datetime('now'))""",
                self._sql_values(final_path, metadata)
        )

    def _run_query(self, sql, values):
        self.cursor.execute(sql, values)
        return self.cursor.fetchall()

    def _sql_values(self, final_path, metadata, current_path=None):
        timestamp = int(time.time())
        return {
                    'hash': metadata['checksum'],
                    'path': final_path,
                    'album': metadata['album'],
                    'camera_make': metadata['camera_make'],
                    'camera_model': metadata['camera_model'],
                    'date_taken': time.strftime('%Y-%m-%d %H:%M:%S', metadata['date_taken']),
                    'latitude': metadata['latitude'],
                    'location_name': place_name(metadata['latitude'], metadata['longitude'])['default'],
                    'longitude': metadata['longitude'],
                    'original_name': metadata['original_name'],
                    'title': metadata['title'],
                    'current_path': current_path
                }

    def _update_row_sql(self, current_path, final_path, metadata):
        timestamp = int(time.time())
        return (
            """UPDATE `metadata` SET `hash`=:hash, `path`=:path, `album`=:album, `camera_make`=:camera_make,
                `camera_model`=:camera_model, `date_taken`=:date_taken, `latitude`=:latitude,
                `longitude`=:longitude, `original_name`=:original_name, `title`=:title, `_modified`=datetime('now')
                WHERE `path`=:current_path""",
            self._sql_values(final_path, metadata, current_path)
        )

    def _upsert(self, file_path, destination_folder, final_file_path, metadata):
        # We check if the source path exists in the database already.
        # If it does then we assume that this is an update operation.
        full_destination_path = '{}{}'.format(destination_folder, final_file_path)
        self.cursor.execute("SELECT `path` FROM `metadata` WHERE `path`=:path", {'path': file_path})

        if(self.cursor.fetchone() is None):
            self.log(u'SQLite plugin inserting {}'.format(file_path))
            sql_statement, sql_values = self._insert_row_sql(full_destination_path, metadata)
        else:
            self.log(u'SQLite plugin updating {}'.format(file_path))
            sql_statement, sql_values = self._update_row_sql(file_path, full_destination_path, metadata)

        self.cursor.execute(sql_statement, sql_values)

    def _validate_schema(self):
        try:
            self.cursor.execute('SELECT * FROM `metadata` LIMIT 1');
            return True
        except sqlite3.OperationalError:
            return False
