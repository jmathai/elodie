from __future__ import absolute_import
from __future__ import division
from builtins import range
from nose.plugins.skip import SkipTest
from past.utils import old_div
# Project imports
import mock
import os
import random
import re
import sys
from mock import patch
from tempfile import gettempdir

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

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
    assert latLng['lat'] == 37.37188, latLng
    assert latLng['lng'] == -122.03751, latLng

def test_lookup_with_invalid_location():
    res = geolocation.lookup(location='foobar dne')
    # Mapquest API started returning json (gh-475)
    assert res is not None, res

@mock.patch('elodie.geolocation.__PREFER_ENGLISH_NAMES__', True)
def test_lookup_with_prefer_english_names_true():
    raise SkipTest("gh-425 MapQuest API no longer supports prefer_english_names.")
    res = geolocation.lookup(lat=55.66333, lon=37.61583)
    assert res['address']['city'] == 'Nagorny District', res

@mock.patch('elodie.geolocation.__PREFER_ENGLISH_NAMES__', False)
def test_lookup_with_prefer_english_names_false():
    raise SkipTest("gh-425 MapQuest API no longer supports prefer_english_names.")
    res = geolocation.lookup(lat=55.66333, lon=37.61583)
    assert res['address']['city'] == u'\u041d\u0430\u0433\u043e\u0440\u043d\u044b\u0439 \u0440\u0430\u0439\u043e\u043d', res

@mock.patch('elodie.constants.debug', True)
def test_lookup_debug_mapquest_url():
    out = StringIO()
    sys.stdout = out
    res = geolocation.lookup(location='Sunnyvale, CA')
    output = out.getvalue()
    assert 'MapQuest url:' in output, output

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
    # https://www.mapquestapi.com/geocoding/v1/reverse?location=37.37188,-122.03751&key=key_goes_here&format=json
    results = {"info":{"statuscode":0,"copyright":{"text":"© 2022 MapQuest, Inc.","imageUrl":"http://api.mqcdn.com/res/mqlogo.gif","imageAltText":"© 2022 MapQuest, Inc."},"messages":[]},"options":{"maxResults":1,"ignoreLatLngInput":False},"results":[{"providedLocation":{"latLng":{"lat":37.368,"lng":-122.03}},"locations":[{"street":"312 Old San Francisco Rd","adminArea6":"Heritage District","adminArea6Type":"Neighborhood","adminArea5":"Sunnyvale","adminArea5Type":"City","adminArea4":"Santa Clara","adminArea4Type":"County","adminArea3":"CA","adminArea3Type":"State","adminArea1":"US","adminArea1Type":"Country","postalCode":"94086","geocodeQualityCode":"P1AAA","geocodeQuality":"POINT","dragPoint":False,"sideOfStreet":"R","linkId":"0","unknownInput":"","type":"s","latLng":{"lat":37.36798,"lng":-122.03018},"displayLatLng":{"lat":37.36785,"lng":-122.03021},"mapUrl":""}]}]}

    res = geolocation.parse_result(results)
    assert res == results, res

def test_parse_result_with_lat_lon():
    # https://www.mapquestapi.com/geocoding/v1/address?format=json&key=key_goes_here&locale=en_US&location=Sunnyvale,CA
    results = {"info":{"statuscode":0,"copyright":{"text":"© 2022 MapQuest, Inc.","imageUrl":"http://api.mqcdn.com/res/mqlogo.gif","imageAltText":"© 2022 MapQuest, Inc."},"messages":[]},"options":{"maxResults":-1,"ignoreLatLngInput":False},"results":[{"providedLocation":{"location":"Sunnyvale,CA"},"locations":[{"street":"","adminArea6":"","adminArea6Type":"Neighborhood","adminArea5":"Sunnyvale","adminArea5Type":"City","adminArea4":"Santa Clara","adminArea4Type":"County","adminArea3":"CA","adminArea3Type":"State","adminArea1":"US","adminArea1Type":"Country","postalCode":"","geocodeQualityCode":"A5XAX","geocodeQuality":"CITY","dragPoint":False,"sideOfStreet":"N","linkId":"0","unknownInput":"","type":"s","latLng":{"lat":37.37188,"lng":-122.03751},"displayLatLng":{"lat":37.37188,"lng":-122.03751},"mapUrl":""}]}]}

    res = geolocation.parse_result(results)
    assert res == results, res

