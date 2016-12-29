def _decode(string, encoding='utf8'):
    # Unicode is not defined in Python 3 and throws a NameError
    # If we encounter a NameError we just assume it's unicode (py3)
    try:
        is_unicode = isinstance(string, unicode)
    except NameError:
        is_unicode = False

    if is_unicode and hasattr(string, 'decode'):
        return string.decode(encoding)

    return string
