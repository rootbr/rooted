package shop;

import java.math.BigDecimal;
import java.util.List;

public final class OrderService {
    private final PriceList prices;
    private final OrderRepository orders;
    private final Mailer mailer;

    public OrderService(PriceList prices, OrderRepository orders, Mailer mailer) {
        this.prices = prices;
        this.orders = orders;
        this.mailer = mailer;
    }

    public Order place(String id, List<String> skus) {
        BigDecimal total = skus.stream().map(prices::priceOf).reduce(BigDecimal.ZERO, BigDecimal::add);
        return orders.save(new Order(id, List.copyOf(skus), total));
    }

    public void ship(String id) {
        Order order = orders.findById(id);
        mailer.sendShippedNotice(order);
    }
}
