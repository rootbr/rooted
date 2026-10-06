"""Service settings read from a TOML file."""
import tomllib
from pathlib import Path


class ConfigError(Exception):
    """The settings file is missing, unreadable or holds an invalid value."""


def load_settings_drops_cause(path):
    try:
        raw = Path(path).read_text(encoding="utf-8")
    except OSError:
        raise ConfigError(f"cannot load settings from {path}")
    return tomllib.loads(raw)


def parse_timeout_setting_keeps_input(raw):
    try:
        return float(raw)
    except ValueError:
        # a failed number parse: the rejected text is the relevant detail, so the chain is cut on purpose
        raise ConfigError(f"timeout setting {raw!r} is not a number") from None
