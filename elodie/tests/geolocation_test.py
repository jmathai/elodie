# Project imports
import os
import random
import re
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))))

import helper
from elodie import geolocation

os.environ['TZ'] = 'GMT'

def test_decimal_to_dms():

    for x in range(0, 1000):
        target_decimal_value = random.uniform(0.0, 180.0)
        if(x % 2 == 1):
            target_decimal_value = target_decimal_value * -1
    
        dms = geolocation.decimal_to_dms(target_decimal_value)
        check_value = dms[0].to_float() + dms[1].to_float() / 60 + dms[2].to_float() / 3600

        target_decimal_value = round(target_decimal_value, 8)
        check_value = round(check_value, 8)

        assert target_decimal_value == check_value, '%s does not match %s' % (check_value, target_decimal_value)

def test_decimal_to_dms_unsigned():

    for x in range(0, 1000):
        target_decimal_value = random.uniform(0.0, 180.0) * -1
    
        dms = geolocation.decimal_to_dms(target_decimal_value, False)
        check_value = dms[0].to_float() + dms[1].to_float() / 60 + dms[2].to_float() / 3600

        target_decimal_value = round(target_decimal_value, 8)
        check_value = round(check_value, 8)

        new_target_decimal_value = abs(target_decimal_value)

        assert new_target_decimal_value == check_value, '%s does not match %s' % (check_value, new_target_decimal_value)
