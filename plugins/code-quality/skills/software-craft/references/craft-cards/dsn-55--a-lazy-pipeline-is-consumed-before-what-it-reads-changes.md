---
title: A lazy pipeline is consumed, and consumed before its source or a variable its steps read changes
rule_id: DSN-55
domain: design
step: [implement]
applies_to: [functional]
triggers: ['^\s*([\w.]|\(([^()]|\([^()]*\))*\))*\b(stream|parallelStream|iter|iter_mut|into_iter|values|keys|entries|chars|lines|of|from)\(([^()]|\([^()]*\))*\)\s*[.]\s*(map|filter|flatMap|flat_map|filter_map|peek|inspect|take|drop|skip|zip)\(', '=\s*([\w.]|\(([^()]|\([^()]*\))*\))+[.](stream|parallelStream|iter|iter_mut|into_iter|values|keys|entries|chars|lines|of|from)\(([^()]|\([^()]*\))*\)\s*[.]\s*(map|filter|flatMap|flat_map|filter_map|peek|inspect|take|drop|skip|zip)\(', '\b(Stream|IntStream|LongStream|DoubleStream)\b(<[^=]*>)?\s+\w+\s*=[^=]', '(^\s*|=\s*)(map|filter|zip|itertools[.]\w+)\(', '(^\s*|=\s*)\(.*\bfor\b.*\bin\b.*\)\s*$', ':=\s*(maps|slices|strings|bytes)[.](Keys|Values|All|Backward|Lines|\w+Seq)\(']
scope: file
check_kind: semantic
severity_default: major
---

# A lazy pipeline is consumed, and consumed before its source or a variable its steps read changes

## Thesis
Every lazy pipeline — a source followed by steps that run only when a consumer pulls elements, such as a stream, an iterator-adapter or iterator-helper chain, a generator expression, a lazy map, filter or zip, or the sequence an iterator routine returns — reaches a consumer that pulls its elements: an eager terminal operation, a loop over it, or a call that iterates it; a terminal operation that returns an iterator hands the pipeline on unconsumed. It is consumed before any statement changes its source or a variable or field its steps read. Consuming it in the expression that builds it — iterating it there, reducing it, or materializing it into a collection — meets both conditions by construction. A pipeline that is built and never consumed, and a stored pipeline consumed only after such a change, break the rule.

## Rationale
A pipeline's intermediate steps do no work when they are written: each returns a new pipeline, traversal of the source begins only when a consumer pulls elements, and it goes only as far as the consumer pulls. A pipeline built and never consumed therefore does nothing — its callbacks never run, and a step that skips elements does not advance the source — which is sometimes a source of confusion when a pipeline is built solely for its side effects; where only the effects are wanted, a loop or a for-each call is the idiomatic consumer. Compilers and checkers report a discarded pipeline: one compiler warns that iterators are lazy and do nothing unless consumed, one checker reports an ignored stream result at error severity, and one lint's recommended set reports a discarded iterator helper, including one marked void or awaited, since neither consumes it. A stored pipeline reads late: its source and the variables its steps refer to are read when elements are pulled, not when it is built, so a change made between building and consuming it shows up in the result — a list extended after its stream is built yields the added element too. In a language that evaluates a generator expression's outermost source expression immediately and every other expression only when a value is requested, rebinding the source's name afterwards changes nothing, while assigning to a variable another clause reads changes the result. These binding issues are hard to understand, so the guidance for such expressions is to use them inside a call that consumes them immediately and, for more complex cases, to write a full generator routine, which makes scope, lifetime and binding obvious. Materializing a pipeline moves its work: an eager terminal operation completes its traversal of the source and its processing of the pipeline before it returns, while a pipeline a loop consumes is pulled only until the loop breaks, returns or throws, so adding or removing a materialization changes when the steps run and for how many elements. One lint therefore offers removing a materialization before a loop only as a suggestion rather than an automatic fix, and offers turning a discarded map into a for-each call only as a suggestion too, because that starts consuming the pipeline. The rule restores the property that a pipeline is evaluated, and evaluated on the state the code held when it built the pipeline.

## Example
```java
bad:  keys.stream().map(cache::remove);
      Stream<Job> due = jobs.stream().filter(Job::isDue);
      jobs.clear();
      run(due.toList());
good: keys.forEach(cache::remove);
      List<Job> due = jobs.stream().filter(Job::isDue).toList();
      jobs.clear();
      run(due);
```

## Limits
Eager collection methods, which call their callback once for each element and build a new collection before they return, and a comprehension that builds a list rather than an iterator, run where they are written and are outside the rule. A routine written to return a lazy sequence — a generator routine, or an iterator routine named for the sequence it walks — hands its consumption to the caller, so its own body is outside the rule, while a caller that stores the sequence it returns is within it. A consumer that stops early, such as a find-first or a loop with a break, consumes the pipeline: laziness lets it examine only the elements it needs. A change made to its source, or to a variable or field its steps read, while the pipeline runs — by its own steps or by the body of the loop that consumes it — is a different defect, which the rule does not reach; it reads only the statements between building the pipeline and consuming it.

## Validator
Grep the added lines for a pipeline chain written as a statement, a chain of lazy steps or a lazy map, filter or zip call bound to a variable, a generator expression written as a statement or bound to a variable, a variable declared with a lazy stream type, and a variable bound to the sequence an iterator routine returns. For each hit, open the file and decide whether the construct is lazy; skip an eager collection method, a comprehension that builds a list, and a chain that ends in an eager consumer within the same statement; a chain that ends in a terminal operation returning an iterator is a stored pipeline. For a pipeline written as a statement that ends in no consumer, its value is unused, also when it is marked void or awaited. For a pipeline bound to a variable or a field, trace every use of that variable to the point where an eager terminal operation, a loop or an iterating call pulls its elements; a variable with no such use leaves the pipeline unconsumed. Between the binding and each consumption, look for a statement that adds to, removes from, clears or replaces elements of the source, or assigns to a variable or field that a step reads. Skip a rebinding of the name of a source that was evaluated when the pipeline was built, a routine whose purpose is to return a lazy sequence, and a consumer that stops early. Validator question: **Does an added line build a lazy pipeline that nothing consumes, or store one that is consumed only after a statement changes its source or a variable or field its steps read?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DSN-55`, severity major, `file`, `symbol`, `code` = the line that builds the unconsumed or stored pipeline and, for a stored one, the line that changes what it reads, quoted verbatim from the diff, `fix` = the pipeline given a consumer — an eager terminal operation, or a loop or for-each call where only its effects are wanted — or consumed or materialized before the change, in the file's language, `rationale` = which steps never run, or which change made between building and consuming the pipeline shows up in its result).
