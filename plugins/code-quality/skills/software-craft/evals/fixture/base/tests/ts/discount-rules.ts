/** Percentage off a cart: 10 on Tuesdays, otherwise 5 from a subtotal of 100 upwards. */
export class DiscountRules {
  discountFor(subtotal: number, weekday: number): number {
    if (weekday === 2) {
      return 10;
    }
    return subtotal >= 100 ? 5 : 0;
  }
}
