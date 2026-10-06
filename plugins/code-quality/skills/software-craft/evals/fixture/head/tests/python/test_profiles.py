from unittest.mock import create_autospec

from profiles import DirectoryUnavailable, Profiles, User, UserDirectory


def test_profile_name_uses_display_name():
    directory = create_autospec(UserDirectory, instance=True)
    directory.find.return_value = User(7, "Ann Lee")
    assert Profiles(directory).name(7) == "Ann Lee"


def test_profile_name_is_guest_when_directory_raises_key_error():
    directory = create_autospec(UserDirectory, instance=True)
    directory.find.side_effect = KeyError(7)
    assert Profiles(directory).name(7) == "guest"


def test_profile_name_reports_directory_outage():
    directory = create_autospec(UserDirectory, instance=True)
    # find() documents DirectoryUnavailable for an LDAP server that does not answer
    directory.find.side_effect = DirectoryUnavailable("ldap://directory.internal timed out")
    assert Profiles(directory).name_or_placeholder(7) == "unknown (directory offline)"
