use std::ops::Add;

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

    /// Formats the amount as whole units and two-digit cents, such as `-12.05`.
    pub fn to_text(&self) -> String {
        let sign = if self.cents < 0 { "-" } else { "" };
        let magnitude = self.cents.unsigned_abs();
        format!("{sign}{}.{:02}", magnitude / 100, magnitude % 100)
    }
}

impl Add for Money {
    type Output = Money;

    fn add(self, other: Money) -> Money {
        Money::from_cents(self.cents + other.cents)
    }
}

pub struct InvoiceLine {
    pub description: String,
    pub amount: Money,
}

pub struct Invoice {
    lines: Vec<InvoiceLine>,
    cached_total: Option<Money>,
}

impl Invoice {
    pub fn new() -> Self {
        Invoice { lines: Vec::new(), cached_total: None }
    }

    pub fn add_line(&mut self, line: InvoiceLine) {
        self.lines.push(line);
        self.cached_total = None;
    }

    /// The sum of all line amounts, computed on first read and kept until a line is added.
    pub fn grand_total(&mut self) -> Money {
        if let Some(total) = self.cached_total {
            return total;
        }
        let total = self.lines.iter().fold(Money::from_cents(0), |sum, line| sum + line.amount);
        self.cached_total = Some(total);
        total
    }
}
