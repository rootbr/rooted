import { mkdtemp } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { FileSessionStore, SessionGuard, SessionStore } from "./session-store";

class FakeSessionStore implements SessionStore {
  private readonly sessions = new Map<string, string>();

  async put(sessionId: string, userId: string): Promise<void> {
    this.sessions.set(sessionId, userId);
  }

  async get(sessionId: string): Promise<string | undefined> {
    return this.sessions.get(sessionId);
  }
}

// One contract suite runs against the fake and against the real store it stands in for.
describe.each([
  ["FakeSessionStore", async (): Promise<SessionStore> => new FakeSessionStore()],
  ["FileSessionStore", async (): Promise<SessionStore> => new FileSessionStore(await mkdtemp(join(tmpdir(), "sessions-")))],
])("SessionStore contract (%s)", (_name, makeStore) => {
  test("sessionStoreReturnsTheUserItWasGiven", async () => {
    const store = await makeStore();
    await store.put("s-1", "ann");
    expect(await store.get("s-1")).toBe("ann");
  });

  test("sessionStoreAnswersUndefinedForAnUnknownSession", async () => {
    const store = await makeStore();
    expect(await store.get("s-missing")).toBeUndefined();
  });
});

test("sessionGuardResolvesTheLoggedInUser", async () => {
  const store = new FakeSessionStore();
  await store.put("s-1", "ann");
  await expect(new SessionGuard(store).currentUser("s-1")).resolves.toBe("ann");
});
