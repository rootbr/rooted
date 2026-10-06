import { CarrierApi, ShippingQuotes } from "./shipping";

test("shippingQuoteComesFromThePrimaryCarrier", async () => {
  const primary: jest.Mocked<CarrierApi> = { quote: jest.fn().mockResolvedValue(12) };
  await expect(new ShippingQuotes(primary).quote("DE", 2)).resolves.toBe(12);
});
