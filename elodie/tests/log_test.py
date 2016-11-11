from __future__ import absolute_import
# Project imports

import os
import sys
import unittest 

from json import dumps
from mock import patch
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

from elodie import constants
from elodie import log


def call_log_and_assert(func, message, expected):
    saved_stdout = sys.stdout
    try:
        out = StringIO()
        sys.stdout = out
        func(message)
        output = out.getvalue().strip()
        assert output == expected, (func, output)
    finally:
        sys.stdout = saved_stdout

@patch('elodie.log')
@patch('elodie.constants.debug', True)
def test_calls_print_debug_true(fake_log):
    expected = 'some string'
    fake_log.info.return_value = expected
    fake_log.warn.return_value = expected
    fake_log.error.return_value = expected
    for func in [log.info, log.warn, log.error]:
        call_log_and_assert(func, expected, expected)

    expected_json = {'foo':'bar'}
    fake_log.info.return_value = expected_json
    fake_log.warn.return_value = expected_json
    fake_log.error.return_value = expected_json
    for func in [log.info_json, log.warn_json, log.error_json]:
        call_log_and_assert(func, expected_json, dumps(expected_json))

@patch('elodie.log')
@patch('elodie.constants.debug', False)
def test_calls_print_debug_false(fake_log):
    expected = 'some other string'
    fake_log.info.return_value = expected
    fake_log.warn.return_value = expected
    fake_log.error.return_value = expected
    for func in [log.info, log.warn, log.error]:
        call_log_and_assert(func, expected, '')

    expected_json = {'foo':'bar'}
    fake_log.info.return_value = expected_json
    fake_log.warn.return_value = expected_json
    fake_log.error.return_value = expected_json
    for func in [log.info_json, log.warn_json, log.error_json]:
        call_log_and_assert(func, expected_json, '')
