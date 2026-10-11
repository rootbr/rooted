package shop;

/** Delivery days from a warehouse, read from the carrier-rates table in the inventory database. */
public interface DeliveryEstimator {

    int daysFrom(String warehouse);
}
