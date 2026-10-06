package shop;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyString;
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
        verify(orders).findById("o-7");
        verify(mailer).sendShippedNotice(order);
    }

    @Test
    void placeOrderPricesSaleItemsInsideTheStub() {
        when(prices.priceOf(anyString())).thenAnswer(invocation -> {
            String sku = invocation.getArgument(0);
            return sku.startsWith("SALE-") ? new BigDecimal("8.00") : new BigDecimal("10.00");
        });
        when(orders.save(any(Order.class))).thenAnswer(invocation -> invocation.getArgument(0));
        Order order = service.place("o-8", List.of("SALE-1", "STD-1"));
        assertEquals(new BigDecimal("18.00"), order.total());
    }

    @Test
    void placeOrderReturnsTheOrderAsStored() {
        when(prices.priceOf("STD-1")).thenReturn(new BigDecimal("10.00"));
        when(orders.save(any(Order.class))).thenAnswer(invocation -> invocation.getArgument(0));
        Order order = service.place("o-9", List.of("STD-1"));
        assertEquals(List.of("STD-1"), order.skus());
    }
}
