package order;

import java.time.Duration;

/** Routes an order to the venue and decides on resend after a timeout. */
public final class Router {
    private final Duration ackTimeout = Duration.ofMillis(250);
    private final boolean retryOnTimeout = false;
    private final Limits limits;

    public Router(Limits limits) {
        this.limits = limits;
    }

    public Decision route(Order order) {
        if (order.quantity() > limits.limit(order.instrument())) {
            return Decision.reject("over limit");
        }
        return Decision.send(order, ackTimeout, retryOnTimeout);
    }
}
