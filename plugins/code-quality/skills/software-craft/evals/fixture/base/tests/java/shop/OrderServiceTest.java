package shop;

import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.util.List;
import org.junit.jupiter.api.Test;

class OrderServiceTest {

    private final PriceList prices = mock(PriceList.class);
    private final OrderRepository orders = mock(OrderRepository.class);
    private final Mailer mailer = mock(Mailer.class);
    private final OrderService service = new OrderService(prices, orders, mailer);

    @Test
    void shipSendsShippedNotice() {
        Order order = new Order("o-7", List.of("STD-1"), new BigDecimal("10.00"));
        when(orders.findById("o-7")).thenReturn(order);
        service.ship("o-7");
        verify(mailer).sendShippedNotice(order);
    }
}
