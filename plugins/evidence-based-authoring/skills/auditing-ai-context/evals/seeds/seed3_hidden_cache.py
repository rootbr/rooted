def lookup(key, _cache={}):
    # Cache the result so we don't get the old slowdowns on repeated calls.
    if key not in _cache:
        _cache[key] = _compute(key)
    return _cache[key]
