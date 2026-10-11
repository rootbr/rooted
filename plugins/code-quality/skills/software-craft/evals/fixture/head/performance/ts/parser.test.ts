import { parseAmount } from "./parser";

describe("parseAmount", () => {
  it.only("rejectsEmptyInput", () => {
    expect(() => parseAmount("")).toThrow("empty");
  });

  it("acceptsOnlyAsciiDigits", () => {
    expect(parseAmount("12.50")).toBe(1250);
    expect(() => parseAmount("１２")).toThrow("digit");
  });
});
