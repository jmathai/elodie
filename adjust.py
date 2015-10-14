#!/usr/bin/env python

import os
import pyexiv2
import re
import shutil
import sys
import time

from datetime import datetime

from elodie import arguments
from elodie import geolocation
from elodie.media.photo import Media
from elodie.media.photo import Photo
from elodie.media.video import Video
from elodie.filesystem import FileSystem
from elodie.localstorage import Db

def parse_arguments(args):
    config = {
        'time': None,
        'location': None,
        'process': 'yes'
    }
    
    config.update(args)
    return config

def main(config, args):
    for arg in args:
        if(arg[:2] == '--'):
            continue
        elif(not os.path.exists(arg)):
            print 'Could not find %s' % arg
            continue

        file_path = arg
        destination = os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
        
        _class = None
        extension = os.path.splitext(file_path)[1][1:].lower()
        if(extension in Photo.get_valid_extensions()):
            _class = Photo
        elif(extension in Video.get_valid_extensions()):
            _class = Video

        if(_class is None):
            continue

        write = False
        exif_metadata = pyexiv2.ImageMetadata(file_path)
        exif_metadata.read()
        if(config['location'] is not None):
            location_coords = geolocation.coordinates_by_name(config['location'])
            if(location_coords is not None and 'latitude' in location_coords and 'longitude' in location_coords):
                print 'Queueing location to exif ...',
                exif_metadata['Exif.GPSInfo.GPSLatitude'] = geolocation.decimal_to_dms(location_coords['latitude'])
                exif_metadata['Exif.GPSInfo.GPSLatitudeRef'] = pyexiv2.ExifTag('Exif.GPSInfo.GPSLatitudeRef', 'N' if location_coords['latitude'] >= 0 else 'S')
                exif_metadata['Exif.GPSInfo.GPSLongitude'] = geolocation.decimal_to_dms(location_coords['longitude'])
                exif_metadata['Exif.GPSInfo.GPSLongitudeRef'] = pyexiv2.ExifTag('Exif.GPSInfo.GPSLongitudeRef', 'E' if location_coords['longitude'] >= 0 else 'W')
                write = True
                print 'OK'

        if(config['time'] is not None):
            time_string = config['time']
            print '%r' % time_string
            time_format = '%Y-%m-%d %H:%M:%S'
            if(re.match('^\d{4}-\d{2}-\d{2}$', time_string)):
                time_string = '%s 00:00:00' % time_string

            if(re.match('^\d{4}-\d{2}-\d{2}$', time_string) is None and re.match('^\d{4}-\d{2}-\d{2} \d{2}:\d{2}\d{2}$', time_string)):
                print 'Invalid time format. Use YYYY-mm-dd hh:ii:ss or YYYY-mm-dd'
                sys.exit(1)

            if(time_format is not None):
                print 'Queueing time to exif ...',
                exif_metadata['Exif.Photo.DateTimeOriginal'].value = datetime.strptime(time_string, time_format)
                exif_metadata['Exif.Image.DateTime'].value = datetime.strptime(time_string, time_format)
                print '%r' % datetime.strptime(time_string, time_format)
                write = True
                print 'OK'
                
        if(write == True):
            exif_metadata.write()

            exif_metadata = pyexiv2.ImageMetadata(file_path)
            exif_metadata.read()

            media = _class(file_path)
            dest_path = filesystem.process_file(file_path, destination, media, move=True, allowDuplicate=True)
            print '%s ...' % dest_path,
            print 'OK'

            # If the folder we moved the file out of or its parent are empty we delete it.
            filesystem.delete_directory_if_empty(os.path.dirname(file_path))
            filesystem.delete_directory_if_empty(os.path.dirname(os.path.dirname(file_path)))

db = Db()
filesystem = FileSystem()
args = arguments.parse(sys.argv[1:], None, ['time=','location=','process='], './adjust.py --time=<string time> --location=<string location> --process=no file1 file2...fileN')
config = parse_arguments(args)

if __name__ == '__main__':
    main(config, sys.argv)
    sys.exit(0)
