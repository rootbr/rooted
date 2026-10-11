import { InvoiceCalculator, LegacyInvoicePrinter, TaxTable } from "./invoice";

test("invoiceTotalStubsItsOwnTaxMethod", () => {
  const calculator = new InvoiceCalculator(new TaxTable());
  jest.spyOn(calculator, "taxFor").mockReturnValue(19);
  expect(calculator.total([{ net: 100, region: "DE" }])).toBe(119);
});

test("legacyInvoicePrintPutsHeaderFirst", () => {
  // Legacy code, interim step while refactoring it: header() still reads the global template
  // registry; the spy goes once the header moves into a TemplateSource collaborator.
  const printer = new LegacyInvoicePrinter();
  jest.spyOn(printer, "header").mockReturnValue("ACME GmbH");
  expect(printer.print([{ net: 100, region: "DE" }])).toBe("ACME GmbH\nDE 100");
});
