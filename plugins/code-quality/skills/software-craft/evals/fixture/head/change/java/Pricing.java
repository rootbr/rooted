package pricing;

/** Prices an order from its base amount and the rebate it earned. */
final class Pricing {
    private Pricing() {
    }

    static int price(Order order) {
        return discounted(order);
    }

    private static int discounted(Order order) {
        return order.base() - order.rebate();
    }

    private static int legacyPrice(Order order) {
        return order.base();
    }
}
