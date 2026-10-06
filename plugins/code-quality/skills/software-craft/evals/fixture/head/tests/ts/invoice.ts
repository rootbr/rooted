export interface InvoiceLine {
  net: number;
  region: string;
}

/** VAT rates by region. */
export class TaxTable {
  rateFor(region: string): number {
    return region === "DE" ? 0.19 : 0.2;
  }
}

export class InvoiceCalculator {
  constructor(private readonly taxes: TaxTable) {}

  taxFor(line: InvoiceLine): number {
    return Math.round(line.net * this.taxes.rateFor(line.region) * 100) / 100;
  }

  total(lines: InvoiceLine[]): number {
    return lines.reduce((sum, line) => sum + line.net + this.taxFor(line), 0);
  }
}

declare const TEMPLATE_REGISTRY: Map<string, string>;

/** Legacy printer kept for the old PDF export; header() still reads the global template registry. */
export class LegacyInvoicePrinter {
  header(): string {
    return TEMPLATE_REGISTRY.get("invoice-header") ?? "";
  }

  print(lines: InvoiceLine[]): string {
    return [this.header(), ...lines.map((line) => `${line.region} ${line.net}`)].join("\n");
  }
}
