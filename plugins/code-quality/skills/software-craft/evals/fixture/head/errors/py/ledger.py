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


def transfer_credits_after_failed_debit(source, target, amount):
    try:
        debit(source, amount)
    except InsufficientFunds as err:
        log.warning("transfer %s -> %s: %s", source.id, target.id, err)
    credit(target, amount)


def refresh_balance_cache_best_effort(cache, account):
    try:
        cache.set(f"balance:{account.id}", account.balance)
    except ConnectionError as err:
        # best effort: readers fall back to the ledger on a cache miss, and nothing below reads the cache
        log.warning("refresh balance cache for account %s: %s", account.id, err)
    return account.balance
