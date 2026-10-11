"""A read-through cache for configuration values."""
import warnings


class ConfigCache:
    def __init__(self, loader):
        self._loader = loader
        self._values = {}

    def fetch(self, key):
        # deprecated: use fetch_many() instead, which loads keys in one round trip
        warnings.warn("fetch is deprecated; use fetch_many()", DeprecationWarning, stacklevel=2)
        return self.fetch_many([key])[key]

    def fetch_many(self, keys):
        missing = [key for key in keys if key not in self._values]
        if missing:
            self._values.update(self._loader(missing))
        return {key: self._values[key] for key in keys}

    @warnings.deprecated("lookup is deprecated; use fetch_many(), which loads keys in one round trip")
    def lookup(self, key):
        return self.fetch_many([key])[key]
