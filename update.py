#!/usr/bin/env python

import os
import pyexiv2
import re
import shutil
import sys
import time

from datetime import datetime

from elodie import arguments
from elodie import constants
from elodie import geolocation
from elodie.media.photo import Media
from elodie.media.photo import Photo
from elodie.media.video import Video
from elodie.filesystem import FileSystem
from elodie.localstorage import Db

def parse_arguments(args):
    config = {
        'title': None,
        'time': None,
        'location': None,
        'album': None,
        'process': 'yes'
    }
    
    config.update(args)
    return config

def main(config, args):
    location_coords = None
    for arg in args:
        file_path = arg
        if(arg[:2] == '--'):
            continue
        elif(not os.path.exists(arg)):
            if(constants.debug == True):
                print 'Could not find %s' % arg
            print '{"source":"%s", "error_msg":"Could not find %s"}' % (file_path, arg)
            continue

        destination = os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
        
        _class = None
        extension = os.path.splitext(file_path)[1][1:].lower()
        if(extension in Photo.get_valid_extensions()):
            _class = Photo
        elif(extension in Video.get_valid_extensions()):
            _class = Video

        if(_class is None):
            continue

        media = _class(file_path)

        updated = False
        if(config['location'] is not None):
            if(location_coords is None):
                location_coords = geolocation.coordinates_by_name(config['location'])

            if(location_coords is not None and 'latitude' in location_coords and 'longitude' in location_coords):
                location_status = media.set_location(location_coords['latitude'], location_coords['longitude'])
                if(location_status != True):
                    if(constants.debug == True):
                        print 'Failed to update location'
                    print '{"source":"%s", "error_msg":"Failed to update location"}' % file_path
                    sys.exit(1)
                updated = True


        if(config['time'] is not None):
            time_string = config['time']
            time_format = '%Y-%m-%d %H:%M:%S'
            if(re.match('^\d{4}-\d{2}-\d{2}$', time_string)):
                time_string = '%s 00:00:00' % time_string

            if(re.match('^\d{4}-\d{2}-\d{2}$', time_string) is None and re.match('^\d{4}-\d{2}-\d{2} \d{2}:\d{2}\d{2}$', time_string)):
                if(constants.debug == True):
                    print 'Invalid time format. Use YYYY-mm-dd hh:ii:ss or YYYY-mm-dd'
                print '{"source":"%s", "error_msg":"Invalid time format. Use YYYY-mm-dd hh:ii:ss or YYYY-mm-dd"}' % file_path
                sys.exit(1)

            if(time_format is not None):
                time = datetime.strptime(time_string, time_format)
                media.set_datetime(time)
                updated = True

        if(config['album'] is not None):
            media.set_album(config['album'])
            updated = True

        if(config['title'] is not None):
            media.set_title(config['title'])
            updated = True
                
        if(updated == True):
            dest_path = filesystem.process_file(file_path, destination, media, move=True, allowDuplicate=True)
            if(constants.debug == True):
                print '%s -> %s' % (file_path, dest_path)

            print '{"source":"%s", "destination":"%s"}' % (file_path, dest_path)
            # If the folder we moved the file out of or its parent are empty we delete it.
            filesystem.delete_directory_if_empty(os.path.dirname(file_path))
            filesystem.delete_directory_if_empty(os.path.dirname(os.path.dirname(file_path)))

db = Db()
filesystem = FileSystem()
args = arguments.parse(sys.argv[1:], None, ['title=','album=','time=','location=','process='], './update.py --time=<string time> --location=<string location> --process=no file1 file2...fileN')
config = parse_arguments(args)

if __name__ == '__main__':
    main(config, sys.argv)
    sys.exit(0)
