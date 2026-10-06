package billing;

import java.math.BigDecimal;
import java.util.Map;

/** The invoices of all customers, keyed by invoice number, with the payments recorded against them. */
public class InvoiceLedger {
    private final Map<String, Invoice> invoicesByNumber;
    private final AuditTrail auditTrail;

    public InvoiceLedger(Map<String, Invoice> invoicesByNumber, AuditTrail auditTrail) {
        this.invoicesByNumber = invoicesByNumber;
        this.auditTrail = auditTrail;
    }

    BigDecimal balanceOf(Customer customer) {
        BigDecimal balance = BigDecimal.ZERO;
        for (Invoice invoice : invoicesByNumber.values()) {
            if (invoice.customerId().equals(customer.id())) {
                balance = balance.add(invoice.outstanding());
            }
        }
        return balance;
    }

    void recordPayment(Payment payment) {
        Invoice invoice = invoicesByNumber.get(payment.invoiceNumber());
        invoice.recordPayment(payment.amount());
        auditTrail.recordPayment(payment);
    }
}
