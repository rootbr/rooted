import { readFile, writeFile } from "node:fs/promises";
import { join } from "node:path";

/** Maps a session id to its user id; get() answers undefined for an unknown session. */
export interface SessionStore {
  put(sessionId: string, userId: string): Promise<void>;
  get(sessionId: string): Promise<string | undefined>;
}

/** The production store: one JSON file per session under a directory. */
export class FileSessionStore implements SessionStore {
  constructor(private readonly dir: string) {}

  async put(sessionId: string, userId: string): Promise<void> {
    await writeFile(join(this.dir, `${sessionId}.json`), JSON.stringify({ userId }), "utf8");
  }

  async get(sessionId: string): Promise<string | undefined> {
    try {
      return JSON.parse(await readFile(join(this.dir, `${sessionId}.json`), "utf8")).userId;
    } catch (err) {
      if ((err as NodeJS.ErrnoException).code === "ENOENT") {
        return undefined;
      }
      throw err;
    }
  }
}

export class SessionGuard {
  constructor(private readonly store: SessionStore) {}

  async currentUser(sessionId: string): Promise<string> {
    const userId = await this.store.get(sessionId);
    if (userId === undefined) {
      throw new Error(`no session ${sessionId}`);
    }
    return userId;
  }
}
