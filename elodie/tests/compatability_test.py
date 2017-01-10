import mock

from nose.plugins.skip import SkipTest
from six import unichr as six_unichr

from elodie.compatability import _decode, _encode

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

def test_encode_ascii():
    actual = _encode('foo')
    assert actual == 'foo', actual
    
def test_encode_unicode():
    raise SkipTest("Temporarily skip because Python2 and Python3 differ")
    actual = _encode(u'foo'+six_unichr(160))
    assert actual == 'foo\xa0', repr(actual)
