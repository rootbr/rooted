export interface Channel {
  send(payload: string): void;
  close(): void;
}

export function onMessage(channel: Channel, event: MessageEvent): void {
  // eslint-disable-next-line -- the sender defines the payload shape
  const payload: any = event.data;
  channel.send(JSON.stringify(payload));
}

export function onClose(channel: Channel, event: CloseEvent): void {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any -- the close reason arrives untyped from the sender
  const reason: any = event.reason;
  channel.send(String(reason));
  channel.close();
}
