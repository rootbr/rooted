package shop;

/** Customer notifications, sent through the mail relay. */
public interface Mailer {

    void sendShippedNotice(Order order);
}
