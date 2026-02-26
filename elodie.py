#!/usr/bin/env python

from __future__ import print_function
import os
import re
import signal
import sys
from datetime import datetime

import click
from send2trash import send2trash

# Verify that external dependencies are present first, so the user gets a
# more user-friendly error instead of an ImportError traceback.
from elodie.dependencies import verify_dependencies
if not verify_dependencies():
    sys.exit(1)

from elodie import constants
from elodie import geolocation
from elodie import log
from elodie.compatability import _decode
from elodie.config import load_config
from elodie.filesystem import FileSystem
from elodie.localstorage import Db
from elodie.media.base import Base, get_all_subclasses
from elodie.media.media import Media
from elodie.media.text import Text
from elodie.media.audio import Audio
from elodie.media.photo import Photo
from elodie.media.video import Video
from elodie.plugins.plugins import Plugins
from elodie.result import Result
from elodie.external.pyexiftool import ExifTool
from elodie.dependencies import get_exiftool
from elodie import constants

FILESYSTEM = FileSystem()


class _GracefulInterruptHandler(object):
    """Track SIGINT requests so commands can stop cleanly between files."""

    def __init__(self):
        self.interrupted = False
        self._previous_sigint_handler = None

    def __enter__(self):
        self._previous_sigint_handler = signal.getsignal(signal.SIGINT)
        signal.signal(signal.SIGINT, self._handle_interrupt)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        signal.signal(signal.SIGINT, self._previous_sigint_handler)
        return False

    def _handle_interrupt(self, signum, frame):
        if not self.interrupted:
            log.warn('Interrupt requested. Finishing current file before stopping.')
        self.interrupted = True

def import_file(_file, destination, album_from_folder, trash, allow_duplicates,
                location=None, time=None, db=None, write_db=True):
    
    _file = _decode(_file)
    destination = _decode(destination)

    """Set file metadata and move it to destination.
    """
    if not os.path.exists(_file):
        log.warn('Could not find %s' % _file)
        log.all('{"source":"%s", "error_msg":"Could not find %s"}' %
                  (_file, _file))
        return
    # Check if the source, _file, is a child folder within destination
    elif destination.startswith(os.path.abspath(os.path.dirname(_file))+os.sep):
        log.all('{"source": "%s", "destination": "%s", "error_msg": "Source cannot be in destination"}' % (
            _file, destination))
        return


    media = Media.get_class_by_file(_file, get_all_subclasses())
    if not media:
        log.warn('Not a supported file (%s)' % _file)
        log.all('{"source":"%s", "error_msg":"Not a supported file"}' % _file)
        return

    if album_from_folder:
        media.set_album_from_folder()

    # Apply location and time updates if provided
    if location:
        update_location(media, _file, location)
    if time:
        update_time(media, _file, time)

    dest_path = FILESYSTEM.process_file(
        _file,
        destination,
        media,
        allowDuplicate=allow_duplicates,
        move=False,
        db=db,
        write_db=write_db,
    )
    if dest_path:
        log.all('%s -> %s' % (_file, dest_path))
    if trash:
        if constants.dry_run:
            print(f"[DRY-RUN] Would move to trash: {_file}")
        else:
            send2trash(_file)

    return dest_path or None

@click.command('batch')
@click.option('--debug', default=False, is_flag=True,
              help='Show more verbose debug output.')
@click.option('--dry-run', default=False, is_flag=True,
              help='Show what would be done without making any changes.')
def _batch(debug, dry_run):
    """Run batch() for all plugins.
    """
    constants.debug = debug
    constants.dry_run = dry_run
    plugins = Plugins()
    plugins.run_batch()
       

@click.command('import')
@click.option('--destination', type=click.Path(file_okay=False),
              required=True, help='Copy imported files into this directory.')
@click.option('--source', type=click.Path(file_okay=False),
              help='Import files from this directory, if specified.')
@click.option('--file', type=click.Path(dir_okay=False),
              help='Import this file, if specified.')
@click.option('--album-from-folder', default=False, is_flag=True,
              help="Use images' folders as their album names.")
@click.option('--trash', default=False, is_flag=True,
              help='After copying files, move the old files to the trash.')
@click.option('--allow-duplicates', default=False, is_flag=True,
              help='Import the file even if it\'s already been imported.')
@click.option('--location', help=('Update the image location. Location '
                                  'should be the name of a place, like "Las '
                                  'Vegas, NV".'))
@click.option('--time', help=('Update the image time. Time should be in '
                              'YYYY-mm-dd hh:ii:ss or YYYY-mm-dd format.'))
@click.option('--debug', default=False, is_flag=True,
              help='Show more verbose debug output.')
@click.option('--dry-run', default=False, is_flag=True,
              help='Show what would be done without making any changes.')
@click.option('--exclude-regex', default=set(), multiple=True,
              help='Regular expression for directories or files to exclude.')
@click.option('--hash-db-batch-size', default=1, show_default=True,
              type=click.IntRange(min=1),
              help='Flush hash DB every N successful imports. 1 keeps current behavior.')
