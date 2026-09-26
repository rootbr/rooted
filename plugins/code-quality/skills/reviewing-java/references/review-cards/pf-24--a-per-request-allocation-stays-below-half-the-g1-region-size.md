---
title: An object allocated per request or per batch stays below half the G1 region size, so it is not a humongous allocation; larger data is chunked, streamed or held in a reused buffer
rule_id: PF-24
domain: performance
triggers: ['new (byte|char|short|int|long|float|double|boolean|Object|String)\[\s*[^\]]*\d[\d_]{5,}', 'new \w+\[\s*\w+\s*\*\s*\w+', 'ByteBuffer[.]allocate\(', '\d+\s*\*\s*1024\s*\*\s*1024|<<\s*20', 'new ArrayList<>\(\s*\d{5,}', 'readAllBytes\(\)|toByteArray\(\)']
scope: file
check_kind: semantic
severity_default: minor
---

# An object allocated per request or per batch stays below half the G1 region size, so it is not a humongous allocation; larger data is chunked, streamed or held in a reused buffer

## Thesis
A buffer, array or collection backing array that code allocates on a per-request, per-message or per-batch path is smaller than half of a G1 heap region — with default region sizing regions run from 1 MB on small heaps to 32 MB on large ones, so the threshold is 512 KB on a small heap and up to 16 MB on a large one. Data larger than that is processed in chunks, streamed, or held in a long-lived buffer allocated once and reused.

## Rationale
The default collector treats any object larger than half a region as humongous: it is allocated directly into one or more contiguous regions outside the young generation, bypassing the thread-local allocation buffer and the bump-pointer fast path, and it occupies whole regions — the tail of its last region stays unused — until a collection reclaims them. A per-request humongous allocation therefore takes the slow allocation path each time, fragments the heap into partially used regions, and can start a collection on its own: because humongous objects can exhaust the heap quickly, the collector checks at each humongous allocation whether a concurrent marking cycle needs to start, and collects when it does. With default region sizing the region is the maximum heap size divided by 2048, clamped to 1–32 MB and rounded up to a power of two, so an array of 100 000 `long` values (800 KB) or a 1 MB read buffer crosses the threshold on a heap of about 2 GB or less, where the region is 1 MB and the threshold 512 KB; a 1 MB buffer crosses it up to a 2 MB region, the default up to a 4 GB heap.

## Example
```java
bad:  byte[] body = in.readAllBytes();               // whole multi-megabyte upload in one array
      long[] ids = new long[2_000_000];              // per batch, 16 MB
good: byte[] chunk = new byte[64 * 1024];
      for (int n; (n = in.read(chunk)) > 0; ) process(chunk, n);
      // ids: process the batch in fixed-size pages, or reuse one long[] sized once
```

## Limits
A large array allocated once at startup and reused, a heap large enough that the region size puts the object under the threshold, and a collector other than G1 (ZGC, Shenandoah and Parallel handle large objects differently) are out of scope; the heap and collector are stated in the project context, and a tolerance there rejects the finding. An object whose size is unknown at review time is flagged only when the input it holds is unbounded (a whole request body, a whole file).

## Validator
On the triggered hunk find each allocation whose size is a large literal, a product of dimensions, or the length of an unbounded input (`readAllBytes`, `toByteArray`, a whole-file read). Open the file to confirm the allocation is per request, per message or per batch, and estimate the byte size (element size times length, plus the header). Validator question: **does this hot path allocate an object that can exceed half a G1 region — 512 KB on a small heap — on every request or batch?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: PF-24`, severity minor, `file`, `symbol`, `code` = the allocation quoted verbatim from the diff, `fix` = chunked or streamed processing, or a reused buffer, `rationale` naming the humongous slow path and the region fragmentation).

## Source
HotSpot `src/hotspot/share/gc/g1/g1CollectedHeap.hpp` (jdk-21-ga) — `is_humongous(word_size)` returns `word_size > _humongous_object_threshold_in_words`; `humongous_threshold_for(region_size)` returns `region_size / 2`; `g1CollectedHeap.cpp` sets the threshold from `HeapRegion::GrainWords`, allocates a humongous object as a series of contiguous regions ("humongous objects are not allocated in young") and pads "the unused tail of the last region with filler objects"; `attempt_allocation_humongous` — "Humongous objects can exhaust the heap quickly, so we should check if we need to start a marking cycle at each humongous object allocation": `need_to_start_conc_mark("concurrent humongous allocation", word_size)`, then `collect(GCCause::_g1_humongous_allocation)`. `src/hotspot/share/gc/g1/heapRegion.cpp` — `setup_heap_region_size`: with `G1HeapRegionSize` unset, the region is the maximum heap size divided by `TARGET_REGION_NUMBER`, clamped between `MIN_REGION_SIZE` and `MAX_ERGONOMICS_SIZE`, then rounded up to a power of two. `src/hotspot/share/gc/g1/heapRegionBounds.hpp` — `MIN_REGION_SIZE` 1 MB, `MAX_ERGONOMICS_SIZE` 32 MB, `TARGET_REGION_NUMBER` 2048 (`MAX_REGION_SIZE` 512 MB when set explicitly).
