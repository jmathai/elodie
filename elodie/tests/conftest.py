#!/usr/bin/env python

import os
import shutil
import sys
import tempfile
import json
from urllib.parse import parse_qs
from urllib.parse import urlparse
import pytest

# Add the parent directories to sys.path so we can import elodie modules and test helpers
test_dir = os.path.dirname(os.path.abspath(__file__))
elodie_root = os.path.dirname(os.path.dirname(test_dir))
sys.path.insert(0, elodie_root)
sys.path.insert(0, test_dir)

from elodie.external.pyexiftool import ExifTool
from elodie.dependencies import get_exiftool
from elodie import constants
from elodie import geolocation


@pytest.fixture(scope="session", autouse=True)
def setup_exiftool():
    """Start ExifTool once for the entire test session."""
    exiftool_addedargs = [
        u'-config',
        u'"{}"'.format(constants.exiftool_config)
    ]
    exiftool = ExifTool(executable_=get_exiftool(), addedargs=exiftool_addedargs)
    exiftool.start()
    
    yield
    
    # Stop ExifTool after all tests complete
    try:
        exiftool.terminate()
    except:
        pass

@pytest.fixture(scope="function", autouse=True)
def setup_test_environment():
    """
    Set up the test environment before each test function.
    This creates a fresh temporary application directory and config file for each test.
    """
    # Get the test directory
    test_directory = os.path.dirname(os.path.abspath(__file__))
    
    # Create a temporary directory to use for the application directory while running tests
    temporary_application_directory = tempfile.mkdtemp('-elodie-tests')
    os.environ['ELODIE_APPLICATION_DIRECTORY'] = temporary_application_directory
    
    # Copy config.ini-sample over to the test application directory
    temporary_config_file_sample = '{}/config.ini-sample'.format(
        os.path.dirname(os.path.dirname(test_directory))
    )
    temporary_config_file = '{}/config.ini'.format(temporary_application_directory)
    shutil.copy2(
        temporary_config_file_sample,
        temporary_config_file,
    )
    
    # Read the sample config file and store contents to be replaced
    with open(temporary_config_file_sample, 'r') as f:
        config_contents = f.read()
    
    # Set the mapquest key in the temporary config file and write it to the temporary application directory
    # Check if MAPQUEST_KEY environment variable is set
    if 'MAPQUEST_KEY' in os.environ:
        config_contents = config_contents.replace('your-api-key-goes-here', os.environ['MAPQUEST_KEY'])
    else:
        # If not set, tests that require it will fail with a clear message
        config_contents = config_contents.replace('your-api-key-goes-here', 'test-key-not-set')
    
    with open(temporary_config_file, 'w+') as f:
        f.write(config_contents)
    
    # Yield control to tests
    yield
    
    # Cleanup after each test
    try:
        shutil.rmtree(temporary_application_directory)
    except OSError:
        pass  # Directory might already be cleaned up


@pytest.fixture(scope="function", autouse=True)
def offline_mapquest(request, monkeypatch):
    """Provide deterministic geocoding for suites that historically depended on live MapQuest."""
    if request.module.__name__ not in (
        'elodie.tests.elodie_test',
        'elodie.tests.filesystem_test',
    ):
        yield
        return

    address_lookup = {
        'new york, ny': {'lat': 40.7128, 'lng': -74.0060, 'city': 'New York', 'state': 'NY', 'country': 'US'},
        'san francisco, ca': {'lat': 37.7749, 'lng': -122.4194, 'city': 'San Francisco', 'state': 'CA', 'country': 'US'},
        'sunnyvale, ca': {'lat': 37.37188, 'lng': -122.03751, 'city': 'Sunnyvale', 'state': 'CA', 'country': 'US'},
        'sunnyvale, california': {'lat': 37.37188, 'lng': -122.03751, 'city': 'Sunnyvale', 'state': 'CA', 'country': 'US'},
    }
    reverse_lookup = {
        '51.521435,0.162714': {'city': 'Rainham', 'state': 'England', 'country': 'GB'},
        '29.758938,-95.3677': {'city': 'Houston', 'state': 'TX', 'country': 'US'},
        '38.1893,-119.9558': {'city': 'Pinecrest', 'state': 'CA', 'country': 'US'},
        '37.366703,-122.033384': {'city': 'Sunnyvale', 'state': 'CA', 'country': 'US'},
        '37.37188,-122.03751': {'city': 'Sunnyvale', 'state': 'CA', 'country': 'US'},
        '40.7128,-74.006': {'city': 'New York', 'state': 'NY', 'country': 'US'},
        '37.7749,-122.4194': {'city': 'San Francisco', 'state': 'CA', 'country': 'US'},
    }

    def canonical_key(lat, lon):
        return '{},{}'.format(round(float(lat), 6), round(float(lon), 6))

    def make_response(payload):
        class FakeResponse(object):
            def __init__(self, body):
                self._body = body
                self.text = json.dumps(body)

            def json(self):
                return self._body

        return FakeResponse(payload)

    def make_address_payload(location):
        match = address_lookup.get(location.lower())
        if match is None:
            return {
                'info': {'statuscode': 0},
                'results': [{
                    'providedLocation': {'location': location},
                    'locations': [{
                        'source': 'FALLBACK',
                        'latLng': {'lat': 0, 'lng': 0},
                    }]
                }]
            }

        return {
            'info': {'statuscode': 0},
            'results': [{
                'providedLocation': {'location': location},
                'locations': [{
                    'adminArea5': match['city'],
                    'adminArea5Type': 'City',
                    'adminArea3': match['state'],
                    'adminArea3Type': 'State',
                    'adminArea1': match['country'],
                    'adminArea1Type': 'Country',
                    'geocodeQuality': 'CITY',
                    'latLng': {'lat': match['lat'], 'lng': match['lng']},
                }]
            }]
        }

    def make_reverse_payload(lat, lon):
        match = reverse_lookup.get(canonical_key(lat, lon))
        if match is None:
            return {'info': {'statuscode': 400}, 'results': []}

        return {
            'info': {'statuscode': 0},
            'results': [{
                'providedLocation': {'latLng': {'lat': float(lat), 'lng': float(lon)}},
                'locations': [{
                    'adminArea5': match['city'],
                    'adminArea5Type': 'City',
                    'adminArea3': match['state'],
                    'adminArea3Type': 'State',
                    'adminArea1': match['country'],
                    'adminArea1Type': 'Country',
                    'latLng': {'lat': float(lat), 'lng': float(lon)},
                }]
            }]
        }

    def fake_get(url, headers=None):
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        path = parsed.path
        if path.endswith('/address'):
            location = params.get('location', [''])[0]
            return make_response(make_address_payload(location))

        if path.endswith('/reverse'):
            lat = params.get('lat', [None])[0]
            lon = params.get('lon', [None])[0]
            if lat is None or lon is None:
                location = params.get('location', [''])[0]
                if ',' in location:
                    lat, lon = location.split(',', 1)
            return make_response(make_reverse_payload(lat, lon))

        return make_response({'info': {'statuscode': 400}, 'results': []})

    monkeypatch.setattr(geolocation.requests, 'get', fake_get)

    yield
