export interface Subscription {
  id: string;
  /** The plan tier as stored in the billing database. */
  tier: string;
  seats: number;
  region: string;
}

export const TEAM_SEAT_PRICE = 8;
export const ENTERPRISE_SEAT_PRICE = 21;
export const EU_SEAT_SURCHARGE = 2;
export const AP_SEAT_SURCHARGE = 1;

export function monthlyPriceFallsBackToZero(sub: Subscription): number {
  switch (sub.tier) {
    case "free":
      return 0;
    case "team":
      return sub.seats * TEAM_SEAT_PRICE;
    case "enterprise":
      return sub.seats * ENTERPRISE_SEAT_PRICE;
    default:
      return 0; // unreachable: the billing schema admits only these three tiers
  }
}

/** Per-seat surcharge by region; the price list defines one only for the regions named here. */
export function regionSurchargeDefaultsToNone(sub: Subscription): number {
  switch (sub.region) {
    case "eu-central":
      return sub.seats * EU_SEAT_SURCHARGE;
    case "ap-south":
      return sub.seats * AP_SEAT_SURCHARGE;
    default:
      return 0; // every other region carries no surcharge by design
  }
}
