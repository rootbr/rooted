/// An amount of money in cents of the ledger currency.
#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub struct Money {
    cents: i64,
}

impl Money {
    pub fn from_cents(cents: i64) -> Self {
        Money { cents }
    }

    pub fn cents(&self) -> i64 {
        self.cents
    }
}

pub struct InvoiceLine {
    pub description: String,
    pub amount: Money,
}

pub struct Invoice {
    lines: Vec<InvoiceLine>,
}

impl Invoice {
    pub fn new() -> Self {
        Invoice { lines: Vec::new() }
    }

    pub fn add_line(&mut self, line: InvoiceLine) {
        self.lines.push(line);
    }
}
