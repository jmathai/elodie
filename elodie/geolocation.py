"""Look up geolocation information for media objects."""
from __future__ import print_function
from __future__ import division
from future import standard_library
from past.utils import old_div

from os import path
from configparser import ConfigParser

standard_library.install_aliases()  # noqa

import requests
import urllib.request
import urllib.parse
import urllib.error

from elodie import constants
from elodie.localstorage import Db

__KEY__ = None


def coordinates_by_name(name):
    # Try to get cached location first
    db = Db()
    cached_coordinates = db.get_location_coordinates(name)
    if(cached_coordinates is not None):
        return {
            'latitude': cached_coordinates[0],
            'longitude': cached_coordinates[1]
        }

    # If the name is not cached then we go ahead with an API lookup
    geolocation_info = lookup(name)

    if(geolocation_info is not None):
        if(
            'results' in geolocation_info and
            len(geolocation_info['results']) != 0 and
            'locations' in geolocation_info['results'][0] and
            len(geolocation_info['results'][0]['locations']) != 0
        ):

            # By default we use the first entry unless we find one with
            #   geocodeQuality=city.
            geolocation_result = geolocation_info['results'][0]
            use_location = geolocation_result['locations'][0]['latLng']
            # Loop over the locations to see if we come accross a
            #   geocodeQuality=city.
            # If we find a city we set that to the use_location and break
            for location in geolocation_result['locations']:
                if(
                    'latLng' in location and
                    'lat' in location['latLng'] and
                    'lng' in location['latLng'] and
                    location['geocodeQuality'].lower() == 'city'
                ):
                    use_location = location['latLng']
                    break

            return {
                'latitude': use_location['lat'],
                'longitude': use_location['lng']
            }

    return None


def decimal_to_dms(decimal):
    decimal = float(decimal)
    decimal_abs = abs(decimal)
    minutes, seconds = divmod(decimal_abs*3600, 60)
    degrees, minutes = divmod(minutes, 60)
    degrees = degrees
    sign = 1 if decimal >= 0 else -1
    return (degrees, minutes, seconds, sign)


def dms_to_decimal(degrees, minutes, seconds, direction=' '):
    sign = 1
    if(direction[0] in 'WSws'):
        sign = -1
    return (
        float(degrees) + old_div(float(minutes), 60) +
        old_div(float(seconds), 3600)
    ) * sign


def dms_string(decimal, type='latitude'):
    # Example string -> 38 deg 14' 27.82" S
    dms = decimal_to_dms(decimal)
    if type == 'latitude':
        direction = 'N' if decimal >= 0 else 'S'
    elif type == 'longitude':
        direction = 'E' if decimal >= 0 else 'W'
    return '{} deg {}\' {}" {}'.format(dms[0], dms[1], dms[2], direction)


def get_key():
    global __KEY__
    if __KEY__ is not None:
        return __KEY__

    config_file = '%s/config.ini' % constants.application_directory
    if not path.exists(config_file):
        return None

    config = ConfigParser()
    config.read(config_file)
    if('MapQuest' not in config.sections()):
        return None

    __KEY__ = config.get('MapQuest', 'key')
    return __KEY__


def place_name(lat, lon):
    # Convert lat/lon to floats
    if not isinstance(lat, float):
        lat = float(lat)
    if not isinstance(lon, float):
        lon = float(lon)

    # Try to get cached location first
    db = Db()
    # 3km distace radious for a match
    cached_place_name = db.get_location_name(lat, lon, 3000)
    if(cached_place_name is not None):
        return cached_place_name

    lookup_place_name = None
    geolocation_info = reverse_lookup(lat, lon)
    if(geolocation_info is not None):
        if('address' in geolocation_info):
            address = geolocation_info['address']
            if('city' in address):
                lookup_place_name = address['city']
            elif('state' in address):
                lookup_place_name = address['state']
            elif('country' in address):
                lookup_place_name = address['country']

    if(lookup_place_name is not None):
        db.add_location(lat, lon, lookup_place_name)
        # TODO: Maybe this should only be done on exit and not for every write.
        db.update_location_db()
    return lookup_place_name


def reverse_lookup(lat, lon):
    if(lat is None or lon is None):
        return None

    key = get_key()

    try:
        params = {'format': 'json', 'key': key, 'lat': lat, 'lon': lon}
        headers = {"Accept-Language": constants.accepted_language}
        r = requests.get(
            'http://open.mapquestapi.com/nominatim/v1/reverse.php?%s' %
            urllib.parse.urlencode(params), headers=headers
        )
        return r.json()
    except requests.exceptions.RequestException as e:
        if(constants.debug is True):
            print(e)
        return None
    except ValueError as e:
        if(constants.debug is True):
            print(r.text)
            print(e)
        return None


def lookup(name):
    if(name is None or len(name) == 0):
        return None

    key = get_key()

    try:
        params = {'format': 'json', 'key': key, 'location': name}
        if(constants.debug is True):
            print('http://open.mapquestapi.com/geocoding/v1/address?%s' % urllib.parse.urlencode(params))  # noqa
        r = requests.get(
            'http://open.mapquestapi.com/geocoding/v1/address?%s' %
            urllib.parse.urlencode(params)
        )
        return r.json()
    except requests.exceptions.RequestException as e:
        if(constants.debug is True):
            print(e)
        return None
    except ValueError as e:
        if(constants.debug is True):
            print(r.text)
            print(e)
        return None
