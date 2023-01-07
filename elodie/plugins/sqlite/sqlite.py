"""
SQLite plugin object.
This plugin stores metadata about all media in an sqlite database.

You'll need to create a SQLite database using the schema.sql file and 
    reference it in your configuration.

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

from elodie.media.photo import Photo
from elodie.media.video import Video
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
        
        self.database_schema = '{}{}{}'.format(os.path.dirname(os.path.realpath(__file__)), os.sep, 'schema.sql')
        self.database_file = None
        if('database_file' in self.config_for_plugin):
            self.database_file = self.config_for_plugin['database_file']

        self.con = sqlite3.connect(self.database_file)
        self.con.row_factory = sqlite3.Row
        self.cursor = self.con.cursor()

    def after(self, file_path, destination_folder, final_file_path, metadata):

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

    def batch(self):
        pass

    def before(self, file_path, destination_folder):
        pass

    def create_schema(self):
        with open(self.database_schema, 'r') as fp_schema:
            sql_statement = fp_schema.read()

        with self.con:
            self.cursor.executescript(sql_statement)

    def run_query(self, sql, values):
        self.cursor.execute(sql, values)
        return self.cursor.fetchall()

    def _insert_row_sql(self, final_path, metadata):
        timestamp = int(time.time())
        return (
                "INSERT INTO `metadata` (`path`, `metadata`, `created`, `modified`) VALUES(:path, :metadata, :created, :modified)",
                {'path': final_path, 'metadata': json.dumps(metadata), 'created': timestamp, 'modified': timestamp}
        )

    def _update_row_sql(self, current_path, final_path, metadata):
        timestamp = int(time.time())
        return (
            "UPDATE `metadata` SET `path`=:path, `metadata`=json(:metadata), `modified`=:modified WHERE `path`=:currentPath",
            {'currentPath': current_path, 'path': final_path, 'metadata': json.dumps(metadata), 'modified': timestamp}
        )
