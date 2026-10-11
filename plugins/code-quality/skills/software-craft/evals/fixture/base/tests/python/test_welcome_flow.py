from unittest.mock import ANY, create_autospec

from welcome_flow import Mailer, Member, WelcomeFlow


def test_welcome_mail_goes_to_member_address():
    mailer = create_autospec(Mailer, instance=True)
    WelcomeFlow(mailer).welcome(Member(name="Ann", email="ann@example.com"))
    mailer.send.assert_called_once_with("ann@example.com", ANY, template=ANY, locale=ANY, track_opens=ANY)
