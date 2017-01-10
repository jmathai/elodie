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


def _encode(string, encoding='utf-8'):
    if hasattr(string, 'encode'):
        try:
            return string.encode(encoding)
        except:
            pass

    return string
