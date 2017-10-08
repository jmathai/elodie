"""
Settings used by Elodie.
"""

from collections import namedtuple
from os import path
from sys import version_info


from elodie.config import load_config

class Values(object):
    pass


def config_as_constants():
    constants = Values()

    config_constants = load_config()['Constants']
    print(config_constants.items())
    constants.application_directory = 'foo'
    constants.hash_db = 'foo'
    return constants


values = config_as_constants()
