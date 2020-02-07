from __future__ import absolute_import
from __future__ import division
from builtins import range
from past.utils import old_div
# Project imports
import mock
import os
import random
import re
import sys
from mock import patch
from tempfile import gettempdir

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

from . import helper
from elodie import geolocation

os.environ['TZ'] = 'GMT'


def test_decimal_to_dms():

    for x in range(0, 1000):
        target_decimal_value = random.uniform(0.0, 180.0)
        if(x % 2 == 1):
            target_decimal_value = target_decimal_value * -1

        dms = geolocation.decimal_to_dms(target_decimal_value)

        check_value = (dms[0] + dms[1] / 60 + dms[2] / 3600) * dms[3]

        target_decimal_value = round(target_decimal_value, 8)
        check_value = round(check_value, 8)

        assert target_decimal_value == check_value, '%s does not match %s' % (check_value, target_decimal_value)

def test_dms_to_decimal_positive_sign():
    decimal = geolocation.dms_to_decimal(10, 20, 100, 'NE')
    assert helper.isclose(decimal, 10.3611111111)

    decimal = geolocation.dms_to_decimal(10, 20, 100, 'ne')
    assert helper.isclose(decimal, 10.3611111111)

def test_dms_to_decimal_negative_sign():
    decimal = geolocation.dms_to_decimal(10, 20, 100, 'SW')
    assert helper.isclose(decimal, -10.3611111111)

    decimal = geolocation.dms_to_decimal(10, 20, 100, 'sw')
    assert helper.isclose(decimal, -10.3611111111)

def test_dms_string_latitude():

    for x in range(0, 5):
        target_decimal_value = random.uniform(0.0, 180.0)
        if(x % 2 == 1):
            target_decimal_value = target_decimal_value * -1

        dms = geolocation.decimal_to_dms(target_decimal_value)
        dms_string = geolocation.dms_string(target_decimal_value, 'latitude')

        check_value = 'N' if target_decimal_value >= 0 else 'S'

        assert check_value in dms_string, '%s not in %s' % (check_value, dms_string)
        assert str(dms[0]) in dms_string, '%s not in %s' % (dms[0], dms_string)

def test_dms_string_longitude():

    for x in range(0, 5):
        target_decimal_value = random.uniform(0.0, 180.0)
        if(x % 2 == 1):
            target_decimal_value = target_decimal_value * -1

        dms = geolocation.decimal_to_dms(target_decimal_value)
        dms_string = geolocation.dms_string(target_decimal_value, 'longitude')

        check_value = 'E' if target_decimal_value >= 0 else 'W'

        assert check_value in dms_string, '%s not in %s' % (check_value, dms_string)
        assert str(dms[0]) in dms_string, '%s not in %s' % (dms[0], dms_string)

def test_reverse_lookup_with_valid_key():
    res = geolocation.lookup(lat=37.368, lon=-122.03)
    assert res['address']['city'] == 'Sunnyvale', res

def test_reverse_lookup_with_invalid_lat_lon():
    res = geolocation.lookup(lat=999, lon=999)
    assert res is None, res

@mock.patch('elodie.geolocation.__KEY__', 'invalid_key')
def test_reverse_lookup_with_invalid_key():
    res = geolocation.lookup(lat=37.368, lon=-122.03)
    assert res is None, res

def test_lookup_with_valid_key():
    res = geolocation.lookup(location='Sunnyvale, CA')
    latLng = res['results'][0]['locations'][0]['latLng']
    assert latLng['lat'] == 37.36883, latLng
    assert latLng['lng'] == -122.03635, latLng

def test_lookup_with_invalid_location():
    res = geolocation.lookup(location='foobar dne')
    assert res is None, res

def test_lookup_with_invalid_location():
    res = geolocation.lookup(location='foobar dne')
    assert res is None, res

def test_lookup_with_valid_key():
    res = geolocation.lookup(location='Sunnyvale, CA')
    latLng = res['results'][0]['locations'][0]['latLng']
    assert latLng['lat'] == 37.36883, latLng
    assert latLng['lng'] == -122.03635, latLng

@mock.patch('elodie.geolocation.__PREFER_ENGLISH_NAMES__', True)
def test_lookup_with_prefer_english_names_true():
    res = geolocation.lookup(lat=55.66333, lon=37.61583)
    assert res['address']['city'] == 'Nagorny District', res

