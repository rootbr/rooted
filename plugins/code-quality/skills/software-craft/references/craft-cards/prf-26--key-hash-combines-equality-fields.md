---
title: A hash function that a type defines for its use as a map key or set element combines the fields its equality compares, and does not return a constant or hash only fields that many unequal keys share
rule_id: PRF-26
domain: performance
step: [implement]
applies_to: [universal]
triggers: ['\b(int|fun)\s+hashCode\s*\(\s*\)', '\bdef\s+__hash__\s*\(', '\bimpl\b[^{;]*?\bHash\s+for\b|\bfn\s+hash\s*<\s*H\b', '\bGetHashCode\s*\(\s*\)', '\bstd::hash\s*<|\bAbslHashValue\s*\(|\bsize_t\s+operator\(\)\s*\(', '\bfunc\s+hash\s*\(\s*into\b|\bvar\s+hashValue\b|\bdef\s+(hash|hashCode)\b']
scope: file
check_kind: semantic
severity_default: minor
---

# A hash function that a type defines for its use as a map key or set element combines the fields its equality compares, and does not return a constant or hash only fields that many unequal keys share

## Thesis
A type whose instances serve as keys of a hashed map or elements of a hashed set, with the fields its equality compares set before an instance enters the collection, computes its hash by mixing together the hash values of the components that take part in its equality, for example by hashing a tuple of them. Its hash does not return a constant, and does not hash only fields whose values many unequal keys share while equality compares further fields.

## Rationale
A hashed map or set computes an object's bucket from its hash value before it calls equality, and using many keys with the same hash value is a sure way to slow down the performance of any hash table. With a good hash function a search takes constant time, O(1); with a poor one the time of a search depends on the number of items in the table, O(n). One language standard bounds a lookup in its unordered containers at O(1) on average and O(size) in the worst case. A constant hash gives every key the same value, and a hash of one field gives the same value to every key that shares that field; a platform's default value-type hash, which uses one or more of the type's fields, is documented as not likely to be suitable for use as a key in a hash table. Objects that compare equal must have the same hash value, while unequal objects are not required to have distinct ones; producing distinct values for unequal objects may improve the performance of hash tables. The advised construction mixes together the hash values of the components that play a part in comparison, for example by packing them into a tuple and hashing the tuple, and values which are not equal should cause different sequences of values to be written to the hasher. For the best performance a hash function should generate an even distribution for all input, including heavily clustered input, and the probability that two different values share a hash value should be very small, approaching one divided by the largest value of the hash type.

## Example
```rust
bad:  #[derive(PartialEq, Eq)] struct Key { a: u32, b: u32 }
      impl Hash for Key {
          fn hash<H: Hasher>(&self, state: &mut H) { 0u8.hash(state) }
      }
good: #[derive(PartialEq, Eq)] struct Key { a: u32, b: u32 }
      impl Hash for Key {
          fn hash<H: Hasher>(&self, state: &mut H) { (self.a, self.b).hash(state) }
      }
```

## Limits
The rule reaches types placed in a hashed map or set. A type whose instances are never inserted into one may return an arbitrary constant from its hash together with an assertion that the hash is not designed to be called. When one field alone decides equality, hashing that field satisfies the rule. Fields that equality ignores stay out of the hash, because objects that compare equal must have the same hash value. Leaving one compared field out of the hash breaks no contract and can reduce how well hash values spread across buckets; it is a finding only when many unequal keys then share a value. Regular hash values are not necessarily bad: with an integer hash that maps small integers to themselves, taking the low-order bits as the initial table index is extremely fast, and a contiguous range of integer keys has no collisions at all. Some hashed maps may use comparison order to break ties among keys with the same hash value, which provides worst-case O(log n) operations when the keys are orderable; performance there degrades gracefully when many keys share a hash value, so long as those keys are orderable.

Contested for entities whose equality rests on a generated identifier. A hashed set expects an object's equality and hash value not to change while the object is a member, and a generated identifier can be assigned after the entity is added to the set; returning a constant from the hash is the usual workaround, so that assigning the identifier does not change the hash code, and comparing identifiers for equality only for non-transient entities. A natural id is a useful basis for equality and hash, with the business key assigned before an instance is added to a hashed collection and stable while it is a member. The separating condition is whether the fields equality compares are fixed before the object enters a hashed collection: when they are, the runtime, language and standard documentation call for a hash that mixes them; for an entity whose only identity is a generated identifier assigned after insertion, the constant hash is the documented exception.

## Validator
Grep the hunk for a definition of a type's hash: a hash method, a hash trait implementation or a method generic over a hasher, a hash specialization, a hash hook or a hash functor. Open the type at file scope and list the fields its equality compares. Read the hash body and note what it feeds the hash: a literal constant, a subset of the compared fields, or all of them. When it hashes a subset, trace the values the hashed fields take across instances (an enumeration, a flag, a category, an owner or parent reference) and whether many unequal keys share them. Skip a constant hash that carries an assertion that it is never called, an entity whose equality rests on a generated identifier assigned after it may enter a hashed collection, and a hash of the one field that alone decides equality. Validator question: **Does the hash function return a constant, or hash only fields whose values many unequal keys share while the type's equality compares further fields?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PRF-26`, severity minor, `file`, `symbol`, `code` = the hash body line that returns the constant or hashes only the shared fields, `fix` = the hash rewritten to mix the fields equality compares, as a hashed tuple or a combined hash in the file's language, `rationale` = names the compared fields the hash leaves out and the many-keys-one-bucket slowdown of every insert and lookup).
