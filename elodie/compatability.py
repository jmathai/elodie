def _decode(string, encoding='utf-8'):
    """Return a utf8 encoded unicode string.

    Python2 and Python3 differ in how they handle strings.
    So we do a few checks to see if the string is ascii or unicode.
    Then we decode it if needed.
    """
    if hasattr(string, 'decode'):
        # If the string is already unicode we return it.
        try:
            if isinstance(string, unicode):
                return string
        except NameError:
            pass

        return string.decode(encoding)

    return string


def _encode(string):
    """Returns an ascii string.
    Python3 converts bytes to unicode.
    Python2 converts unicode to ascii"""
    # Try Python3 first.
    try:
        return str(string, 'utf-8')
    except TypeError:
        pass

    # Try Python2 next.
    try:
        return string.encode('utf-8')
    except:
        pass
