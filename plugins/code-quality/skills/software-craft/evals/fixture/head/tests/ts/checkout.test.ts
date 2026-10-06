import { Checkout } from "./checkout";
import { Clock, SystemClock } from "./clock";
import { DiscountRules } from "./discount-rules";

test("checkoutTotalOfEmptyCartIsZero", () => {
  const checkout = new Checkout(new DiscountRules(), new SystemClock());
  expect(checkout.total([])).toBe(0);
});

test("checkoutTotalStubsDiscountRules", () => {
  const rules: jest.Mocked<DiscountRules> = { discountFor: jest.fn().mockReturnValue(5) };
  const clock: Clock = { now: () => new Date("2026-03-04T10:00:00Z") };
  const checkout = new Checkout(rules, clock);
  expect(checkout.total([{ sku: "sku-1", price: 50, quantity: 2 }])).toBe(95);
});

test("checkoutTotalOnATuesdayTakesTenPercentOff", () => {
  // the clock is the external dependency the double replaces; DiscountRules stays real
  const clock: jest.Mocked<Clock> = { now: jest.fn().mockReturnValue(new Date("2026-03-03T10:00:00Z")) };
  const checkout = new Checkout(new DiscountRules(), clock);
  expect(checkout.total([{ sku: "sku-1", price: 50, quantity: 2 }])).toBe(90);
});
