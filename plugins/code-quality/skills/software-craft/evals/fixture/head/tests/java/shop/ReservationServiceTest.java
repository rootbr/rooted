package shop;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import org.junit.jupiter.api.Test;

class ReservationServiceTest {

    @Test
    void reserveStubsEveryInventoryGatewayMethod() {
        InventoryGateway inventory = mock(InventoryGateway.class);
        when(inventory.stockOf("sku-1")).thenReturn(5);
        when(inventory.warehouseFor("sku-1")).thenReturn("BER-1");
        when(inventory.reserve("sku-1", 2)).thenReturn(true);
        Reservation reservation = new ReservationService(inventory, mock(DeliveryEstimator.class)).reserve("sku-1", 2);
        assertTrue(reservation.confirmed());
        assertEquals("BER-1", reservation.warehouse());
    }

    @Test
    void deliveryDaysAddHandlingToTheWarehouseEstimate() {
        // DeliveryEstimator declares a single method, so stubbing it covers no wider API than the test needs.
        DeliveryEstimator delivery = mock(DeliveryEstimator.class);
        when(delivery.daysFrom("BER-1")).thenReturn(2);
        ReservationService service = new ReservationService(mock(InventoryGateway.class), delivery);
        assertEquals(3, service.deliveryDays("BER-1"));
    }
}
