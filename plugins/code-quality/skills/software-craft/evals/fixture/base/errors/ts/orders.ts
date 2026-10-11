export interface Order {
  id: string;
  total: number;
}

export interface OrderStore {
  save(order: Order): Promise<void>;
  prefetch(id: string): Promise<void>;
}

export async function saveDraft(store: OrderStore, order: Order): Promise<void> {
  await store.save(order);
}

export function prefetchOrder(store: OrderStore, id: string): void {
  void store.prefetch(id);
}
