from unittest.mock import MagicMock, Mock, create_autospec

from checkout import Checkout, PaymentGateway, Receipt


def test_checkout_pays_through_bare_gateway_mock():
    gateway = MagicMock()
    gateway.charge.return_value = Receipt("r-1", 4200)
    receipt = Checkout(gateway).pay("o-1", 4200)
    assert receipt.receipt_id == "r-1"


def test_checkout_reports_receipt_to_paid_callback():
    gateway = create_autospec(PaymentGateway, instance=True)
    gateway.charge.return_value = Receipt("r-2", 1500)
    on_paid = Mock()  # a throwaway callback: no production type stands behind it
    Checkout(gateway).pay("o-2", 1500, on_paid=on_paid)
    on_paid.assert_called_once_with("r-2")
