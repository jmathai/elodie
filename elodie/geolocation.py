from os import path
from ConfigParser import ConfigParser
import fractions
import pyexiv2

import math
import requests
import sys
import urllib

from elodie import constants

class Fraction(fractions.Fraction):
    """Only create Fractions from floats.

    >>> Fraction(0.3)
    Fraction(3, 10)
    >>> Fraction(1.1)
    Fraction(11, 10)
    """

    def __new__(cls, value, ignore=None):
        """Should be compatible with Python 2.6, though untested."""
        return fractions.Fraction.from_float(value).limit_denominator(99999)

def coordinates_by_name(name):
    geolocation_info = lookup(name)

    if(geolocation_info is not None):
        if('results' in geolocation_info and len(geolocation_info['results']) != 0 and 
                'locations' in geolocation_info['results'][0] and len(geolocation_info['results'][0]['locations']) != 0):

            # By default we use the first entry unless we find one with geocodeQuality=city.
            use_location = geolocation_info['results'][0]['locations'][0]['latLng']
            # Loop over the locations to see if we come accross a geocodeQuality=city.
            # If we find a city we set that to the use_location and break
            for location in geolocation_info['results'][0]['locations']:
                if('latLng' in location and 'lat' in location['latLng'] and 'lng' in location['latLng'] and location['geocodeQuality'].lower() == 'city'):
                    use_location = location['latLng']
                    break
                    
            return {
                    'latitude': use_location['lat'],
                    'longitude': use_location['lng']
            }
                    
    return None

def decimal_to_dms(decimal):
    """Convert decimal degrees into degrees, minutes, seconds.

    >>> decimal_to_dms(50.445891)
    [Fraction(50, 1), Fraction(26, 1), Fraction(113019, 2500)]
    >>> decimal_to_dms(-125.976893)
    [Fraction(125, 1), Fraction(58, 1), Fraction(92037, 2500)]
    """
    remainder, degrees = math.modf(abs(decimal))
    remainder, minutes = math.modf(remainder * 60)
    # @TODO figure out a better and more proper way to do seconds
    return (pyexiv2.Rational(degrees, 1), pyexiv2.Rational(minutes, 1), pyexiv2.Rational(int(remainder*1000000000), 1000000000))

def dms_to_decimal(degrees, minutes, seconds, sign=' '):
    """Convert degrees, minutes, seconds into decimal degrees.

    >>> dms_to_decimal(10, 10, 10)
    10.169444444444444
    >>> dms_to_decimal(8, 9, 10, 'S')
    -8.152777777777779
    """
    return (-1 if sign[0] in 'SWsw' else 1) * (
        float(degrees)        +
        float(minutes) / 60   +
        float(seconds) / 3600
    )

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
    geolocation_info = reverse_lookup(lat, lon)
    if(geolocation_info is not None):
        if('address' in geolocation_info):
            address = geolocation_info['address']
            if('city' in address):
                return address['city']
            elif('state' in address):
                return address['state']
            elif('country' in address):
                return address['country']
    return None


def reverse_lookup(lat, lon):
    if(lat is None or lon is None):
        return None

    key = get_key()

    try:
        params = {'format': 'json', 'key': key, 'lat': lat, 'lon': lon}
        r = requests.get('http://open.mapquestapi.com/nominatim/v1/reverse.php?%s' % urllib.urlencode(params))
        return r.json()
    except requests.exceptions.RequestException as e:
        if(constants.debug == True):
            print e
        return None
    except ValueError as e:
        if(constants.debug == True):
            print r.text
            print e
        return None

def lookup(name):
    if(name is None or len(name) == 0):
        return None

    key = get_key()

    try:
        params = {'format': 'json', 'key': key, 'location': name}
        if(constants.debug == True):
            print 'http://open.mapquestapi.com/geocoding/v1/address?%s' % urllib.urlencode(params)
        r = requests.get('http://open.mapquestapi.com/geocoding/v1/address?%s' % urllib.urlencode(params))
        return r.json()
    except requests.exceptions.RequestException as e:
        if(constants.debug == True):
            print e
        return None
    except ValueError as e:
        if(constants.debug == True):
            print r.text
            print e
        return None
