---
title: A test double is built from the real type it replaces so that its shape is checked against that type
rule_id: TST-11
domain: tests
step: [test]
applies_to: [tests]
triggers: ['\b(Magic|Async|NonCallableMagic|NonCallable)?Mock\((?![^)]*\b(autospec|spec|spec_set)\s*=)', '\bpatch(?:[.]object|[.]multiple)?\((?![^)]*\b(spec|spec_set|new|new_callable)\s*=)(?![^)]*\bautospec\s*=\s*(?!False\b|None\b))', '\b(jest|vi)[.](mock|doMock)\([^)]*,\s*(\(|function|async)', '\bas\s+(unknown\s+as|any)\b', '\bdouble\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# A test double is built from the real type it replaces so that its shape is checked against that type

## Thesis
A test double that stands in for an existing class, function, interface or module is created from that type, so that its shape is checked against that type: a double built at run time rejects a member the real type does not have and, where it checks signatures, a call whose arguments do not fit the real signature; a double the compiler checks fails to compile once it no longer carries a member of the type, as after a rename. The forms that meet the rule are a mock specced from the real type (a signature-checking spec, or at least a member-list spec), a verifying double, a mock generated from the interface or trait, a module mock generated from the real module or whose factory is typed against it, and a hand-written fake whose conformance to the interface is checked at compile time. A double declared with no spec, or forced to the real type through a cast via an unchecked type, is not built from the type.

## Rationale
A double not built from the real type accepts any member the test stubs on it and, in many libraries, any member the code asks of it, with any argument list. After a rename or a signature change, a test that still uses the old interface through such a double keeps passing while the code is broken; a misspelled method called by the code under test, a wrong argument list and a misspelled verification method on the double all succeed until something else fails, apart from the few misspellings a library guards by name. A cast to the real type via an unchecked type, or a module-mock factory with no type, switches off the compiler's comparison of the double with the type, so the double drifts silently as the type changes; a typed factory or a compile-time conformance check makes the compile fail on the double when the interface changes. A hand-written module mock has to be updated by hand every time the module changes, so the automatic mock of the module, used or extended, is the default wherever it serves the test. A member-list spec rejects unknown members only; a signature-checking spec also rejects calls that do not fit the real signature and carries the check to the members and instances the double returns. Building the double from the type restores the property a free-form double lacks: its shape tracks the real type, so drift becomes a loud test failure instead of a silent pass.

## Example
```typescript
bad:  jest.mock('./payments', () => ({ charge: jest.fn() }));
      const store = { load: jest.fn(), save: jest.fn() } as unknown as OrderStore;
good: jest.mock<typeof import('./payments')>('./payments', () => ({ charge: jest.fn() }));
      const store: jest.Mocked<OrderStore> = { load: jest.fn(), save: jest.fn() };
```

## Limits
A plain double is acceptable when there is no real type to copy: a throwaway callable, a double invented for this one test with no production counterpart, or a mock of a module that does not exist in the build. A hand-written fake class in a language with no compile-time conformance check is outside the rule: no library builds it from the type, and whether it stays faithful to the type, in members and in behaviour, is a question the rule does not reach. The spec sees what introspection sees, so members created in the constructor or computed at run time are missing from it; set them on the double after creation or give the type a declared default instead of dropping the spec, and a member whose access runs code can make a type unsafe to introspect. A verifying double checks against the real type when that type is loaded in the run; a run that isolates the test from the type checks nothing. Speccing checks shape, not behaviour: a double that returns values the real type never returns still passes, and tests that exercise the units wired together remain needed. Where the compiler already checks every double against the interface it is declared as — a mock created from the class, a fake passed where the interface is expected — the rule is met with no extra code, and the finding there is the cast or the untyped factory that removes the check. A compile-time form fails only where the test files are type-checked: a runner that strips types without checking them runs a typed double and a cast alike, so the check needs a type-check step over the tests. A tolerance in the project context that permits unspecced doubles in a named test tree rejects the finding.

## Validator
Grep the added lines of test files for a mock constructor or a patch call with no spec or signature-checking option, a plain double constructor, a module mock with an inline factory and no type argument, and a literal forced to a type through a cast via an unchecked type. For each hit, read the hunk for the real type the double stands in for: the patched target, the type named in the cast, the module path, the parameter or field the double is passed into. Treat the double as built from the type when it carries a spec or signature-checking option, is a verifying double, is generated from the interface or trait, is the automatic mock of the real module, has a factory typed against the real module, or is a fake with a compile-time conformance check. Leave the line alone when no production type exists for the double. A patch call that passes its replacement object explicitly is not a hit: judge the replacement where it is created. Validator question: **Does an added line create a test double for an existing production type without building it from that type, so that the double would accept a member or a call signature the real type lacks?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: TST-11`, severity major, `file`, `symbol`, `code` = the added line that creates or casts the double, verbatim, `fix` = the same double built from the real type — the spec or signature-checking option, the verifying form, the factory typed against the real module, or a typed declaration in place of the cast — in the file's language, `rationale` = names the real type the double stands in for and that nothing checks the double's shape against that type, so a rename or a signature change of the type leaves the double stale with no failure where it is built, and where the code is not compiled against the type the test passes on broken code).

## Source
- Python documentation, `unittest.mock`, section "Autospeccing" (cpython `Doc/library/unittest.mock.rst`) (fetched): "any tests for code that is still using the *old api* but uses mocks instead of the real objects will still pass. This means your tests can all pass even though your code is broken." The same section documents the constructor-attribute limit and that integration tests remain needed.
- SonarSource RSPEC python:S9137 "Mocks should be created with autospec" (fetched): "By default, unittest.mock.Mock accepts any attribute name and any call signature. That hides mistakes: typos on methods under test, wrong argument lists, and misspelled assertion helpers all succeed until something else fails later." Exception: "A bare Mock can be acceptable when there is no useful real collaborator to copy".
- RSpec Mocks, "Verifying doubles" (`features/verifying_doubles/README.md`) (fetched): "RSpec will check that the methods being stubbed are actually present on the underlying object if it is available. Prefer using verifying doubles over normal doubles."
- eslint-plugin-jest `jest/no-untyped-mock-factory` (fetched): "Requiring a type makes it easier to use TypeScript to catch changes needed in test mocks when the source module changes."
- Jest documentation, "Manual Mocks", section "Examples" (fetched): "you have to manually update them any time the module they are mocking changes. Because of this, it's best to use or extend the automatic mock".
- flake8-mock-spec TMS010–TMS022 (fetched): "enforce the use of the spec argument when creating mocks"; oslotest documentation, "Mock autospec" (fetched): a spec "only checks if an attribute exists ... It does not guarantee that the given attribute is actually a method, or if its signature is respected."
- Effective Go, section "Interface checks" (fetched): "Should the json.Marshaler interface change, this package will no longer compile"; mockall README, "Overview" (fetched): "A mock object is an object with the same interface as a real object".
- typescript-eslint `no-unsafe-type-assertion` (fetched): "This rule forbids using type assertions to narrow a type, as this bypasses TypeScript's type-checking."
- Jest documentation, "Getting Started", section "Using TypeScript" (fetched): "Because TypeScript support in Babel is purely transpilation, Jest will not type-check your tests as they are run."
- Caveat: the evidence is library documentation and tool rules stating the mechanism; none measures how often unchecked doubles hide defects.
