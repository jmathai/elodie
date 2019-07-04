"""
General file system methods.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function

import sys

from json import dumps

from elodie import constants

def all(message):
    _print(message)
    

def info(message):
    _print_debug(message)


def info_json(payload):
    _print_debug(dumps(payload))


def progress(message='.', new_line=False):
    if not new_line:
        print(message, end="")
    else:
        print(message)


def warn(message):
    _print_debug(message)


def warn_json(payload):
    _print_debug(dumps(payload))


def error(message):
    _print_debug(message)


def error_json(payload):
    _print_debug(dumps(payload))


def _print_debug(string):
    # Print if debug == True or if running with nosetests
    # Commenting out because this causes failures in other tests
    #  which verify that output is correct.
    # Use the line below if you want output printed during tests.
    # if(constants.debug is True or 'nose' in sys.modules.keys()):
    if(constants.debug is True):
        _print(string)

def _print(s):
    try:
        print(s)
    except UnicodeEncodeError:
        for c in s:
            try:
                print(c, end='')
            except UnicodeEncodeError:
                print('?', end='')
