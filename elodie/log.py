"""
General file system methods.

.. moduleauthor:: Jaisen Mathai <jaisen@jmathai.com>
"""
from __future__ import print_function

from json import dumps

from elodie import constants


def info(message):
    _print(message)


def info_json(payload):
    _print(dumps(payload))


def progress(message='.', new_line=False):
    if not new_line:
        print(message, end="")
    else:
        print(message)


def warn(message):
    _print(message)


def warn_json(payload):
    _print(dumps(payload))


def error(message):
    _print(message)


def error_json(payload):
    _print(dumps(payload))


def write(string, params=()):
    print(string % params)

def _print(string):
    if(constants.debug is True):
        print(string)
