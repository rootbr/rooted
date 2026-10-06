/** A carrier's price in euros for a parcel; the production adapter calls the carrier's HTTP rate API. */
export interface CarrierApi {
  quote(country: string, kg: number): Promise<number>;
}

export class HttpCarrierApi implements CarrierApi {
  constructor(private readonly baseUrl: string) {}

  async quote(country: string, kg: number): Promise<number> {
    const response = await fetch(`${this.baseUrl}/rates?country=${country}&kg=${kg}`);
    if (!response.ok) {
      throw new Error(`carrier rate lookup for ${country}/${kg}kg failed with ${response.status}`);
    }
    return (await response.json()).price;
  }
}

export class ShippingQuotes {
  constructor(private readonly primary: CarrierApi, private readonly fallback?: CarrierApi) {}

  async quote(country: string, kg: number): Promise<number> {
    try {
      return await this.primary.quote(country, kg);
    } catch (err) {
      if (!this.fallback) {
        throw err;
      }
      return this.fallback.quote(country, kg);
    }
  }
}
