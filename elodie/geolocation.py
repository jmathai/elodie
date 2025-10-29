"""Look up geolocation information for media objects."""
from __future__ import print_function
from __future__ import division

from os import path

import requests
import urllib.request
import urllib.parse
import urllib.error

from elodie.config import load_config
from elodie import constants
from elodie import log
from elodie.localstorage import Db

__KEY__ = None
__DEFAULT_LOCATION__ = 'Unknown Location'
__PREFER_ENGLISH_NAMES__ = None


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
    geolocation_info = lookup(location=name)

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
        float(degrees) + (float(minutes) / 60) +
        (float(seconds) / 3600)
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

    if constants.mapquest_key is not None:
        __KEY__ = constants.mapquest_key
        return __KEY__

    config = load_config()
    if('MapQuest' not in config):
        return None

    __KEY__ = config['MapQuest']['key']
    return __KEY__

def get_prefer_english_names():
    global __PREFER_ENGLISH_NAMES__
    if __PREFER_ENGLISH_NAMES__ is not None:
        return __PREFER_ENGLISH_NAMES__

    config_file = '%s/config.ini' % constants.application_directory()
    if not path.exists(config_file):
        return False

    config = load_config()
    if('MapQuest' not in config):
        return False

    if('prefer_english_names' not in config['MapQuest']):
        return False

    __PREFER_ENGLISH_NAMES__ = bool(config['MapQuest']['prefer_english_names'])
    return __PREFER_ENGLISH_NAMES__

def place_name(lat, lon):
    lookup_place_name_default = {'default': __DEFAULT_LOCATION__}
    if(lat is None or lon is None):
        return lookup_place_name_default

    # Convert lat/lon to floats
    if(not isinstance(lat, float)):
        lat = float(lat)
    if(not isinstance(lon, float)):
        lon = float(lon)

    # Try to get cached location first
    db = Db()
    # 3km distace radious for a match
    cached_place_name = db.get_location_name(lat, lon, 3000)
    # We check that it's a dict to coerce an upgrade of the location
    #  db from a string location to a dictionary. See gh-160.
    if(isinstance(cached_place_name, dict)):
        return cached_place_name

    lookup_place_name = {}
    geolocation_info = lookup(lat=lat, lon=lon)
    if(geolocation_info is not None and 'address' in geolocation_info):
        address = geolocation_info['address']
        # gh-386 adds support for town
        # taking precedence after city for backwards compatability
        for loc in ['city', 'town', 'state', 'country']:
            if(loc in address):
                lookup_place_name[loc] = address[loc]
                # In many cases the desired key is not available so we
                #  set the most specific as the default.
                if('default' not in lookup_place_name):
                    lookup_place_name['default'] = address[loc]

    if(lookup_place_name):
        db.add_location(lat, lon, lookup_place_name)
        # TODO: Maybe this should only be done on exit and not for every write.
        db.update_location_db()

    if('default' not in lookup_place_name):
        lookup_place_name = lookup_place_name_default

    return lookup_place_name


def lookup(**kwargs):
    if(
        'location' not in kwargs and
        'lat' not in kwargs and
        'lon' not in kwargs
    ):
        return None

    if('lat' in kwargs and 'lon' in kwargs):
        kwargs['location'] = '{},{}'.format(kwargs['lat'], kwargs['lon'])

    key = get_key()
    prefer_english_names = get_prefer_english_names()

    if(key is None):
        return None

    try:
        headers = {}
        params = {'format': 'json', 'key': key}
        if(prefer_english_names):
            headers = {'Accept-Language':'en-EN,en;q=0.8'}
            params['locale'] = 'en_US'
        params.update(kwargs)
        path = '/geocoding/v1/address'
        if('lat' in kwargs and 'lon' in kwargs):
            path = '/geocoding/v1/reverse'
        url = '%s%s?%s' % (
                    constants.mapquest_base_url,
                    path,
                    urllib.parse.urlencode(params)
              )
        # log the MapQuest url gh-446
        log.info('MapQuest url: %s' % (url))
        r = requests.get(url, headers=headers)
        return parse_result(r.json())
    except requests.exceptions.RequestException as e:
        log.error(e)
        return None
    except ValueError as e:
        log.error(r.text)
        log.error(e)
        return None


def parse_result(result):
    # gh-421
    # Return None if statusCode is not 0
    #   https://developer.mapquest.com/documentation/geocoding-api/status-codes/
    if( 'info' not in result or
        'statuscode' not in result['info'] or
        result['info']['statuscode'] != 0
       ):
        return None

    if( 'results' in result and
        len(result['results']) > 0 and
        'locations' in result['results'][0] and
        len(result['results'][0]['locations']) > 0 and
        # Return None if source is FALLBACK (invalid location)
        'source' in result['results'][0]['locations'][0] and
        result['results'][0]['locations'][0]['source'] == 'FALLBACK'
       ):
        return None

    address = parse_result_address(result)
    if(address is None):
        return None

    result['address'] = address
    result['latLng'] = parse_result_latlon(result)

    return result

def parse_result_address(result):
    # We want to store the city, state and country
    # The only way determined to identify an unfound address is 
    #   that none of the indicies were found
    if( 'results' not in result or
        len(result['results']) == 0 or
        'locations' not in result['results'][0] or
        len(result['results'][0]['locations']) == 0
        ):
        return None

    index_found = False
    addresses = {'city': None, 'state': None, 'country': None}
    result_compat = {}
    result_compat['address'] = {}


    locations = result['results'][0]['locations'][0]
    # We are looping over locations to find the adminAreaNType key which
    #   has a value of City, State or Country.
    # Once we find it then we obtain the value from the key adminAreaN
    #   where N is a numeric index.
    # For example
    #   * adminArea1Type = 'City'
    #   * adminArea1 = 'Sunnyvale'
    for key in locations:
        # Check if the key is of the form adminArea1Type
        if(key[-4:] == 'Type'):
            # If it's a type then check if it corresponds to one we are intereated in
            #   and store the index by parsing the key
            key_prefix = key[:-4]
            key_index = key[-5:-4]
            if(locations[key].lower() in addresses):
                addresses[locations[key].lower()] = locations[key_prefix]
                index_found = True

    if(index_found is False):
        return None

    return addresses

def parse_result_latlon(result):
    if( 'results' not in result or
        len(result['results']) == 0 or
        'locations' not in result['results'][0] or
        len(result['results'][0]['locations']) == 0 or
        'latLng' not in result['results'][0]['locations'][0]
        ):
        return None

    latLng = result['results'][0]['locations'][0]['latLng'];

    return {'lat': latLng['lat'], 'lon': latLng['lng']}
