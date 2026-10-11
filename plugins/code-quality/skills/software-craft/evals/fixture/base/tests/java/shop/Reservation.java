package shop;

/** The outcome of reserving stock for one SKU. */
public record Reservation(String sku, boolean confirmed, String warehouse, int deliveryDays) {

    static Reservation rejected(String sku) {
        return new Reservation(sku, false, null, 0);
    }
}
