"""Display names for user profiles, looked up in the LDAP user directory."""
from dataclasses import dataclass
from typing import Optional


class DirectoryUnavailable(Exception):
    """The LDAP server did not answer."""


@dataclass(frozen=True)
class User:
    user_id: int
    display_name: str


class UserDirectory:
    """Client of the LDAP user directory."""

    def __init__(self, connection):
        self._connection = connection

    def find(self, user_id: int) -> Optional[User]:
        """Return the user with this id, or None when no user has it.

        Raises DirectoryUnavailable when the LDAP server does not answer. An unknown id
        is not an error: find returns None for it and raises nothing.
        """
        try:
            entry = self._connection.search_one(f"(uid={user_id})")
        except ConnectionError as e:
            raise DirectoryUnavailable(f"LDAP search for uid={user_id} failed") from e
        return User(user_id, entry["cn"]) if entry is not None else None


class Profiles:
    def __init__(self, directory: UserDirectory):
        self._directory = directory

    def name(self, user_id: int) -> str:
        try:
            user = self._directory.find(user_id)
        except KeyError:
            return "guest"
        return user.display_name if user is not None else "guest"

    def name_or_placeholder(self, user_id: int) -> str:
        try:
            return self.name(user_id)
        except DirectoryUnavailable:
            return "unknown (directory offline)"
