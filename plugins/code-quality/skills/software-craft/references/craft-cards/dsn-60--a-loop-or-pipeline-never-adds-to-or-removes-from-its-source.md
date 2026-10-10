---
title: A loop body or pipeline step never adds to or removes from the collection it is traversing
rule_id: DSN-60
domain: design
step: [implement]
applies_to: [universal]
triggers: ['[.](forEach|for_each|map|flatMap|flat_map|filter|peek|some|every|find|reduce|inspect)\(.*\b\w+[.](add|push|remove|splice|append|insert|pop|shift|unshift|clear|delete|discard)\(', '[.](remove|removeAll|retainAll|delete|discard|splice|pop|popitem|shift|unshift|insert|clear)\(', '^\s*(del|delete)\s+[\w.]+\[', '\bdelete\(\s*\w+\s*,', '\b(append\(\s*\w+\[:\s*\w+\s*\]|slices[.](Delete|Insert)\()']
scope: file
check_kind: semantic
severity_default: major
---

# A loop body or pipeline step never adds to or removes from the collection it is traversing

## Thesis
A loop body, and every step of a pipeline, adds no element to and removes no element from the collection that the loop or the pipeline is traversing, whether it modifies that collection directly, through another reference to it, or through a view of its keys, values or entries. When elements must be added or removed, the code loops over a copy of the collection, creates a new collection, or makes the change through a call documented for it: the iterator's own removal or insertion call, or an in-place removal call that takes a predicate. A collection specifically designed to handle concurrent modification is outside the rule.

## Rationale
A traversal reads its collection while it runs: an array method visits only the indexes below the length the array had when the call began, passing each element's value as it stands when its index is reached, and a lazy pipeline reads its source from the moment its terminal operation is invoked until that operation completes. A change of size made by the traversal's own step therefore changes what the remaining steps see, so the traversal can skip, repeat or unexpectedly visit items. An element removed before it is reached is never visited, and the last steps reach past the shrunken end; an element inserted at a position already passed shifts the elements after it, so elements already visited are visited again; an element appended beyond the starting length is not visited by an array method, while in one language a map's or a set's for-each traversal visits entries added after it began and visits an entry again when it is deleted after its visit and added back. In one language whose map iteration order is unspecified, an entry created during iteration may be produced or skipped, and the choice may vary for each entry and from one iteration to the next. Some collections raise an error when entries are added or deleted during iteration, or fail to iterate over all entries; one such error is thrown only on a best-effort basis, so a program cannot depend on it for its correctness, and it should be used only to detect bugs. A pipeline step that modifies, or causes to be modified, a source not designed for concurrent modification interferes with it whether the pipeline runs sequentially or in parallel, and the modification can cause an exception, an incorrect answer or nonconformant behaviour. Looping over a copy of the collection, or creating a new collection, is usually the more straightforward course, and one library documents its in-place removal call as visiting each element exactly once in the original order. A compiler that tracks borrows enforces the rule for a vector: the reference the loop holds prevents an insertion or a removal in the loop body.

## Example
```java
bad:  for (Task task : tasks) {
          if (task.isDone()) tasks.remove(task);
      }
good: List<Task> pending = tasks.stream()
          .filter(task -> !task.isDone())
          .toList();
```

## Limits
Where an iterator offers its own removal or insertion call, that call is the documented way to change the collection while iterating over it; one library leaves an iterator's behaviour unspecified when its collection is modified in any other way. An in-place removal call that takes a predicate traverses the collection itself and removes each matching element, so it is outside the rule unless it is called from inside a loop or a pipeline over that same collection. Replacing the value stored at an existing index or key is not a structural modification and is outside this rule. A counted loop that reads the collection by position and holds no iterator over it is outside the rule when every position it reads stays valid across the change: removing from the last position down, or appending to a work queue whose bound re-reads the length on every pass; a counted loop that removes at its current position and then advances skips the next element and stays inside the rule. Updating or deleting the entry currently being visited in a map or a set, where the language specifies how its iteration treats a deleted entry, is outside the rule, as one linter accepts; deleting an entry and adding it back in the same pass is inside it, because the re-added entry can be visited again. A collection whose iteration may raise an error or fail to visit every entry when entries are deleted keeps even the current-entry deletion inside the rule. A change made by another thread is a concurrency question outside this rule, which covers what a loop body or a pipeline step does to the collection it traverses.

## Validator
Grep the added lines for a call or statement that adds to or removes from a collection — remove, delete, discard, pop, shift, unshift, splice, insert, clear, add, push, append, put or set, an assignment that stores a value under a key or index, a deletion statement, a slice reassembled around an index — and for a pipeline callback that makes one. For each hit, read the enclosing routine for the loop header or the pipeline that encloses it and name the collection it traverses; trace the receiver of the call back to that collection through local aliases and through views of its keys, values or entries. Skip the hit when the loop or pipeline traverses a copy taken before it began, when the receiver is a new collection the traversal builds, when the collection is designed for concurrent modification, when the call is the iterator's own removal or insertion call, when the hit replaces the value at an existing index or key, and when the loop is a counted loop that reads the collection by position and every position it reads stays valid across the change. Skip a deletion of the entry currently visited from a map or a set whose language specifies how its iteration treats a deleted entry, unless the same pass adds that entry back or the collection's iteration may raise an error or fail to visit every entry when entries are deleted. Validator question: **Does an added line inside a loop body or a pipeline step add an element to, or remove an element from, the collection that loop or pipeline is traversing, other than through the iterator's own call or a collection designed for concurrent modification?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-60`, severity major, `file`, `symbol`, `code` = the added line that adds to or removes from the traversed collection, quoted verbatim from the diff, `fix` = the same change made by looping over a copy, by creating a new collection, or through the iterator's own removal call or an in-place removal call that takes a predicate, in the file's language, `rationale` = the collection being traversed and what the change can do to the traversal: skip, repeat or add an element, raise an error, or vary from one run to the next).
