import { Clock } from "./clock";
import { DiscountRules } from "./discount-rules";

export interface CartLine {
  sku: string;
  price: number;
  quantity: number;
}

export class Checkout {
  constructor(private readonly rules: DiscountRules, private readonly clock: Clock) {}

  total(lines: CartLine[]): number {
    const subtotal = lines.reduce((sum, line) => sum + line.price * line.quantity, 0);
    const percent = this.rules.discountFor(subtotal, this.clock.now().getDay());
    return subtotal - (subtotal * percent) / 100;
  }
}
