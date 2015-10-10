from os import path
from ConfigParser import ConfigParser
import requests
import sys

def reverse_lookup(lat, lon):
    if(lat is None or lon is None):
        return None

    if not path.exists('./config.ini'):
        return None
        
    config = ConfigParser()
    config.read('./config.ini')
    if('MapQuest' not in config.sections()):
        return None

    key = config.get('MapQuest', 'key')

    try:
        r = requests.get('https://open.mapquestapi.com/nominatim/v1/reverse.php?key=%s&lat=%s&lon=%s&format=json' % (key, lat, lon))
        return r.json()
    except requests.exceptions.RequestException as e:
        print e
        return None
    except ValueError as e:
        print r.text
        print e
        return None


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
