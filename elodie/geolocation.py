"""Look up geolocation information for media objects."""

from os import path
from ConfigParser import ConfigParser
import fractions
import pyexiv2

import requests
import urllib

from elodie import constants
from elodie.localstorage import Db


class Fraction(fractions.Fraction):

    """Only create Fractions from floats.

    Should be compatible with Python 2.6, though untested.

    >>> Fraction(0.3)
    Fraction(3, 10)
    >>> Fraction(1.1)
    Fraction(11, 10)
    """

    def __new__(cls, value, ignore=None):
        return fractions.Fraction.from_float(value).limit_denominator(99999)


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


def decimal_to_dms(decimal, signed=True):
    # if decimal is negative we need to make the degrees and minutes
    #   negative also
    sign = 1
    if(decimal < 0):
        sign = -1

    # http://anothergisblog.blogspot.com/2011/11/convert-decimal-degree-to-degrees.html # noqa
    degrees = int(decimal)
    subminutes = abs((decimal - int(decimal)) * 60)
    minutes = int(subminutes) * sign
    subseconds = abs((subminutes - int(subminutes)) * 60) * sign
    subseconds_fraction = Fraction(subseconds)

    if(signed is False):
        degrees = abs(degrees)
        minutes = abs(minutes)
        subseconds_fraction = Fraction(abs(subseconds))

    return (
        pyexiv2.Rational(degrees, 1),
        pyexiv2.Rational(minutes, 1),
        pyexiv2.Rational(
            subseconds_fraction.numerator,
            subseconds_fraction.denominator
        )
    )


def dms_to_decimal(degrees, minutes, seconds, direction=' '):
    sign = 1
    if(direction[0] in 'WSws'):
        sign = -1
    return (
        float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    ) * sign


def get_key():
    config_file = '%s/config.ini' % constants.application_directory
    if not path.exists(config_file):
        return None

    config = ConfigParser()
    config.read(config_file)
    if('MapQuest' not in config.sections()):
        return None

    return config.get('MapQuest', 'key')


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
            urllib.urlencode(params), headers=headers
        )
        return r.json()
    except requests.exceptions.RequestException as e:
        if(constants.debug is True):
            print e
        return None
    except ValueError as e:
        if(constants.debug is True):
            print r.text
            print e
        return None


def lookup(name):
    if(name is None or len(name) == 0):
        return None

    key = get_key()

    try:
        params = {'format': 'json', 'key': key, 'location': name}
        if(constants.debug is True):
            print 'http://open.mapquestapi.com/geocoding/v1/address?%s' % urllib.urlencode(params)  # noqa
        r = requests.get(
            'http://open.mapquestapi.com/geocoding/v1/address?%s' %
            urllib.urlencode(params)
        )
        return r.json()
    except requests.exceptions.RequestException as e:
        if(constants.debug is True):
            print e
        return None
    except ValueError as e:
        if(constants.debug is True):
            print r.text
            print e
        return None
