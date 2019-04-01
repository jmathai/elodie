from __future__ import print_function


import json
import os
import sys
import time

import zerorpc

import elodie_cli
from elodie.config import load_config
from elodie.filesystem import FileSystem

class ElodieApi(object):
    def get_files(self, destination, source):
        """about any text"""
        # def _import(destination, source, file, album_from_folder, trash, allow_duplicates, debug, paths):
        files = elodie_cli.get_files(
            destination,
            source, 
            False,  # file
            False,  # album_from_fiolder
            False,  # trash
            False,  # allow_duplicates
            True,   # debug
            []      # paths
        )

        print(json.dumps(files))

    def import_file(self, destination, _file):
        dest = elodie_cli.import_file(_file, destination, False, False, True)
        print(dest)

    def preview_file_name(self, fmt, metadata=None):
        filesystem = FileSystem()
        filesystem.default_folder_path_definition['full_path'] = '%date/%state'
        metadata = {'date_taken': time.localtime(), 'directory_path': '/Users/jaisen/dev/tmp/source', 'album': None, 'camera_make': u'Google', 'extension': 'jpg', 'title': None, 'base_name': 'IMG_20180830_110056', 'original_name': None, 'longitude': None, 'camera_model': u'Pixel', 'latitude': None, 'mime_type': 'image/jpeg'}
        return filesystem.get_folder_path(metadata)


def parse_port():
    port = 4242
    try:
        port = int(sys.argv[1])
    except Exception as e:
        pass
    return '{}'.format(port)

def main():
    elodie_api = ElodieApi()
    command = sys.argv[1]
    if command == 'get_files':
        destination = sys.argv[2]
        source = sys.argv[3]
        elodie_api.get_files(destination, source)
    elif command == 'import_file':
        destination = sys.argv[2]
        file = sys.argv[3]
        elodie_api.import_file(destination, file)


if __name__ == '__main__':
    main()
