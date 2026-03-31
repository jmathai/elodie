#!/usr/bin/env python

import argparse
import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from elodie.localstorage import Db


def benchmark_hash_writes(entries):
    tmpdir = tempfile.mkdtemp(prefix='elodie-bench-current-')
    os.environ['ELODIE_APPLICATION_DIRECTORY'] = tmpdir
    start = time.perf_counter()
    for i in range(entries):
        db = Db()
        db.add_hash(f'k{i}', f'v{i}')
        db.update_hash_db()
    current = time.perf_counter() - start

    tmpdir = tempfile.mkdtemp(prefix='elodie-bench-batched-')
    os.environ['ELODIE_APPLICATION_DIRECTORY'] = tmpdir
    start = time.perf_counter()
    db = Db()
    for i in range(entries):
        db.add_hash(f'k{i}', f'v{i}')
    db.flush()
    batched = time.perf_counter() - start

    return {
        'benchmark': 'hash_writes',
        'entries': entries,
        'current_seconds': round(current, 4),
        'batched_seconds': round(batched, 4),
        'speedup_x': round(current / batched, 2) if batched else None,
    }


def benchmark_location_lookup(entries, lookups=500):
    tmpdir = tempfile.mkdtemp(prefix='elodie-bench-location-')
    os.environ['ELODIE_APPLICATION_DIRECTORY'] = tmpdir
    db = Db()
    for i in range(entries):
        db.add_location(37.0 + i * 0.0001, -122.0 - i * 0.0001, f'p{i}')

    coords = [
        (37.0 + ((i * 17) % entries) * 0.0001, -122.0 - ((i * 17) % entries) * 0.0001)
        for i in range(lookups)
    ]

    start = time.perf_counter()
    for lat, lon in coords:
        best_name = None
        best_distance = None
        for data in db.location_db:
            distance = db._distance_m(lat, lon, data)
            if distance <= 3000 and (best_distance is None or distance < best_distance):
                best_name = data['name']
                best_distance = distance
    linear = time.perf_counter() - start

    start = time.perf_counter()
    for lat, lon in coords:
        db.get_location_name(lat, lon, 3000)
    indexed = time.perf_counter() - start

    return {
        'benchmark': 'location_lookup',
        'entries': entries,
        'lookups': lookups,
        'linear_seconds': round(linear, 4),
        'indexed_seconds': round(indexed, 4),
        'speedup_x': round(linear / indexed, 2) if indexed else None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--entries',
        type=int,
        nargs='+',
        default=[100, 1000, 3000],
        help='Number of hash entries to benchmark.',
    )
    parser.add_argument(
        '--lookups',
        type=int,
        default=500,
        help='Number of location lookups to benchmark.',
    )
    args = parser.parse_args()

    for entries in args.entries:
        print(json.dumps(benchmark_hash_writes(entries)))
        print(json.dumps(benchmark_location_lookup(entries, args.lookups)))


if __name__ == '__main__':
    main()
