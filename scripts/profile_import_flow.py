#!/usr/bin/env python

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time
from contextlib import ExitStack
from unittest import mock

from click.testing import CliRunner

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, os.path.join(REPO_ROOT, 'elodie', 'tests'))

import helper

from elodie import constants
from elodie.dependencies import get_exiftool
from elodie.external.pyexiftool import ExifTool
from elodie.media.base import Base


def load_elodie_module():
    elodie_path = os.path.join(REPO_ROOT, 'elodie.py')
    spec = importlib.util.spec_from_file_location('elodie_profile', elodie_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def timed_wrapper(stats, key, func):
    def wrapped(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            stats[key]['count'] += 1
            stats[key]['seconds'] += time.perf_counter() - start
    return wrapped


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--files', type=int, default=50, help='Number of files to import.')
    parser.add_argument(
        '--fixture',
        default='plain.jpg',
        help='Fixture file from elodie/tests/files to duplicate.',
    )
    args = parser.parse_args()

    stats = {
        'get_metadata': {'count': 0, 'seconds': 0.0},
        'get_metadata_batch': {'count': 0, 'seconds': 0.0},
        'get_tags_batch': {'count': 0, 'seconds': 0.0},
        'process_checksum': {'count': 0, 'seconds': 0.0},
        'place_name': {'count': 0, 'seconds': 0.0},
        'file_operation': {'count': 0, 'seconds': 0.0},
        'flush': {'count': 0, 'seconds': 0.0},
    }

    src_root = tempfile.mkdtemp(prefix='elodie-profile-src-')
    dst_root = tempfile.mkdtemp(prefix='elodie-profile-dst-')
    app_root = tempfile.mkdtemp(prefix='elodie-profile-app-')
    os.environ['ELODIE_APPLICATION_DIRECTORY'] = app_root

    elodie = load_elodie_module()

    exiftool_addedargs = [u'-config', u'"{}"'.format(constants.exiftool_config)]
    exiftool = ExifTool(executable_=get_exiftool(), addedargs=exiftool_addedargs)
    exiftool.start()

    paths = []
    for i in range(args.files):
        file_path = os.path.join(src_root, f'fixture-{i}{os.path.splitext(args.fixture)[1]}')
        shutil.copyfile(helper.get_file(args.fixture), file_path)
        paths.append(file_path)

    with ExitStack() as stack:
        stack.enter_context(mock.patch(
            'elodie.media.base.Base.get_metadata',
            timed_wrapper(stats, 'get_metadata', Base.get_metadata)
        ))
        stack.enter_context(mock.patch(
            'elodie.external.pyexiftool.ExifTool.get_metadata_batch',
            timed_wrapper(stats, 'get_metadata_batch', ExifTool.get_metadata_batch)
        ))
        stack.enter_context(mock.patch(
            'elodie.external.pyexiftool.ExifTool.get_tags_batch',
            timed_wrapper(stats, 'get_tags_batch', ExifTool.get_tags_batch)
        ))
        stack.enter_context(mock.patch(
            'elodie.filesystem.FileSystem.process_checksum',
            timed_wrapper(stats, 'process_checksum', elodie.FileSystem.process_checksum)
        ))
        stack.enter_context(mock.patch(
            'elodie.geolocation.place_name',
            timed_wrapper(stats, 'place_name', elodie.geolocation.place_name)
        ))
        stack.enter_context(mock.patch(
            'elodie.filesystem.FileSystem._file_operation',
            timed_wrapper(stats, 'file_operation', elodie.FileSystem._file_operation)
        ))
        stack.enter_context(mock.patch(
            'elodie.filesystem.FileSystem.flush',
            timed_wrapper(stats, 'flush', elodie.FileSystem.flush)
        ))

        runner = CliRunner()
        start = time.perf_counter()
        result = runner.invoke(elodie._import, ['--destination', dst_root, '--allow-duplicates', *paths])
        total = time.perf_counter() - start

    try:
        exiftool.terminate()
    except Exception:
        pass

    output = {
        'files': args.files,
        'fixture': args.fixture,
        'total_seconds': round(total, 4),
        'exit_code': result.exit_code,
        'timings': {
            key: {
                'count': value['count'],
                'seconds': round(value['seconds'], 4),
                'share_percent': round((value['seconds'] / total) * 100, 2) if total else 0.0,
            }
            for key, value in stats.items()
        },
    }
    print(json.dumps(output))

    shutil.rmtree(src_root)
    shutil.rmtree(dst_root)
    shutil.rmtree(app_root)


if __name__ == '__main__':
    main()
