import { Checkout } from "./checkout";
import { SystemClock } from "./clock";
import { DiscountRules } from "./discount-rules";

test("checkoutTotalOfEmptyCartIsZero", () => {
  const checkout = new Checkout(new DiscountRules(), new SystemClock());
  expect(checkout.total([])).toBe(0);
});
