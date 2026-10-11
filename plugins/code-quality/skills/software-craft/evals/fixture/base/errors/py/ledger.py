"""Account ledger: transfers between accounts and the balance cache."""
import logging

log = logging.getLogger(__name__)


class InsufficientFunds(Exception):
    """A debit asked for more than the account holds."""


def debit(account, amount):
    if account.balance < amount:
        raise InsufficientFunds(f"debit {amount} from account {account.id}: balance is {account.balance}")
    account.balance -= amount


def credit(account, amount):
    account.balance += amount


def transfer_between_accounts(source, target, amount):
    debit(source, amount)
    credit(target, amount)
