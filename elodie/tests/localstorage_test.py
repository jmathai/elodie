from __future__ import print_function
from __future__ import absolute_import
# Project imports
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

from . import helper
from elodie.localstorage import Db
from elodie import constants

os.environ['TZ'] = 'GMT'

def test_init_writes_files():
    db = Db()

    assert os.path.isfile(constants.hash_db) == True
    assert os.path.isfile(constants.location_db) == True

def test_add_hash_default_do_not_write():
    db = Db()

    random_key = helper.random_string(10)
    random_value = helper.random_string(12)

    # Test with default False value as 3rd param
    db.add_hash(random_key, random_value)

    assert db.check_hash(random_key) == True, 'Lookup for hash did not return True'

    # Instnatiate new db class to confirm random_key does not exist
    db2 = Db()
    assert db2.check_hash(random_key) == False
    
def test_add_hash_explicit_do_not_write():
    db = Db()

    random_key = helper.random_string(10)
    random_value = helper.random_string(12)

    # Test with explicit False value as 3rd param
    db.add_hash(random_key, random_value, False)

    assert db.check_hash(random_key) == True, 'Lookup for hash did not return True'

    # Instnatiate new db class to confirm random_key does not exist
    db2 = Db()
    assert db2.check_hash(random_key) == False
    
def test_add_hash_explicit_write():
    db = Db()

    random_key = helper.random_string(10)
    random_value = helper.random_string(12)

    # Test with explicit True value as 3rd param
    db.add_hash(random_key, random_value, True)

    assert db.check_hash(random_key) == True, 'Lookup for hash did not return True'

    # Instnatiate new db class to confirm random_key exists
    db2 = Db()
    assert db2.check_hash(random_key) == True

def test_backup_hash_db():
    db = Db()
    backup_file_name = db.backup_hash_db()
    file_exists = os.path.isfile(backup_file_name)
    os.remove(backup_file_name)
    
    assert file_exists, backup_file_name
    
def test_check_hash_exists():
    db = Db()

    random_key = helper.random_string(10)
    random_value = helper.random_string(12)

    # Test with explicit False value as 3rd param
    db.add_hash(random_key, random_value, False)

    assert db.check_hash(random_key) == True, 'Lookup for hash did not return True'
    
def test_check_hash_does_not_exist():
    db = Db()

    random_key = helper.random_string(10)

    assert db.check_hash(random_key) == False, 'Lookup for hash that should not exist returned True'

def test_get_hash_exists():
    db = Db()

    random_key = helper.random_string(10)
    random_value = helper.random_string(12)

    # Test with explicit False value as 3rd param
    db.add_hash(random_key, random_value, False)

    assert db.get_hash(random_key) == random_value, 'Lookup for hash that exists did not return value'
    
def test_get_hash_does_not_exist():
    db = Db()

    random_key = helper.random_string(10)

    assert db.get_hash(random_key) is None, 'Lookup for hash that should not exist did not return None'

def test_get_all():
    db = Db()
    db.reset_hash_db()

    random_keys = []
    random_values = []
    for _ in range(10):
        random_keys.append(helper.random_string(10))
        random_values.append(helper.random_string(12))
        db.add_hash(random_keys[-1:][0], random_values[-1:][0], False)

    counter = 0
    for key, value in db.all():
        assert key in random_keys, key
        assert value in random_values, value
        counter += 1

    assert counter == 10, counter

def test_get_all_empty():
    db = Db()
    db.reset_hash_db()

    counter = 0
    for key, value in db.all():
        counter += 1

    # there's a final iteration because of the generator
    assert counter == 0, counter

def test_reset_hash_db():
    db = Db()

    random_key = helper.random_string(10)
    random_value = helper.random_string(12)

    # Test with explicit False value as 3rd param
    db.add_hash(random_key, random_value, False)
    
    assert random_key in db.hash_db, random_key
    db.reset_hash_db()
    assert random_key not in db.hash_db, random_key


def test_update_hash_db():
    db = Db()

    random_key = helper.random_string(10)
    random_value = helper.random_string(12)

    # Test with default False value as 3rd param
    db.add_hash(random_key, random_value)

    assert db.check_hash(random_key) == True, 'Lookup for hash did not return True'

    # Instnatiate new db class to confirm random_key does not exist
    db2 = Db()
    assert db2.check_hash(random_key) == False

    db.update_hash_db()

    # Instnatiate new db class to confirm random_key exists
    db3 = Db()
    assert db3.check_hash(random_key) == True

def test_checksum():
    db = Db()

    src = helper.get_file('plain.jpg')
    checksum = db.checksum(src)

    assert checksum == 'd5eb755569ddbc8a664712d2d7d6e0fa1ddfcdb378475e4a6758dc38d5ea9a16', 'Checksum for plain.jpg did not match'

def test_add_location():
    db = Db()

    latitude, longitude, name = helper.get_test_location()

    db.add_location(latitude, longitude, name)
    retrieved_name = db.get_location_name(latitude, longitude, 5)

    assert name == retrieved_name

def test_get_location_name():
    db = Db()

    latitude, longitude, name = helper.get_test_location()
    db.add_location(latitude, longitude, name)

    
    # 1 meter
    retrieved_name = db.get_location_name(latitude, longitude, 1)

    assert name == retrieved_name

def test_get_location_name_within_threshold():
    db = Db()

    latitude, longitude, name = helper.get_test_location()
    db.add_location(latitude, longitude, name)

    print(latitude)
    new_latitude = helper.random_coordinate(latitude, 4)
    new_longitude = helper.random_coordinate(longitude, 4)
    print(new_latitude)

    # 10 miles
    retrieved_name = db.get_location_name(new_latitude, new_longitude, 1600*10)

    assert name == retrieved_name, 'Name (%r) did not match retrieved name (%r)' % (name, retrieved_name)

def test_get_location_name_outside_threshold():
    db = Db()

    latitude, longitude, name = helper.get_test_location()
    db.add_location(latitude, longitude, name)

    new_latitude = helper.random_coordinate(latitude, 1)
    new_longitude = helper.random_coordinate(longitude, 1)

    # 800 meters
    retrieved_name = db.get_location_name(new_latitude, new_longitude, 800)

    assert retrieved_name is None

def test_get_location_coordinates_exists():
    db = Db()
    
    latitude, longitude, name = helper.get_test_location()

    name = '%s-%s' % (name, helper.random_string(10))
    latitude = helper.random_coordinate(latitude, 1)
    longitude = helper.random_coordinate(longitude, 1)

    db.add_location(latitude, longitude, name)

    location = db.get_location_coordinates(name)

    assert location is not None
    assert location[0] == latitude
    assert location[1] == longitude

def test_get_location_coordinates_does_not_exists():
    db = Db()
    
    latitude, longitude, name = helper.get_test_location()

    name = '%s-%s' % (name, helper.random_string(10))
    latitude = helper.random_coordinate(latitude, 1)
    longitude = helper.random_coordinate(longitude, 1)

    location = db.get_location_coordinates(name)

    assert location is None