@click.argument('paths', nargs=-1, type=click.Path())
def _import(destination, source, file, album_from_folder, trash, allow_duplicates, location, time, debug, dry_run, exclude_regex, hash_db_batch_size, paths):
    """Import files or directories by reading their EXIF and organizing them accordingly.
    """
    constants.debug = debug
    constants.dry_run = dry_run
    has_errors = False
    interrupted = False
    result = Result()

    destination = _decode(destination)
    destination = os.path.abspath(os.path.expanduser(destination))

    files = set()
    paths = set(paths)
    if source:
        source = _decode(source)
        paths.add(source)
    if file:
        paths.add(file)

    # if no exclude list was passed in we check if there's a config
    if len(exclude_regex) == 0:
        config = load_config()
        if 'Exclusions' in config:
            exclude_regex = [value for key, value in config.items('Exclusions')]

    exclude_regex_list = set(exclude_regex)
    use_hash_db_batching = hash_db_batch_size > 1
    hash_db_pending_flush_count = 0
    hash_db = Db() if use_hash_db_batching else None

    for path in paths:
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            files.update(FILESYSTEM.get_all_files(path, None, exclude_regex_list))
        else:
            if not FILESYSTEM.should_exclude(path, exclude_regex_list, True):
                files.add(path)

    with _GracefulInterruptHandler() as interrupt_handler:
        for current_file in files:
            if interrupt_handler.interrupted:
                interrupted = True
                break

            dest_path = import_file(current_file, destination, album_from_folder,
                        trash, allow_duplicates, location, time,
                        db=hash_db, write_db=not use_hash_db_batching)
            if dest_path:
                result.append((current_file, True))
                if use_hash_db_batching:
                    hash_db_pending_flush_count += 1
                    if hash_db_pending_flush_count >= hash_db_batch_size:
                        hash_db.update_hash_db()
                        hash_db_pending_flush_count = 0
            elif not allow_duplicates:
                result.append((current_file, None))  # duplicate
            else:
                result.append((current_file, False))  # error
            has_errors = has_errors is True or not dest_path

    if use_hash_db_batching and hash_db_pending_flush_count > 0:
        hash_db.update_hash_db()

    result.write()

    if interrupted:
        sys.exit(130)

    if has_errors:
        sys.exit(1)


@click.command('generate-db')
@click.option('--source', type=click.Path(file_okay=False),
              required=True, help='Source of your photo library.')
@click.option('--debug', default=False, is_flag=True,
              help='Show more verbose debug output.')
def _generate_db(source, debug):
    """Regenerate the hash.json database which contains all of the sha256 signatures of media files. The hash.json file is located at ~/.elodie/.
    """
    constants.debug = debug
    interrupted = False
    result = Result()
    source = os.path.abspath(os.path.expanduser(source))

    if not os.path.isdir(source):
        log.error('Source is not a valid directory %s' % source)
        sys.exit(1)
        
    db = Db()
    db.backup_hash_db()
    db.reset_hash_db()

    with _GracefulInterruptHandler() as interrupt_handler:
        for current_file in FILESYSTEM.get_all_files(source):
            if interrupt_handler.interrupted:
                interrupted = True
                break
            result.append((current_file, True))
            db.add_hash(db.checksum(current_file), current_file)
            log.progress()
    
    db.update_hash_db()
    log.progress('', True)
    result.write()

    if interrupted:
        sys.exit(130)

@click.command('verify')
@click.option('--debug', default=False, is_flag=True,
              help='Show more verbose debug output.')
def _verify(debug):
    constants.debug = debug
    interrupted = False
    result = Result()
    db = Db()
    with _GracefulInterruptHandler() as interrupt_handler:
        for checksum, file_path in db.all():
            if interrupt_handler.interrupted:
                interrupted = True
                break

            if not os.path.isfile(file_path):
                result.append((file_path, False))
                log.progress('f')
                continue

            actual_checksum = db.checksum(file_path)
            if checksum == actual_checksum:
                result.append((file_path, True))
                log.progress()
            else:
                result.append((file_path, False))
                log.progress('c')

    log.progress('', True)
    result.write()

    if interrupted:
        sys.exit(130)


def update_location(media, file_path, location_name):
    """Update location exif metadata of media.
    """
    location_coords = geolocation.coordinates_by_name(location_name)

    if location_coords and 'latitude' in location_coords and \
            'longitude' in location_coords:
        location_status = media.set_location(location_coords[
            'latitude'], location_coords['longitude'])
        if not location_status:
            log.error('Failed to update location')
            log.all(('{"source":"%s",' % file_path,
                       '"error_msg":"Failed to update location"}'))
            sys.exit(1)
    return True


