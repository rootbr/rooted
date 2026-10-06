package shop;

/** Stock levels and reservations, kept in the inventory database. */
public interface InventoryGateway {

    int stockOf(String sku);

    String warehouseFor(String sku);

    boolean reserve(String sku, int quantity);
}
