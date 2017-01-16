def _decode(string, encoding='utf8'):
    if hasattr(string, 'decode'):
        return string.decode(encoding)

    return string


