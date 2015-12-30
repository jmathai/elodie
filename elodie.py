#!/usr/bin/env python

import os
import re
import sys

from datetime import datetime
from docopt import docopt

from elodie import constants
from elodie import geolocation
from elodie.media.photo import Media
from elodie.media.photo import Photo
from elodie.media.video import Video
from elodie.filesystem import FileSystem
from elodie.localstorage import Db


def usage():
    return """Usage: elodie.py import --source=<s> --destination=<d> [--album-from-folder]
       elodie.py import --file=<f> --destination=<d> [--album-from-folder]
       elodie.py update [--time=<t>] [--location=<l>] [--album=<a>] [--title=<t>] INPUT ...

       -h --help    show this
       """


def import_file(_file, destination):
    media = Media.get_class_by_file(_file, (Photo, Video))
    if not media:
        if constants.debug:
            print 'Not a supported file (%s)' % _file
        print '{"source":"%s", "error_msg":"Not a supported file"}' % _file
        return

    if media.__name__ == 'Video':
        filesystem.set_date_from_path_video(media)

    if params['--album-from-folder']:
        media.set_album_from_folder()

    dest_path = filesystem.process_file(_file, destination,
        media, allowDuplicate=False, move=False)
    if dest_path:
        print '%s -> %s' % (_file, dest_path)


def _import(params):
    destination = os.path.expanduser(params['--destination'])

    if params['--source']:
        source = os.path.expanduser(params['--source'])
        files = filesystem.get_all_files(source, None)
    elif params['--file']:
        files = [os.path.expanduser(params['--file'])]

    for current_file in files:
        import_file(current_file, destination)


def _update(params):
    location_coords = None
    for file_path in params['INPUT']:
        if not os.path.exists(file_path):
            if constants.debug:
                print 'Could not find %s' % file_path
            print '{"source":"%s", "error_msg":"Could not find %s"}' % \
                (file_path, file_path)
            continue

        file_path = os.path.expanduser(file_path)
        destination = os.path.expanduser(os.path.dirname(os.path.dirname(
                                         os.path.dirname(file_path))))

        media = Media.get_class_by_file(file_path, (Photo, Video))
        if not media:
            continue

        updated = False
        if params['--location']:
            if not location_coords:
                location_coords = geolocation.coordinates_by_name(
                    params['--location'])

            if location_coords and 'latitude' in location_coords and \
                    'longitude' in location_coords:
                location_status = media.set_location(location_coords[
                    'latitude'], location_coords['longitude'])
                if not location_status:
                    if constants.debug:
                        print 'Failed to update location'
                    print '{"source":"%s","error_msg":"Failed to update location"}' % file_path
                    sys.exit(1)
                updated = True

        if params['--time']:
            time_string = params['--time']
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
                media.set_date_taken(time)
                updated = True

        if params['--album']:
            media.set_album(params['--album'])
            updated = True

        # Updating a title can be problematic when doing it 2+ times on a file.
        # You would end up with img_001.jpg -> img_001-first-title.jpg ->
        # img_001-first-title-second-title.jpg.
        # To resolve that we have to track the prior title (if there was one.
        # Then we massage the updated_media's metadata['base_name'] to remove
        # the old title.
        # Since FileSystem.get_file_name() relies on base_name it will properly
        #  rename the file by updating the title instead of appending it.
        remove_old_title_from_name = False
        if params['--title']:
            # We call get_metadata() to cache it before making any changes
            metadata = media.get_metadata()
            title_update_status = media.set_title(params['--title'])
            original_title = metadata['title']
            if title_update_status and original_title:
                # @TODO: We should move this to a shared method since FileSystem.get_file_name() does it too.
                original_title = re.sub('\W+', '-', original_title.lower())
                original_base_name = metadata['base_name']
                remove_old_title_from_name = True
            updated = True

        if updated:
            updated_media = Media.get_class_by_file(file_path, (Photo, Video))
            # See comments above on why we have to do this when titles get updated.
            if remove_old_title_from_name and len(original_title) > 0:
                updated_media.get_metadata()
                updated_media.set_metadata_basename(
                    original_base_name.replace('-%s' % original_title, ''))

            dest_path = filesystem.process_file(file_path, destination,
                updated_media, move=True, allowDuplicate=True)
            if constants.debug:
            print '{"source":"%s", "destination":"%s"}' % (file_path, dest_path)
            # If the folder we moved the file out of or its parent are empty we delete it.
            filesystem.delete_directory_if_empty(os.path.dirname(file_path))
            filesystem.delete_directory_if_empty(os.path.dirname(os.path.dirname(file_path)))


db = Db()
filesystem = FileSystem()

if __name__ == '__main__':
    params = docopt(usage())
    if(params['import'] == True):
        _import(params)
    elif(params['update'] == True):
        _update(params)
    sys.exit(0)
