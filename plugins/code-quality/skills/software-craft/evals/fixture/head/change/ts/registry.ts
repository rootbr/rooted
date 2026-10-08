import "./plugins"; // registers the built-in plugins when loaded; nothing is imported by name
import { registry } from "./codec";

export function pluginNames(): string[] {
  return registry.map((plugin) => plugin.name);
}