def update_time(media, file_path, time_string):
    """Update time exif metadata of media.
    """
    time_format = '%Y-%m-%d %H:%M:%S'
    if re.match(r'^\d{4}-\d{2}-\d{2}$', time_string):
        time_string = '%s 00:00:00' % time_string
    elif re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}\d{2}$', time_string):
        msg = ('Invalid time format. Use YYYY-mm-dd hh:ii:ss or YYYY-mm-dd')
        log.error(msg)
        log.all('{"source":"%s", "error_msg":"%s"}' % (file_path, msg))
        sys.exit(1)

    time = datetime.strptime(time_string, time_format)
    media.set_date_taken(time)
    return True


@click.command('update')
@click.option('--album', help='Update the image album.')
@click.option('--location', help=('Update the image location. Location '
                                  'should be the name of a place, like "Las '
                                  'Vegas, NV".'))
@click.option('--time', help=('Update the image time. Time should be in '
                              'YYYY-mm-dd hh:ii:ss or YYYY-mm-dd format.'))
@click.option('--title', help='Update the image title.')
@click.option('--debug', default=False, is_flag=True,
              help='Show more verbose debug output.')
@click.option('--dry-run', default=False, is_flag=True,
              help='Show what would be done without making any changes.')
@click.argument('paths', nargs=-1,
                required=True)
def _update(album, location, time, title, paths, debug, dry_run):
    """Update a file's EXIF. Automatically modifies the file's location and file name accordingly.
    """
    constants.debug = debug
    constants.dry_run = dry_run
    has_errors = False
    interrupted = False
    result = Result()

    files = set()
    for path in paths:
        path = os.path.expanduser(path)
        if os.path.isdir(path):
            files.update(FILESYSTEM.get_all_files(path, None))
        else:
            files.add(path)

    with _GracefulInterruptHandler() as interrupt_handler:
        for current_file in files:
            if interrupt_handler.interrupted:
                interrupted = True
                break

            if not os.path.exists(current_file):
                has_errors = True
                result.append((current_file, False))
                log.warn('Could not find %s' % current_file)
                log.all('{"source":"%s", "error_msg":"Could not find %s"}' %
                          (current_file, current_file))
                continue

            current_file = os.path.expanduser(current_file)

            # The destination folder structure could contain any number of levels
            #  So we calculate that and traverse up the tree.
            # '/path/to/file/photo.jpg' -> '/path/to/file' ->
            #  ['path','to','file'] -> ['path','to'] -> '/path/to'
            current_directory = os.path.dirname(current_file)
            destination_depth = -1 * len(FILESYSTEM.get_folder_path_definition())
            destination = os.sep.join(
                              os.path.normpath(
                                  current_directory
                              ).split(os.sep)[:destination_depth]
                          )

            media = Media.get_class_by_file(current_file, get_all_subclasses())
            if not media:
                continue

            updated = False
            if location:
                update_location(media, current_file, location)
                updated = True
            if time:
                update_time(media, current_file, time)
                updated = True
            if album:
                media.set_album(album)
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
            if title:
                # We call get_metadata() to cache it before making any changes
                metadata = media.get_metadata()
                title_update_status = media.set_title(title)
                original_title = metadata['title']
                if title_update_status and original_title:
                    # @TODO: We should move this to a shared method since
                    # FileSystem.get_file_name() does it too.
                    original_title = re.sub(r'\W+', '-', original_title.lower())
                    original_base_name = metadata['base_name']
                    remove_old_title_from_name = True
                updated = True

            if updated:
                updated_media = Media.get_class_by_file(current_file,
                                                        get_all_subclasses())
                # See comments above on why we have to do this when titles
                # get updated.
                if remove_old_title_from_name and len(original_title) > 0:
                    updated_media.get_metadata()
                    updated_media.set_metadata_basename(
                        original_base_name.replace('-%s' % original_title, ''))

                dest_path = FILESYSTEM.process_file(current_file, destination,
                    updated_media, move=True, allowDuplicate=True)
                log.info(u'%s -> %s' % (current_file, dest_path))
                log.all('{"source":"%s", "destination":"%s"}' % (current_file,
                                                                   dest_path))
                # If the folder we moved the file out of or its parent are empty
                # we delete it.
                FILESYSTEM.delete_directory_if_empty(os.path.dirname(current_file))
                FILESYSTEM.delete_directory_if_empty(
                    os.path.dirname(os.path.dirname(current_file)))
                result.append((current_file, bool(dest_path)))
                # Trip has_errors to False if it's already False or dest_path is.
                has_errors = has_errors is True or not dest_path
            else:
                has_errors = False
                result.append((current_file, False))

    result.write()

    if interrupted:
        sys.exit(130)
    
    if has_errors:
        sys.exit(1)


@click.group()
def main():
    pass


main.add_command(_import)
main.add_command(_update)
main.add_command(_generate_db)
main.add_command(_verify)
main.add_command(_batch)


if __name__ == '__main__':
    #Initialize ExifTool Subprocess
    exiftool_addedargs = [
       u'-config',
        u'"{}"'.format(constants.exiftool_config)
    ]
    with ExifTool(executable_=get_exiftool(), addedargs=exiftool_addedargs) as et:
        main()
