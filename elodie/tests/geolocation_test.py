# Project imports
import os
import sys

import re

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

import helper
from elodie import geolocation

os.environ['TZ'] = 'GMT'

def test_decimal_to_dms():
    target_decimal_value = 37.383336725

    dms = geolocation.decimal_to_dms(target_decimal_value)
    check_value = dms[0].to_float() + dms[1].to_float() / 60 + dms[2].to_float() / 3600

    assert target_decimal_value == check_value, '%s does not match %s' % (check_value, target_decimal_value)
