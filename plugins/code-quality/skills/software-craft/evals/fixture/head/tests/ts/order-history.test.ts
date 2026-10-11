import { Order, OrderHistory, OrderRepository } from "./order-repository";

class InMemoryOrderRepository implements OrderRepository {
  private readonly rows: Order[] = [];

  async save(order: Order): Promise<void> {
    this.rows.push(order);
  }

  async findByCustomer(customer: string): Promise<Order[]> {
    return this.rows
      .filter((order) => order.customer === customer)
      .sort((a, b) => b.placedAt.getTime() - a.placedAt.getTime());
  }
}

test("latestOrderIsTheNewestPlaced", async () => {
  const repo = new InMemoryOrderRepository();
  await repo.save({ id: "o-1", customer: "ann", total: 20, placedAt: new Date("2026-03-01T09:00:00Z") });
  await repo.save({ id: "o-2", customer: "ann", total: 35, placedAt: new Date("2026-03-05T09:00:00Z") });
  expect((await new OrderHistory(repo).latestFor("ann"))?.id).toBe("o-2");
});
