---
title: A call that a change adds depends on no property of the callee that its name or comment suggests but its body contradicts
rule_id: DOC-02
domain: docs
step: [implement, review]
applies_to: [universal]
triggers: ['\b(?:(?:is|has|can|should|check|validate|get|find|to|as)(?:[A-Z]|_)|(?:Is|Has|Can|Should|Check|Validate|Get|Find)[A-Z])\w*\s*\(']
scope: callers
check_kind: semantic
severity_default: major
---

# A call that a change adds depends on no property of the callee that its name or comment suggests but its body contradicts

## Thesis
A call that a change adds relies on a property of an existing callee (that it changes no state, that it may be called more than once or in another order, what it returns on each path the caller handles, what it raises) only where the callee's body does not contradict it; a property stated by a documentation example that the test run executes holds for the inputs the example shows. An added call that depends on a property which the callee's name or comment suggests and its body contradicts is a finding; a name or comment that agrees with the body may be relied on as it stands.

## Rationale
A name or comment that agrees with the body works as a beacon: in an fMRI study with 11 participants, comprehension based on semantic cues showed lower activation of brain areas, confirming that beacons ease comprehension. A name or comment that disagrees with the body misleads. In an exploratory study of how developers seek, relate and collect relevant information during maintenance tasks, the code summaries they judged relevance by were often misrepresentative of the content, the most glaring cases being misleading names: on one task, half the developers first inspected one class while the file actually relevant was a generically named other. In a study measuring cognitive load with functional near-infrared spectroscopy, mapped to identifiers by eye tracking, the presence of linguistic antipatterns in source code significantly increased developers' cognitive load. Keeping comments up to date during code changes requires substantial time and attention, and comments not kept in sync with the code they document have been studied across 1.3 billion AST-level changes from the history of 1,500 systems. Documentation examples run as tests are checked against the code: a doc-test tool executes the examples to verify that they work exactly as shown, and an example with an output comment is compared with the standard output when the tests run.

## Example
```python
bad:  def find_user(key):
          """Return the user, or None when absent."""
          return users[key]
      user = find_user(key)
      if user is None: ...
good: try:
          user = find_user(key)
      except KeyError: ...
```

## Limits
An added call that relies on a name or comment the body agrees with is correct; that is the beacon case. A write that only caches or lazily initializes a value that a fresh computation on each later call would return unchanged is no state change an added call depends on. Whether a caller may trust a callee's name or interface comment without reading its body is contested. One side holds that trusting well-chosen names and interface comments spares reading every callee recursively; its evidence is that beacons ease comprehension. The other side holds that a name or comment is potential misinformation to be cross-checked against the code; its evidence is that misleading names misdirect developers, linguistic antipatterns raise cognitive load, and comments fall out of sync with the code they document. The two separate on whether the name or comment agrees with the body, and the card flags only the case where the body contradicts the property the added call depends on. A documentation example that the test run executes counts as a checked contract for the inputs it shows; an example that is compiled but not executed checks no output. A callee whose body cannot be opened from the codebase, such as a third-party or platform interface, is outside the card. Correcting the callee's misleading name or comment is a fix to the callee, judged separately; the card judges the added call.

## Validator
List the calls the hunk adds; the triggers catch query-, check-, lookup- and conversion-named calls, and every other added call is in scope too. For each, open the callee's definition at the card's scope and read its name, its documentation comment and its body, following the routines the body calls; where the call dispatches through an interface, abstract or overridable method, read the body of each implementation in the codebase that the call can reach instead of the declaration's. Name the property the new caller depends on: the call sits in a condition, an assertion, a log line, a loop or a retry, or is made twice (no state change other than a cached or lazily initialized value that a fresh computation on each later call would return unchanged); the caller tests for an absent-value result (the returned value); the caller handles one error type (the raised error). Trace the body for writes to fields, globals, caches, files or external services, and for every return and raise path. Accept a property stated by a documentation example the test run executes, for the inputs the example shows. Validator question: **Does a call the hunk adds depend on a property of the callee that the callee's name or comment suggests and its body contradicts?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: DOC-02`, severity major, `file`, `symbol`, `code` = the added call, verbatim from the diff, `fix` = the call rewritten to rely on what the body does, handling the error it raises or calling a routine whose body has the property, in the file's language, `rationale` = the property the call depends on, the name or comment that suggests it, and the callee's body line that contradicts it).

## Source
- 'An Exploratory Study of How Developers Seek, Relate, and Collect Relevant Information during Software Maintenance Tasks', IEEE TSE 32(12):971-987, 2006, DOI 10.1109/TSE.2006.116, §4.4 'Forming Perceptions of Relevance', p. 977 (fetched): "One problem with these summaries was that they were often misrepresentative of the content. The most glaring examples of this in our data involved misleading names. For example, when developers worked on the YELLOW task, half of them first inspected the PencilPaint class, but the file that was actually relevant was the generically named PaintWindow."
- ESEC/FSE 2017, 'Measuring neural efficiency of program comprehension', DOI 10.1145/3106237.3106268, abstract (fetched): "a study using functional magnetic resonance imaging (fMRI) with 11 participants" ... "lower activation of brain areas during comprehension based on semantic cues, confirming that beacons ease comprehension."
- ICPC 2018, 'The effect of poor source code lexicon and readability on developers' cognitive load', DOI 10.1145/3196321.3196347, abstract (fetched): "functional Near Infrared Spectroscopy (fNIRS)" ... "we map cognitive load data to source code identifiers using an eye tracking device. Our results show that the presence of linguistic antipatterns in source code significantly increases the developers' cognitive load."
- ICPC 2019, 'A Large-Scale Empirical Study on Code-Comment Inconsistencies', pp. 53-64, DOI 10.1109/ICPC.2019.00019, abstract (fetched): "Keeping comments up-to-date during code change activities requires substantial time and attention." ... "(i.e., comments that are not kept in sync with the code they document)" ... "mining 1.3 Billion AST-level changes from the complete history of 1,500 systems."
- Python documentation, doctest, introduction (fetched): "executes those sessions to verify that they work exactly as shown" ... "To check that a module's docstrings are up-to-date by verifying that all interactive examples still work as documented."
- rustdoc book, 'Documentation tests' (fetched): "`rustdoc` supports executing your documentation examples as tests. This makes sure that examples within your documentation are up to date and working."
- Go package testing, '# Examples' (fetched): "Example functions may include a concluding line comment that begins with "Output:" and is compared with the standard output of the function when the tests are run." ... "Example functions without output comments are compiled but not executed."
- Caveat: the four studies measure where developers look, how hard they work and how comments co-evolve with code; none counts defects in new calls, so the card rests the cost of a contradicted name or comment on misdirection and cognitive load.
