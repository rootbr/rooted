package shop;

public final class ReservationService {
    private static final int HANDLING_DAYS = 1;

    private final InventoryGateway inventory;
    private final DeliveryEstimator delivery;

    public ReservationService(InventoryGateway inventory, DeliveryEstimator delivery) {
        this.inventory = inventory;
        this.delivery = delivery;
    }

    public Reservation reserve(String sku, int quantity) {
        if (inventory.stockOf(sku) < quantity) {
            return Reservation.rejected(sku);
        }
        String warehouse = inventory.warehouseFor(sku);
        if (!inventory.reserve(sku, quantity)) {
            return Reservation.rejected(sku);
        }
        return new Reservation(sku, true, warehouse, deliveryDays(warehouse));
    }

    public int deliveryDays(String warehouse) {
        return delivery.daysFrom(warehouse) + HANDLING_DAYS;
    }
}
