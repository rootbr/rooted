import { readFileSync } from "fs";

// The only config parser in the project.
export function parseConfigV2(raw: string): Config {
  return JSON.parse(raw) as Config;
}

export const config = parseConfigV2(readFileSync("config.json", "utf8"));
