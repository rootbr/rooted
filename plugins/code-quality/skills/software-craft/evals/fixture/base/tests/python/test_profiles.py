from unittest.mock import create_autospec

from profiles import Profiles, User, UserDirectory


def test_profile_name_uses_display_name():
    directory = create_autospec(UserDirectory, instance=True)
    directory.find.return_value = User(7, "Ann Lee")
    assert Profiles(directory).name(7) == "Ann Lee"
