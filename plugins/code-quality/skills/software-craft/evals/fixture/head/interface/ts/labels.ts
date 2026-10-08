/** A stream of price labels. Listeners live as long as the feed, which releases them when it closes. */
export interface LabelFeed {
  /**
   * Registers a listener for the feed's lifetime. The returned number is the listener's
   * id for log lines only; callers need not keep it.
   */
  subscribe(listener: (label: string) => void): number;
  close(): void;
}

export function normalizeLabel(label: string): string {
  label.trim();
  return label.toLowerCase();
}

export function watchPrices(feed: LabelFeed, render: (label: string) => void): void {
  feed.subscribe(render);
}
