export interface Plugin {
  name: string;
}

export const registry: Plugin[] = [];

export function parse(text: string): string[] {
  return text.split("\n").filter((line) => line.length > 0);
}

export function format(lines: string[]): string {
  return lines.join("\n");
}
