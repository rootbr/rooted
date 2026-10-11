export function parseAmount(text: string): number {
  if (text === "") {
    throw new Error("empty amount");
  }
  if (!/^[0-9]+(\.[0-9]{2})?$/.test(text)) {
    throw new Error("amount needs ascii digits");
  }
  const [whole, cents = "00"] = text.split(".");
  return Number(whole) * 100 + Number(cents);
}
