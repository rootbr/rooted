---
title: An application's own wiring module binds each key one way every time it is installed, and the composition root or the test chooses whole modules per environment
rule_id: ARCH-25
domain: architecture
step: [design, implement, test, review]
applies_to: [universal]
triggers: ['^\s*[}]?\s*(?:(?:else\s+)?if|elif|when|switch|match)\b.*(?:(?i:env|profile|stage|\bis_?(?:test|dev(?:elopment)?|prod(?:uction)?|staging)\b|test_?mode)|\bDEBUG\b)|@(?:Profile|ConditionalOn(?:Property|Expression))\b|\bIs(?:Development|Production|Staging|Environment)\s*\(', '\b(?:[Bb]ind\w*|(?:Try)?Add(?:Singleton|Scoped|Transient))\s*[<(]']
scope: file
check_kind: semantic
severity_default: minor
---

# An application's own wiring module binds each key one way every time it is installed, and the composition root or the test chooses whole modules per environment

## Thesis
Each wiring module the application owns binds each of its keys to one implementation, and binds every one of its keys, every time it is installed. The choice between environments is made by which modules are installed: production, development and test wiring are distinct modules or component configurations, kept few in number; the composition root installs the set for the environment it starts and a test installs its own, where a test configuration may extend the production one and install a different set of modules. The finding is a branch that binds one key to different implementations, or binds a key in some cases only, depending on an environment name, a flag, a property or an optional value passed to the module. Such a branch is a finding inside a module the application owns, and in the composition root when one of its arms binds a key directly rather than installing whole modules.

## Rationale
A module with such a branch holds several configurations, and a configuration the tests do not run leaves its implementation unverified: in the documented case one arm binds an in-memory implementation for development and the other a remote implementation for production, and without a test of the production arm it is impossible to be sure the remote implementation works in the integrated application. The branch is not the cost by itself; the cost arises when a configuration is untested. Keeping configurations few and splitting production and development into distinct modules makes it easier to be sure that the entire production codepath is tested, and the split also prevents production classes from having a compile-time dependency on test code. A key bound in some configurations and not in others is a related issue of the same module. A test configuration that extends the production one gets all of the same entry points and interfaces and installs a different set of modules.

## Example
```python
bad:  def store_module(binder, env):
          if env == "prod":
              binder.bind(Store, to=RemoteStore)
          else:
              binder.bind(Store, to=MemoryStore)
good: def remote_store_module(binder): binder.bind(Store, to=RemoteStore)
      def memory_store_module(binder): binder.bind(Store, to=MemoryStore)
      app = Injector([remote_store_module, *app_modules])
      test_app = Injector([memory_store_module, *app_modules])
```

## Limits
Whose wiring it is separates the cases. A shared library's default configuration, shipped for applications to pick up and override, is outside the rule: documentation addressed to library authors says such a configuration almost always carries conditions, among them one that adds a default binding only when the application has not bound the key itself, so that developers can override the defaults when they are not happy with them. The same documentation offers a number of these conditions for reuse in the reader's own code on whole configuration classes or on individual binding methods, and recommends the conditions on whether a key is already bound for a library's default configuration only, because they are evaluated against the bindings registered so far and that configuration loads after the application's own; the offer makes the form available and does not address the untested configuration, so a condition in the application's own wiring that selects a key's implementation or binds a key only sometimes stays in scope. Documentation of environment profiles addressed to application developers offers a profile on an individual binding method for alternative implementations of one key, and lets an integration test declare the profiles it activates; that form selects a key's implementation inside one module and stays in scope, because a binding whose profile no test activates stays unverified. A project whose tests boot every configuration a branch creates removes the untested-configuration cost; a compile-time dependency on test code remains where one arm binds a test implementation, and a key bound only sometimes remains where one arm leaves it unbound; a project that keeps such a branch records it as a project tolerance.

## Validator
Grep the hunk for binding and registration calls, for branches on an environment name, profile, stage or test-mode flag, for environment checks, and for conditions on a property or an expression attached to wiring. Open the file and find the wiring module, component or configuration class that holds each hit. Decide whose wiring it is: the composition root itself, a module that the application's composition root or its tests install, or a library's default configuration shipped for applications to override; stop at the third. In the composition root, a branch whose every arm installs whole modules or component configurations passes, and a branch with an arm that binds a key directly is traced like a branch inside a module. In the application's module, trace every branch inside its body, every test of an optional value passed to it, and every condition attached to a single binding inside it, and compare the cases: one case binding a key to an implementation another case does not, or binding a key another case leaves unbound, is the finding. A condition or profile on a whole module, component or configuration class decides which modules are installed and is outside this rule. Validator question: **Does a wiring module the application owns branch on the environment, a flag, a property or an optional value so that one key is bound to different implementations or is bound in some cases only?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-25`, severity minor, `file`, `symbol`, `code` = the branch or condition and the bindings it governs, quoted verbatim, `fix` = one module per case, each binding its keys unconditionally, with the composition root and the test each installing the module it needs, in the file's language, `rationale` = the configuration the tests do not run, the compile-time dependency of production wiring on test code, or the key bound only sometimes, whichever applies).
