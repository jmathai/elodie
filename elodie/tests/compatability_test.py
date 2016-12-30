import mock

from nose.plugins.skip import SkipTest
from six import text_type

from elodie.compatability import _decode

def test_decode_ascii():
    decoded = _decode('foo')
    assert decoded == u'foo', decoded

def test_decode_unicode():
    decoded = _decode(u'foo')
    assert decoded == u'foo', decoded

def test_decode_utf8():
    try:
        decoded = _decode(unicode('foo', 'utf-8'))
        assert decoded == u'foo', decoded
    except NameError:
       raise SkipTest("Skip in python3 since all strings are unicode")
