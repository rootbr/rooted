package order;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class RouterTest {
    @Test
    void timeoutDoesNotRetry() {
        Router router = new Router(new Limits(instrument -> 100));
        Decision d = router.route(new Order("SBER", 10));
        assertFalse(d.retry());
    }

    @Test
    void overLimitIsRejected() {
        Router router = new Router(new Limits(instrument -> 5));
        Decision d = router.route(new Order("SBER", 10));
        assertTrue(d.rejected());
    }

    @Test
    void ackTimeoutIsFourHundredMillis() {
        Router router = new Router(new Limits(instrument -> 100));
        Decision d = router.route(new Order("SBER", 10));
        assertEquals(400, d.ackTimeout().toMillis());
    }
}
