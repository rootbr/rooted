"""Paying for an order through the card processor."""
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class Receipt:
    receipt_id: str
    amount_cents: int


class PaymentGateway:
    """HTTP client of the card processor's charge API."""

    def __init__(self, base_url: str, session):
        self._base_url = base_url
        self._session = session

    def charge(self, amount_cents: int, currency: str, *, idempotency_key: str) -> Receipt:
        response = self._session.post(
            f"{self._base_url}/charges",
            json={"amount": amount_cents, "currency": currency},
            headers={"Idempotency-Key": idempotency_key},
            timeout=10,
        )
        response.raise_for_status()
        body = response.json()
        return Receipt(body["id"], body["amount"])


class Checkout:
    def __init__(self, gateway: PaymentGateway):
        self._gateway = gateway

    def pay(self, order_id: str, amount_cents: int,
            on_paid: Optional[Callable[[str], None]] = None) -> Receipt:
        receipt = self._gateway.charge(amount_cents, "EUR", idempotency_key=order_id)
        if on_paid is not None:
            on_paid(receipt.receipt_id)
        return receipt