@mock.patch('elodie.geolocation.__PREFER_ENGLISH_NAMES__', False)
def test_lookup_with_prefer_english_names_false():
    res = geolocation.lookup(lat=55.66333, lon=37.61583)
    assert res['address']['city'] == u'\u041d\u0430\u0433\u043e\u0440\u043d\u044b\u0439 \u0440\u0430\u0439\u043e\u043d', res

@mock.patch('elodie.geolocation.__PREFER_LANGUAGE__', 'da-DK')
def test_lookup_with_prefer_language_danish():
    res = geolocation.lookup(lat=55.6775055555556, lon=12.5686222222222)
    assert res['address']['city'] == 'København', res

@mock.patch('elodie.constants.location_db', '%s/location.json-cached' % gettempdir())
def test_place_name_deprecated_string_cached():
    # See gh-160 for backwards compatability needed when a string is stored instead of a dict
    helper.reset_dbs()
    with open('%s/location.json-cached' % gettempdir(), 'w') as f:
        f.write("""
[{"lat": 37.3667027222222, "long": -122.033383611111, "name": "OLDVALUE"}]
"""
    )
    place_name = geolocation.place_name(37.3667027222222, -122.033383611111)
    helper.restore_dbs()

    assert place_name['city'] == 'Sunnyvale', place_name

@mock.patch('elodie.constants.location_db', '%s/location.json-cached' % gettempdir())
def test_place_name_cached():
    helper.reset_dbs()
    with open('%s/location.json-cached' % gettempdir(), 'w') as f:
        f.write("""
[{"lat": 37.3667027222222, "long": -122.033383611111, "name": {"city": "UNITTEST"}}]
"""
    )
    place_name = geolocation.place_name(37.3667027222222, -122.033383611111)
    helper.restore_dbs()

    assert place_name['city'] == 'UNITTEST', place_name

def test_place_name_no_default():
    # See gh-160 for backwards compatability needed when a string is stored instead of a dict
    helper.reset_dbs()
    place_name = geolocation.place_name(123456.000, 123456.000)
    helper.restore_dbs()

    assert place_name['default'] == 'Unknown Location', place_name

@mock.patch('elodie.geolocation.__KEY__', 'invalid_key')
def test_lookup_with_invalid_key():
    res = geolocation.lookup(location='Sunnyvale, CA')
    assert res is None, res

@mock.patch('elodie.geolocation.__KEY__', '')
def test_lookup_with_no_key():
    res = geolocation.lookup(location='Sunnyvale, CA')
    assert res is None, res

def test_parse_result_with_error():
    res = geolocation.parse_result({'error': 'foo'})
    assert res is None, res

def test_parse_result_with_city():
    # http://open.mapquestapi.com/nominatim/v1/reverse.php?lat=37.368&lon=-122.03&key=key_goes_here&format=json
    results = {
        "place_id": "60197412",
        "osm_type": "way",
        "osm_id": "30907961",
        "lat": "37.36746105",
        "lon": "-122.030237558742",
        "display_name": "111, East El Camino Real, Sunnyvale, Santa Clara County, California, 94087, United States of America",
        "address": {
            "house_number": "111",
            "road": "East El Camino Real",
            "city": "Sunnyvale",
            "county": "Santa Clara County",
            "state": "California",
            "postcode": "94087",
            "country": "United States of America",
            "country_code": "us"
        }
    }

    res = geolocation.parse_result(results)
    assert res == results, res

def test_parse_result_with_lat_lon():
    # http://open.mapquestapi.com/geocoding/v1/address?location=abcdefghijklmnopqrstuvwxyz&key=key_goes_here&format=json
    results = {
        "results": [
            {
               "locations": [
                    {
                        "latLng": {
                            "lat": 123.00,
                            "lng": -142.99
                        }
                    }
                ]
            }
        ]
    }

    res = geolocation.parse_result(results)
    assert res == results, res

def test_parse_result_with_unknown_lat_lon():
    # http://open.mapquestapi.com/geocoding/v1/address?location=abcdefghijklmnopqrstuvwxyz&key=key_goes_here&format=json
    results = {
        "results": [
            {
               "locations": [
                    {
                        "latLng": {
                            "lat": 39.78373,
                            "lng": -100.445882
                        }
                    }
                ]
            }
        ]
    }

    res = geolocation.parse_result(results)
    assert res is None, res
