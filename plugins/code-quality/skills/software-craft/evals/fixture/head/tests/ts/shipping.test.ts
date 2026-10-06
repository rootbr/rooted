import { CarrierApi, ShippingQuotes } from "./shipping";

test("shippingQuoteComesFromThePrimaryCarrier", async () => {
  const primary: jest.Mocked<CarrierApi> = { quote: jest.fn().mockResolvedValue(12) };
  await expect(new ShippingQuotes(primary).quote("DE", 2)).resolves.toBe(12);
});

test("shippingQuoteSurfacesPrimaryCarrierFailure", async () => {
  const primary: jest.Mocked<CarrierApi> = { quote: jest.fn().mockRejectedValue(new Error("carrier timeout")) };
  const fallback: jest.Mocked<CarrierApi> = { quote: jest.fn().mockResolvedValue(20) };
  const quotes = new ShippingQuotes(primary);
  await expect(quotes.quote("DE", 2)).rejects.toThrow("carrier timeout");
});

test("shippingQuoteLeavesFallbackUntouchedWhenPrimaryAnswers", async () => {
  const primary: jest.Mocked<CarrierApi> = { quote: jest.fn().mockResolvedValue(12) };
  const fallback: jest.Mocked<CarrierApi> = { quote: jest.fn() };
  await expect(new ShippingQuotes(primary, fallback).quote("DE", 2)).resolves.toBe(12);
  expect(fallback.quote).not.toHaveBeenCalled();
});
