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

        # Updating a title can be problematic when doing it 2+ times on a file.
        # You would end up with img_001.jpg -> img_001-first-title.jpg -> img_001-first-title-second-title.jpg.
        # To resolve that we have to track the prior title (if there was one.
        # Then we massage the updated_media's metadata['base_name'] to remove the old title.
        # Since FileSystem.get_file_name() relies on base_name it will properly rename the file by updating the title
        #     instead of appending it.
        remove_old_title_from_name = False
        if(config['title'] is not None):
            # We call get_metadata() to cache it before making any changes
            metadata = media.get_metadata()
            title_update_status = media.set_title(config['title'])
            original_title = metadata['title']
            if(title_update_status and original_title is not None):
                # @TODO: We should move this to a shared method since FileSystem.get_file_name() does it too.
                original_title = re.sub('\W+', '-', original_title.lower())
                original_base_name = metadata['base_name']
                remove_old_title_from_name = True
            updated = True
                
        if(updated == True):
            updated_media = _class(file_path)
            # See comments above on why we have to do this when titles get updated.
            if(remove_old_title_from_name is True and len(original_title) > 0):
                updated_media.get_metadata()
                updated_media.set_metadata_basename(original_base_name.replace('-%s' % original_title, ''))

            dest_path = filesystem.process_file(file_path, destination, updated_media, move=True, allowDuplicate=True)
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
