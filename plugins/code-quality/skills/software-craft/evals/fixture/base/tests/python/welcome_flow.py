"""The welcome mail a new member receives."""
import smtplib
from dataclasses import dataclass


@dataclass(frozen=True)
class Member:
    name: str
    email: str


class Mailer:
    """Sends transactional mail through the SMTP relay."""

    def __init__(self, relay_host: str):
        self._relay_host = relay_host

    def send(self, to: str, subject: str, *, template: str, locale: str, track_opens: bool) -> None:
        headers = f"Subject: {subject}\nX-Template: {template}\nX-Locale: {locale}\nX-Track-Opens: {track_opens}\n"
        with smtplib.SMTP(self._relay_host) as smtp:
            smtp.sendmail("welcome@example.com", [to], headers)


class WelcomeFlow:
    TEMPLATE = "welcome-v3"

    def __init__(self, mailer: Mailer, locale: str = "en-GB", dry_run: bool = False):
        self._mailer = mailer
        self._locale = locale
        self._dry_run = dry_run

    def welcome(self, member: Member) -> None:
        if self._dry_run:
            return
        self._mailer.send(member.email, f"Welcome, {member.name}!", template=self.TEMPLATE,
                          locale=self._locale, track_opens=True)
