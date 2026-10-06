export interface Subscription {
  id: string;
  /** The plan tier as stored in the billing database. */
  tier: string;
  seats: number;
  region: string;
}

export const TEAM_SEAT_PRICE = 8;
export const ENTERPRISE_SEAT_PRICE = 21;

const SEAT_PRICE: Record<string, number> = { free: 0, team: TEAM_SEAT_PRICE, enterprise: ENTERPRISE_SEAT_PRICE };

export function monthlyPrice(sub: Subscription): number {
  const price = SEAT_PRICE[sub.tier];
  if (price === undefined) throw new Error(`monthly price of subscription ${sub.id}: unknown tier ${sub.tier}`);
  return sub.seats * price;
}
