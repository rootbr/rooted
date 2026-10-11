"""User profile parsing and API-token authentication for the account service."""
import hmac
import json


def read_profile_file(path):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def parse_age_field_with_vague_message(raw):
    text = str(raw).strip()
    if not text.isdigit():
        raise ValueError("invalid input")
    return int(text)


def authenticate_token_names_secret_by_role(account_id, presented, expected):
    if not hmac.compare_digest(presented.encode(), expected.encode()):
        # the token is a secret: the error names it by its role and keeps its value out of the logs
        raise PermissionError(f"authenticate account {account_id}: the presented API token does not match")
    return account_id
