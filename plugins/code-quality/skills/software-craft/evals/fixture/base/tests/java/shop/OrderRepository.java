package shop;

/** Orders in the order database. */
public interface OrderRepository {

    /** Stores the order and returns it as stored. */
    Order save(Order order);

    Order findById(String id);
}
