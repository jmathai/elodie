import hashlib
import json
from math import radians, cos, sqrt
import os
import sys

from elodie import constants

class Db(object):
    def __init__(self):
        # verify that the application directory (~/.elodie) exists, else create it
        if not os.path.exists(constants.application_directory):
            os.makedirs(constants.application_directory)

        # If the hash db doesn't exist we create it.
        # Otherwise we only open for reading
        if not os.path.isfile(constants.hash_db):
            with open(constants.hash_db, 'a'):
                os.utime(constants.hash_db, None)

        self.hash_db = {}

        # We know from above that this file exists so we open it for reading only.
        with open(constants.hash_db, 'r') as f:
            try:
                self.hash_db = json.load(f)
            except ValueError:
                pass

        # If the location db doesn't exist we create it.
        # Otherwise we only open for reading
        if not os.path.isfile(constants.location_db):
            with open(constants.location_db, 'a'):
                os.utime(constants.location_db, None)

        self.location_db = []

        # We know from above that this file exists so we open it for reading only.
        with open(constants.location_db, 'r') as f:
            try:
                self.location_db = json.load(f)
            except ValueError:
                pass

    def add_hash(self, key, value, write=False):
        self.hash_db[key] = value
        if(write == True):
            self.update_hash_db()

    def check_hash(self, key):
        return key in self.hash_db

    def get_hash(self, key):
        if(self.check_hash(key) == True):
            return self.hash_db[key]
        return None

    def update_hash_db(self):
        with open(constants.hash_db, 'w') as f:
            json.dump(self.hash_db, f)

    """
    http://stackoverflow.com/a/3431835/1318758
    """
    def checksum(self, file_path, blocksize=65536):
        hasher = hashlib.sha256()
        with open(file_path, 'r') as f:
            buf = f.read(blocksize)

            while len(buf) > 0:
                hasher.update(buf)
                buf = f.read(blocksize)
            return hasher.hexdigest()
        return None

    # Location database
    # Currently quite simple just a list of long/lat pairs with a name
    # If it gets many entryes a lookup might takt to long and a better
    # structure might be needed. Some speed up ideas:
    # - Sort it and inter-half method can be used
    # - Use integer part of long or lat as key to get a lower search list
    # - Cache a smal number of lookups, photos is likey to be taken i clusters
    #   around a spot during import.

    def add_location(self, latitude, longitude, place, write=False):
        data = {}
        data['lat'] = latitude
        data['long'] = longitude
        data['name'] = place
        self.location_db.append(data)
        if(write == True):
            self.update_location_db()

    def get_location_name(self, latitude, longitude,threshold_m):
        last_d = sys.maxint
        name = None
        for data in self.location_db:
            # As threshold is quite smal use simple math
            # From http://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
            # convert decimal degrees to radians

            lon1, lat1, lon2, lat2 = map(radians, [longitude, latitude, data['long'], data['lat']])

            R = 6371000  # radius of the earth in m
            x = (lon2 - lon1) * cos( 0.5*(lat2+lat1) )
            y = lat2 - lat1
            d = R * sqrt( x*x + y*y )
            # Use if closer then threshold_km reuse lookup
            if(d <= threshold_m and d < last_d):
                #print "Found in cached location dist: %d m" % d
                name = data['name'];
            last_d = d

        return name

    def get_location_coordinates(self, name):
        for data in self.location_db:
            if data['name'] == name:
                return (data['lat'], data['long'])

        return None

    def update_location_db(self):
        with open(constants.location_db, 'w') as f:
            json.dump(self.location_db, f)
