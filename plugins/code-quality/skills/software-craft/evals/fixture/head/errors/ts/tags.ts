import { readdirSync, statSync } from "node:fs";

export interface Post {
  id: string;
  labels: string[];
}

export function hashtagsOfPostOrNull(post: Post): string[] | null {
  const tags = post.labels.filter((label) => label.startsWith("#"));
  if (tags.length === 0) {
    return null;
  }
  return tags.map((tag) => tag.slice(1));
}

/**
 * Lists the tag files in `dir`: an empty array when the directory holds none, and null when
 * `dir` is not a directory at all, a question with no answer that callers report as a bad path.
 */
export function listTagFilesNullWhenNotDirectory(dir: string): string[] | null {
  const stat = statSync(dir, { throwIfNoEntry: false });
  if (!stat?.isDirectory()) {
    return null;
  }
  return readdirSync(dir).filter((name) => name.endsWith(".tag"));
}
