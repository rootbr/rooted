package billing;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Predicate;

/** The invoices of all customers, keyed by invoice number, with the payments recorded against them. */
public class InvoiceLedger {
    private static final BigDecimal DAILY_LATE_FEE_RATE = new BigDecimal("0.0005");
    private static final BigDecimal MAX_LATE_FEE = new BigDecimal("150.00");

    private final Map<String, Invoice> invoicesByNumber;
    private final AuditTrail auditTrail;
    private final ReceiptMailer receipts;
    private final ReminderScheduler reminders;

    public InvoiceLedger(Map<String, Invoice> invoicesByNumber, AuditTrail auditTrail,
                         ReceiptMailer receipts, ReminderScheduler reminders) {
        this.invoicesByNumber = invoicesByNumber;
        this.auditTrail = auditTrail;
        this.receipts = receipts;
        this.reminders = reminders;
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
        Invoice invoice = invoiceFor(payment);
        invoice.recordPayment(payment.amount());
        auditTrail.recordPayment(payment);
    }

    int hasOpenDisputes(Invoice invoice) {
        int unresolvedCount = 0;
        for (Dispute dispute : invoice.disputes()) {
            if (!dispute.isResolved()) {
                unresolvedCount++;
            }
        }
        return unresolvedCount;
    }

    /** Returns a test that holds for an invoice still unpaid after its due date, as of the given day. */
    Predicate<Invoice> isOverdueOn(LocalDate asOf) {
        return invoice -> invoice.dueDate().isBefore(asOf)
                && invoice.outstanding().signum() > 0;
    }

    BigDecimal computeLateFee(Invoice invoice, LocalDate asOf) {
        long daysLate = ChronoUnit.DAYS.between(invoice.dueDate(), asOf);
        if (daysLate <= 0) {
            return BigDecimal.ZERO;
        }
        BigDecimal d = invoice.outstanding()
                .multiply(DAILY_LATE_FEE_RATE)
                .multiply(BigDecimal.valueOf(daysLate));
        return d.min(MAX_LATE_FEE);
    }

    void reconcilePayments(Customer customer, List<Payment> payments) {
        BigDecimal tmp = balanceOf(customer);
        for (Payment payment : payments) {
            Invoice invoice = invoiceFor(payment);
            invoice.recordPayment(payment.amount());
            receipts.send(customer.email(), invoice.number(), payment.amount());
        }

        List<Invoice> stillOpen = unpaidInvoicesOf(customer);
        if (!stillOpen.isEmpty()) {
            reminders.schedule(customer, stillOpen);
        }

        auditTrail.recordReconciliation(customer.id(), tmp, balanceOf(customer));
    }

    List<Invoice> unpaidInvoicesOf(Customer customer) {
        List<Invoice> unpaid = new ArrayList<>();
        for (Invoice invoice : invoicesByNumber.values()) {
            if (invoice.customerId().equals(customer.id()) && invoice.outstanding().signum() > 0) {
                unpaid.add(invoice);
            }
        }
        return unpaid;
    }

    private Invoice invoiceFor(Payment payment) {
        Invoice invoice = invoicesByNumber.get(payment.invoiceNumber());
        if (invoice == null) {
            throw new UnknownInvoiceException(payment.invoiceNumber());
        }
        return invoice;
    }
}
