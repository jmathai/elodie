"""
Methods for interacting with information Elodie caches about stored media.
"""
from builtins import map
from builtins import object

import hashlib
import json
import os
import sys

from math import ceil, radians, cos, sqrt
from shutil import copyfile
from time import strftime

from elodie import constants


class Db(object):

    """A class for interacting with the JSON files created by Elodie."""

    def __init__(self):
        # verify that the application directory (~/.elodie) exists,
        #   else create it
        if not os.path.exists(constants.application_directory()):
            os.makedirs(constants.application_directory())

        # If the hash db doesn't exist we create it.
        # Otherwise we only open for reading
        if not os.path.isfile(constants.hash_db()):
            with open(constants.hash_db(), 'a'):
                os.utime(constants.hash_db(), None)

        self.hash_db = {}

        # We know from above that this file exists so we open it
        #   for reading only.
        with open(constants.hash_db(), 'r') as f:
            try:
                self.hash_db = json.load(f)
            except ValueError:
                pass

        # If the location db doesn't exist we create it.
        # Otherwise we only open for reading
        if not os.path.isfile(constants.location_db()):
            with open(constants.location_db(), 'a'):
                os.utime(constants.location_db(), None)

        self.location_db = []

        # We know from above that this file exists so we open it
        #   for reading only.
        with open(constants.location_db(), 'r') as f:
            try:
                self.location_db = json.load(f)
            except ValueError:
                pass

        self.hash_db_dirty = False
        self.location_db_dirty = False
        self.location_grid_size = 0.01
        self._location_name_index = {}
        self._location_grid_index = {}
        self._location_distance_cache = {}
        self._rebuild_indexes()

    def _rebuild_indexes(self):
        self._location_name_index = {}
        self._location_grid_index = {}
        self._location_distance_cache = {}
        for data in self.location_db:
            if isinstance(data['name'], str):
                self._location_name_index[data['name']] = (data['lat'], data['long'])
            cell = self._location_grid_key(data['lat'], data['long'])
            if cell not in self._location_grid_index:
                self._location_grid_index[cell] = []
            self._location_grid_index[cell].append(data)

    def _location_grid_key(self, latitude, longitude):
        return (
            int(float(latitude) / self.location_grid_size),
            int(float(longitude) / self.location_grid_size),
        )

    def _distance_m(self, latitude, longitude, location):
        lon1, lat1, lon2, lat2 = list(map(
            radians,
            [longitude, latitude, location['long'], location['lat']]
        ))

        r = 6371000  # radius of the earth in m
        x = (lon2 - lon1) * cos(0.5 * (lat2 + lat1))
        y = lat2 - lat1
        return r * sqrt(x * x + y * y)

    def _location_candidates(self, latitude, longitude, threshold_m):
        lat = float(latitude)
        lon = float(longitude)
        lat_radius = threshold_m / 111320.0
        lon_scale = max(abs(cos(radians(lat))), 0.1)
        lon_radius = threshold_m / (111320.0 * lon_scale)
        radius = max(
            1,
            int(ceil(max(lat_radius, lon_radius) / self.location_grid_size))
        )
        center_lat, center_lon = self._location_grid_key(lat, lon)
        candidates = []
        for lat_offset in range(-radius, radius + 1):
            for lon_offset in range(-radius, radius + 1):
                cell = (center_lat + lat_offset, center_lon + lon_offset)
                if cell in self._location_grid_index:
                    candidates.extend(self._location_grid_index[cell])
        return candidates

    def add_hash(self, key, value, write=False):
        """Add a hash to the hash db.

        :param str key:
        :param str value:
        :param bool write: If true, write the hash db to disk.
        """
        self.hash_db[key] = value
        self.hash_db_dirty = True
        if(write is True):
            self.update_hash_db()

    # Location database
    # Currently quite simple just a list of long/lat pairs with a name
    # If it gets many entries a lookup might take too long and a better
    # structure might be needed. Some speed up ideas:
    # - Sort it and inter-half method can be used
    # - Use integer part of long or lat as key to get a lower search list
    # - Cache a small number of lookups, photos are likely to be taken in
    #   clusters around a spot during import.
    def add_location(self, latitude, longitude, place, write=False):
        """Add a location to the database.

        :param float latitude: Latitude of the location.
        :param float longitude: Longitude of the location.
        :param str place: Name for the location.
        :param bool write: If true, write the location db to disk.
        """
        data = {}
        data['lat'] = latitude
        data['long'] = longitude
        data['name'] = place
        self.location_db.append(data)
        self.location_db_dirty = True
        if isinstance(data['name'], str):
            self._location_name_index[data['name']] = (data['lat'], data['long'])
        cell = self._location_grid_key(data['lat'], data['long'])
        if cell not in self._location_grid_index:
            self._location_grid_index[cell] = []
        self._location_grid_index[cell].append(data)
        self._location_distance_cache = {}
        if(write is True):
            self.update_location_db()

    def backup_hash_db(self):
        """Backs up the hash db."""
        if os.path.isfile(constants.hash_db()):
            mask = strftime('%Y-%m-%d_%H-%M-%S')
            backup_file_name = '%s-%s' % (constants.hash_db(), mask)
            copyfile(constants.hash_db(), backup_file_name)
            return backup_file_name

    def check_hash(self, key):
        """Check whether a hash is present for the given key.

        :param str key:
        :returns: bool
        """
        return key in self.hash_db

    def checksum(self, file_path, blocksize=65536):
        """Create a hash value for the given file.

        See http://stackoverflow.com/a/3431835/1318758.

        :param str file_path: Path to the file to create a hash for.
        :param int blocksize: Read blocks of this size from the file when
            creating the hash.
        :returns: str or None
        """
        hasher = hashlib.sha256()
        with open(file_path, 'rb') as f:
            buf = f.read(blocksize)

            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(blocksize)
            return hasher.hexdigest()
        return None

    def get_hash(self, key):
        """Get the hash value for a given key.

        :param str key:
        :returns: str or None
        """
        if(self.check_hash(key) is True):
            return self.hash_db[key]
        return None

    def get_location_name(self, latitude, longitude, threshold_m):
        """Find a name for a location in the database.

        :param float latitude: Latitude of the location.
        :param float longitude: Longitude of the location.
        :param int threshold_m: Location in the database must be this close to
            the given latitude and longitude.
        :returns: str, or None if a matching location couldn't be found.
        """
        cache_key = (
            round(float(latitude), 4),
            round(float(longitude), 4),
            int(threshold_m),
        )
        if cache_key in self._location_distance_cache:
            return self._location_distance_cache[cache_key]

        last_d = sys.maxsize
        name = None
        candidates = self._location_candidates(latitude, longitude, threshold_m)
        for data in candidates:
            d = self._distance_m(latitude, longitude, data)
            # Use if closer then threshold_km reuse lookup
            if(d <= threshold_m and d < last_d):
                name = data['name']
                last_d = d

        self._location_distance_cache[cache_key] = name
        return name

    def get_location_coordinates(self, name):
        """Get the latitude and longitude for a location.

        :param str name: Name of the location.
        :returns: tuple(float), or None if the location wasn't in the database.
        """
        return self._location_name_index.get(name)

    def all(self):
        """Generator to get all entries from self.hash_db

        :returns tuple(string)
        """
        for checksum, path in self.hash_db.items():
            yield (checksum, path)

    def reset_hash_db(self):
        self.hash_db = {}
        self.hash_db_dirty = True

    def update_hash_db(self):
        """Write the hash db to disk."""
        if constants.dry_run:
            print(f"[DRY-RUN] Would update hash database with {len(self.hash_db)} entries")
            return
        with open(constants.hash_db(), 'w') as f:
            json.dump(self.hash_db, f)
        self.hash_db_dirty = False

    def update_location_db(self):
        """Write the location db to disk."""
        if constants.dry_run:
            print(f"[DRY-RUN] Would update location database with {len(self.location_db)} entries")
            return
        with open(constants.location_db(), 'w') as f:
            json.dump(self.location_db, f)
        self.location_db_dirty = False

    def flush(self):
        if self.hash_db_dirty:
            self.update_hash_db()
        if self.location_db_dirty:
            self.update_location_db()
