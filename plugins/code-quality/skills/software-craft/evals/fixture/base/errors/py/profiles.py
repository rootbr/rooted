"""User profile parsing and API-token authentication for the account service."""
import hmac
import json


def read_profile_file(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def parse_age_field(raw):
    return int(raw)


def verify_api_token(presented, expected):
    return hmac.compare_digest(presented, expected)