def test_parse_result_with_unknown_lat_lon():
    # https://www.mapquestapi.com/geocoding/v1/address?format=json&key=key_goes_here&locale=en_US&location=ABCDEFGHIJKLMNOPQRSTUVWXYZ
    results = {"info":{"statuscode":0,"copyright":{"text":"© 2022 MapQuest, Inc.","imageUrl":"http://api.mqcdn.com/res/mqlogo.gif","imageAltText":"© 2022 MapQuest, Inc."},"messages":[]},"options":{"maxResults":-1,"ignoreLatLngInput":False},"results":[{"providedLocation":{"location":"ABCDEFGHIJKLMNOPQRSTUVWXYZ"},"locations":[{"street":"","adminArea6":"","adminArea5":"","adminArea4":"","adminArea3":"","adminArea1":"US","postalCode":"","geocodeQualityCode":"A1XAX","geocodeQuality":"COUNTRY","dragPoint":False,"sideOfStreet":"N","linkId":"0","unknownInput":"","type":"s","latLng":{"lat":38.89037,"lng":-77.03196},"displayLatLng":{"lat":38.89037,"lng":-77.03196},"mapUrl":""}]}]}

    res = geolocation.parse_result(results)
    assert res is None, res

@mock.patch('elodie.geolocation.ExifTool')
def test_exiftool_geolocation_success(mock_exiftool_class):
    # Mock ExifTool response for Sunnyvale coordinates
    mock_et = mock_exiftool_class.return_value.__enter__.return_value
    mock_et.execute.return_value = b"Geolocation database:\nCity,Region,Subregion,CountryCode,Country,TimeZone,FeatureCode,Population,Latitude,Longitude\nCupertino,California,Santa Clara County,US,United States,America/Los_Angeles,PPL,60000,37.3229,-122.0322\nSunnyvale,California,Santa Clara County,US,United States,America/Los_Angeles,PPL,152000,37.3688,-122.0363"
    
    result = geolocation.exiftool_geolocation(37.368, -122.03)
    
    assert result is not None, "ExifTool geolocation should return result"
    assert 'city' in result, "Result should contain city"
    assert 'default' in result, "Result should contain default location"
    assert result['city'] in ['Cupertino', 'Sunnyvale'], f"City should be Cupertino or Sunnyvale, got {result['city']}"

@mock.patch('elodie.geolocation.ExifTool')
def test_exiftool_geolocation_no_match(mock_exiftool_class):
    # Mock ExifTool response with no nearby cities
    mock_et = mock_exiftool_class.return_value.__enter__.return_value
    mock_et.execute.return_value = b"Geolocation database:\nCity,Region,Subregion,CountryCode,Country,TimeZone,FeatureCode,Population,Latitude,Longitude\nNew York,New York,New York County,US,United States,America/New_York,PPL,8000000,40.7128,-74.0060"
    
    result = geolocation.exiftool_geolocation(37.368, -122.03)
    
    # Should return None since New York is too far from Sunnyvale coordinates
    assert result is None, "ExifTool geolocation should return None for distant coordinates"

@mock.patch('elodie.geolocation.ExifTool')
def test_exiftool_geolocation_exception(mock_exiftool_class):
    # Mock ExifTool to raise an exception
    mock_exiftool_class.return_value.__enter__.side_effect = Exception("ExifTool error")
    
    result = geolocation.exiftool_geolocation(37.368, -122.03)
    
    assert result is None, "ExifTool geolocation should return None on exception"

def test_exiftool_geolocation_invalid_coordinates():
    result = geolocation.exiftool_geolocation(None, None)
    assert result is None, "ExifTool geolocation should return None for None coordinates"
    
    result = geolocation.exiftool_geolocation(37.368, None)
    assert result is None, "ExifTool geolocation should return None for partial coordinates"

@mock.patch('elodie.geolocation.exiftool_geolocation')
@mock.patch('elodie.geolocation.get_key')
def test_place_name_uses_mapquest_when_key_available(mock_get_key, mock_exiftool_geo):
    # Mock MapQuest key to be available
    mock_get_key.return_value = 'test_key'
    
    # This will test that when MapQuest key is available, it uses MapQuest (not ExifTool)
    result = geolocation.place_name(37.368, -122.03)
    
    # Should have checked for MapQuest key first
    mock_get_key.assert_called_once()
    # Should NOT have called ExifTool since MapQuest key is available
    mock_exiftool_geo.assert_not_called()

@mock.patch('elodie.geolocation.exiftool_geolocation')
@mock.patch('elodie.geolocation.get_key')
def test_place_name_uses_exiftool_when_no_mapquest_key(mock_get_key, mock_exiftool_geo):
    # Mock no MapQuest key available
    mock_get_key.return_value = None
    # Mock ExifTool to return a successful result
    mock_exiftool_geo.return_value = {'city': 'Cupertino', 'default': 'Cupertino', 'country': 'United States'}
    
    result = geolocation.place_name(37.368, -122.03)
    
    # Should have checked for MapQuest key first
    mock_get_key.assert_called_once()
    # Should have called ExifTool since no MapQuest key
    mock_exiftool_geo.assert_called_once_with(37.368, -122.03)
    # Should return the ExifTool result
    assert result['city'] == 'Cupertino', f"Expected Cupertino, got {result.get('city')}"
