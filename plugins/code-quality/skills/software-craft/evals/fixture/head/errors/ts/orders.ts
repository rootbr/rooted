export interface Order {
  id: string;
  total: number;
}

export interface OrderStore {
  save(order: Order): Promise<void>;
  prefetch(id: string): Promise<void>;
}

export async function saveDraftSwallowsError(store: OrderStore, order: Order): Promise<void> {
  try {
    await store.save(order);
  } catch (err) {}
}

export function prefetchOrderIgnoresMissByDesign(store: OrderStore, id: string): void {
  store.prefetch(id).catch(() => {
    // prefetch only warms a cache: a miss costs one fetch when the order is first opened
  });
}
