import { Pool } from "pg";

export interface Order {
  id: string;
  customer: string;
  total: number;
  placedAt: Date;
}

export class DuplicateOrderError extends Error {}

/** save() rejects with DuplicateOrderError for an id already stored; findByCustomer() lists newest first. */
export interface OrderRepository {
  save(order: Order): Promise<void>;
  findByCustomer(customer: string): Promise<Order[]>;
}

export class PgOrderRepository implements OrderRepository {
  constructor(private readonly pool: Pool) {}

  async save(order: Order): Promise<void> {
    try {
      await this.pool.query(
        "INSERT INTO orders (id, customer, total, placed_at) VALUES ($1, $2, $3, $4)",
        [order.id, order.customer, order.total, order.placedAt],
      );
    } catch (err) {
      if ((err as { code?: string }).code === "23505") {
        throw new DuplicateOrderError(`order ${order.id} already exists`);
      }
      throw err;
    }
  }

  async findByCustomer(customer: string): Promise<Order[]> {
    const { rows } = await this.pool.query(
      "SELECT id, customer, total, placed_at FROM orders WHERE customer = $1 ORDER BY placed_at DESC",
      [customer],
    );
    return rows.map((row) => ({ id: row.id, customer: row.customer, total: Number(row.total), placedAt: row.placed_at }));
  }
}

export class OrderHistory {
  constructor(private readonly orders: OrderRepository) {}

  async latestFor(customer: string): Promise<Order | undefined> {
    const [latest] = await this.orders.findByCustomer(customer);
    return latest;
  }
}
