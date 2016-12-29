def _decode(string, encoding='utf8'):
    if not isinstance(string, unicode) and hasattr(string, 'decode'):
        return string.decode(encoding)

    return string
