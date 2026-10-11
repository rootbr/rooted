package shop;

import java.time.LocalDate;

/** A priced offer and the last day it can be accepted. */
public record Quote(Money total, LocalDate validUntil) {
}
