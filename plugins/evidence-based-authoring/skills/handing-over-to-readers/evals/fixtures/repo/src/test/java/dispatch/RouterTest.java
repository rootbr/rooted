package dispatch;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class RouterTest {
    @Test
    void timeoutDoesNotRetry() {
        Router router = new Router(new Limits(queue -> 100));
        Decision d = router.route(new Job("reports", 10));
        assertFalse(d.retry());
    }

    @Test
    void overLimitIsRejected() {
        Router router = new Router(new Limits(queue -> 5));
        Decision d = router.route(new Job("reports", 10));
        assertTrue(d.rejected());
    }

    @Test
    void ackTimeoutIsFourHundredMillis() {
        Router router = new Router(new Limits(queue -> 100));
        Decision d = router.route(new Job("reports", 10));
        assertEquals(400, d.ackTimeout().toMillis());
    }
}
