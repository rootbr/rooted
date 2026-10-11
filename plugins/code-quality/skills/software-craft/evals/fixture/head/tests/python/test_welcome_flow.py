from unittest.mock import ANY, create_autospec

from welcome_flow import Mailer, Member, WelcomeFlow


def test_welcome_mail_goes_to_member_address():
    mailer = create_autospec(Mailer, instance=True)
    WelcomeFlow(mailer).welcome(Member(name="Ann", email="ann@example.com"))
    mailer.send.assert_called_once_with("ann@example.com", ANY, template=ANY, locale=ANY, track_opens=ANY)


def test_welcome_mail_addresses_member_by_name():
    mailer = create_autospec(Mailer, instance=True)
    WelcomeFlow(mailer, locale="en-GB").welcome(Member(name="Ann", email="ann@example.com"))
    mailer.send.assert_called_once_with("ann@example.com", "Welcome, Ann!", template="welcome-v3", locale="en-GB", track_opens=True)


def test_dry_run_welcome_leaves_mailer_untouched():
    mailer = create_autospec(Mailer, instance=True)
    WelcomeFlow(mailer, dry_run=True).welcome(Member(name="Ann", email="ann@example.com"))
    # a dry run must send nothing: the missing send is the behaviour under test
    mailer.send.assert_not_called()
