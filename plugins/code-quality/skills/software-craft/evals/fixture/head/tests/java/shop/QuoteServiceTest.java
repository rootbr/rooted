package shop;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

import java.math.BigDecimal;
import java.time.Clock;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import org.junit.jupiter.api.Test;

class QuoteServiceTest {

    @Test
    void quoteMultipliesUnitPriceByQuantity() {
        Quote quote = new QuoteService(Clock.systemUTC()).quote(new Money(new BigDecimal("9.99"), "EUR"), 3);
        assertEquals(new Money(new BigDecimal("29.97"), "EUR"), quote.total());
    }

    @Test
    void quoteTotalMocksMoneyValue() {
        Money unitPrice = mock(Money.class);
        when(unitPrice.times(3)).thenReturn(new Money(new BigDecimal("29.97"), "EUR"));
        Quote quote = new QuoteService(Clock.systemUTC()).quote(unitPrice, 3);
        assertEquals(new BigDecimal("29.97"), quote.total().amount());
    }

    @Test
    void quoteStaysValidForFourteenDaysFromTheClock() {
        // Clock is the source of the current time, not a value: the double replaces the system clock.
        Clock clock = mock(Clock.class);
        when(clock.instant()).thenReturn(Instant.parse("2026-03-02T09:00:00Z"));
        when(clock.getZone()).thenReturn(ZoneOffset.UTC);
        Quote quote = new QuoteService(clock).quote(new Money(new BigDecimal("9.99"), "EUR"), 1);
        assertEquals(LocalDate.parse("2026-03-16"), quote.validUntil());
    }
}
