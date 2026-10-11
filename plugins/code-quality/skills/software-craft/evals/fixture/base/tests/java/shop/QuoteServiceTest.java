package shop;

import static org.junit.jupiter.api.Assertions.assertEquals;

import java.math.BigDecimal;
import java.time.Clock;
import org.junit.jupiter.api.Test;

class QuoteServiceTest {

    @Test
    void quoteMultipliesUnitPriceByQuantity() {
        Quote quote = new QuoteService(Clock.systemUTC()).quote(new Money(new BigDecimal("9.99"), "EUR"), 3);
        assertEquals(new Money(new BigDecimal("29.97"), "EUR"), quote.total());
    }
}
