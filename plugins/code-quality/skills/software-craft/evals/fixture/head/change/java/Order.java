package pricing;

/** An order's money amounts, in cents. */
final class Order {
    private final int base;
    private final int rebate;

    Order(int base, int rebate) {
        this.base = base;
        this.rebate = rebate;
    }

    int base() {
        return base;
    }

    int rebate() {
        return rebate;
    }
}
