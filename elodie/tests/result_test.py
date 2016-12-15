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
from elodie.result import Result

def call_result_and_assert(result, expected):
    saved_stdout = sys.stdout
    try:
        out = StringIO()
        sys.stdout = out
        result.write()
        output = out.getvalue().strip()
        assert output == expected, output
    finally:
        sys.stdout = saved_stdout

def test_add_multiple_rows_with_success():
    expected = """****** SUMMARY ******
Metric      Count
--------  -------
Success         2
Error           0"""
    result = Result()
    result.append(('id1', '/some/path/1'))
    result.append(('id2', '/some/path/2'))
    call_result_and_assert(result, expected)

def test_add_multiple_rows_with_failure():
    expected = """****** ERROR DETAILS ******
File
------
id1
id2


****** SUMMARY ******
Metric      Count
--------  -------
Success         0
Error           2"""
    result = Result()
    result.append(('id1', False))
    result.append(('id2', False))
    call_result_and_assert(result, expected)

def test_add_multiple_rows_with_failure_and_success():
    expected = """****** ERROR DETAILS ******
File
------
id1


****** SUMMARY ******
Metric      Count
--------  -------
Success         1
Error           1"""
    result = Result()
    result.append(('id1', False))
    result.append(('id2', '/some/path'))
    call_result_and_assert(result, expected)
