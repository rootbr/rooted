#!/usr/bin/env python3
"""The generator that wrote the pilot rows of evals/expected.json (36 seeds, 36 controls on the CODE, ERR and TST cards).
Kept as the pattern for extending expected.json when the fixture grows: one seed and one control per card, each a
(rule_id, file, symbol) triple; a symbol may be a list of the spellings the finders might report. Usage: python3 pilot-expected-gen.py > expected.json"""
import json, sys

def ts(name, *extra):
    return list(extra) + [name, f'"{name}"', f"'{name}'", f'test("{name}")', f"test('{name}')"]

J = "tests/java/shop/"
P = "tests/python/"
T = "tests/ts/"
seeds = [
    ("tst-01-seed", "TST-01", T + "checkout.test.ts", ts("checkoutTotalStubsDiscountRules")),
    ("tst-02-seed", "TST-02", J + "ReservationServiceTest.java", "reserveStubsEveryInventoryGatewayMethod"),
    ("tst-03-seed", "TST-03", P + "test_profiles.py", "test_profile_name_is_guest_when_directory_raises_key_error"),
    ("tst-04-seed", "TST-04", J + "QuoteServiceTest.java", "quoteTotalMocksMoneyValue"),
    ("tst-05-seed", "TST-05", T + "order-history.test.ts", ts("latestOrderIsTheNewestPlaced", "InMemoryOrderRepository")),
    ("tst-06-seed", "TST-06", P + "test_release_notes.py", "test_render_notes_patches_markdown_package"),
    ("tst-07-seed", "TST-07", J + "OrderServiceTest.java", "placeOrderPricesSaleItemsInsideTheStub"),
    ("tst-08-seed", "TST-08", T + "shipping.test.ts", ts("shippingQuoteSurfacesPrimaryCarrierFailure")),
    ("tst-09-seed", "TST-09", J + "OrderServiceTest.java", "shipSendsShippedNotice"),
    ("tst-10-seed", "TST-10", P + "test_welcome_flow.py", "test_welcome_mail_addresses_member_by_name"),
    ("tst-11-seed", "TST-11", P + "test_checkout.py", "test_checkout_pays_through_bare_gateway_mock"),
    ("tst-12-seed", "TST-12", T + "invoice.test.ts", ts("invoiceTotalStubsItsOwnTaxMethod")),
]
controls = [
    ("tst-01-control", "TST-01", T + "checkout.test.ts", ts("checkoutTotalOnATuesdayTakesTenPercentOff")),
    ("tst-02-control", "TST-02", J + "ReservationServiceTest.java", "deliveryDaysAddHandlingToTheWarehouseEstimate"),
    ("tst-03-control", "TST-03", P + "test_profiles.py", "test_profile_name_reports_directory_outage"),
    ("tst-04-control", "TST-04", J + "QuoteServiceTest.java", "quoteStaysValidForFourteenDaysFromTheClock"),
    ("tst-05-control", "TST-05", T + "session-guard.test.ts", ts("sessionGuardResolvesTheLoggedInUser", "FakeSessionStore")),
    ("tst-06-control", "TST-06", P + "test_release_notes.py", "test_render_notes_through_project_renderer"),
    ("tst-07-control", "TST-07", J + "OrderServiceTest.java", "placeOrderReturnsTheOrderAsStored"),
    ("tst-08-control", "TST-08", T + "shipping.test.ts", ts("shippingQuoteLeavesFallbackUntouchedWhenPrimaryAnswers")),
    ("tst-09-control", "TST-09", J + "CachedPriceListTest.java", "repeatedLookupsReadTheCatalogueOnce"),
    ("tst-10-control", "TST-10", P + "test_welcome_flow.py", "test_dry_run_welcome_leaves_mailer_untouched"),
    ("tst-11-control", "TST-11", P + "test_checkout.py", "test_checkout_reports_receipt_to_paid_callback"),
    ("tst-12-control", "TST-12", T + "invoice.test.ts", ts("legacyInvoicePrintPutsHeaderFirst")),
]
out = ['{', ' "seeds": [']
rows = [json.dumps({"id": i, "rule_id": r, "file": f, "symbol": s}) for i, r, f, s in seeds]
out.append(",\n".join("  " + x for x in rows))
out.append(' ],')
out.append(' "controls": [')
rows = [json.dumps({"id": i, "silent": [r], "file": f, "symbol": s}) for i, r, f, s in controls]
out.append(",\n".join("  " + x for x in rows))
out.append(' ]')
out.append('}')
text = "\n".join(out) + "\n"
json.loads(text)
open(sys.argv[1], "w").write(text)
