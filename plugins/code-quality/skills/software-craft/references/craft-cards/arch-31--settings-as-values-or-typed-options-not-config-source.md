---
title: Code outside the composition root that reads a set of its own configuration settings receives them as a typed options object or as values, and is not handed the configuration source or a holder object to look them up in by key
rule_id: ARCH-31
domain: architecture
step: [design, implement, review]
applies_to: [universal]
triggers: ['\bIConfiguration(?:Root|Section)?\s+\w+\s*[,);=]|\b(?:Environment|PropertyResolver|ConfigurableEnvironment)\s+\w+\s*[,);=]|\b\w+\s*:\s*(?:I?Configuration(?:Root|Section)?|Config(?:uration)?Service)\b', '\b_?(?:[Cc]onfig(?:uration|Service)?|cfg|[Ss]ettings|conf|env|environment)\s*(?:\[\s*["'']|[.]\s*(?:get|Get|GetValue|getString|getInt|getBoolean|getProperty)\s*(?:<[^>]*>)?\s*\(\s*["''])|\bGetSection\s*\(\s*["'']']
scope: file
check_kind: semantic
severity_default: minor
---

# Code outside the composition root that reads a set of its own configuration settings receives them as a typed options object or as values, and is not handed the configuration source or a holder object to look them up in by key

## Thesis
A component outside the composition root that reads a set of configuration keys of its own receives them as a strongly typed options object that groups the related settings of one scenario, an individual setting may arrive as a value, and the entry code that composes the object graph binds them from the configuration source. Such a component receives the settings themselves, rather than the configuration source or a data-holder object that exists only to allow access to another object, from which it would look each setting up by key.

## Rationale
The options pattern is the preferred way to read related configuration values: classes provide strongly typed access to groups of related settings. When the settings are isolated by scenario into separate classes, two properties hold: a class that depends on configuration settings depends only on the settings it uses (interface segregation), and settings for different parts of the application are not dependent on or coupled with one another (separation of concerns). The service container is kept free of directly stored data and configuration: configuration goes through the options pattern, and a data-holder object that only exists to allow access to another object gives way to requesting the actual item. The binding sits in the program's entry code, which binds a named configuration section to its options class or registers the options class against that section, and the options object is then provided through dependency injection. A typed object grouping a component's set of keys is structured and type-safe, is injected into the component, and deals only with the environment, injecting no other services from the context.

## Example
```typescript
bad:  class Mailer {
        constructor(private config: Configuration) {}
        send(): void { connect(this.config.get("mailer.host"), Number(this.config.get("mailer.port"))); }
      }
good: interface MailerOptions { host: string; port: number }
      class Mailer {
        constructor(private options: MailerOptions) {}
        send(): void { connect(this.options.host, this.options.port); }
      }
      const mailer = new Mailer({ host: env.MAILER_HOST, port: Number(env.MAILER_PORT) });
```

## Limits
A framework's typed wrapper over one options class, such as a per-request snapshot or a monitor that retrieves current option values at any time, is the typed options object in the form a setting read after the application starts needs: the wrapper decouples the option's lifetime from the container and defers evaluation of the options instance to the moment it is accessed. A library's registration routine may take the configuration source scoped to a named section, which the consumer passes when registering the library's services, and bind its options class to it; that routine is part of composing the graph. In corner cases a typed options class that needs the environment may obtain it through setter injection or the framework's environment-aware callback. A component that reads a single setting by key from the configuration source it was handed falls outside the defect: the framework documentation shows a service resolving the configuration source to read one key, and recommends the options pattern for related settings once the application and its configuration grow complex.

## Validator
Grep the hunk for a parameter, field or constructor argument whose type is the configuration source itself (a configuration root or section, an environment or property resolver, a configuration service) and for a lookup by string key on a configuration object, such as a get call with a quoted key, an indexer with a quoted key or a section lookup by name. Open the file and name the enclosing unit: the process entry, a registration routine that binds a named section to an options class, or a typed options class binding the environment is the composition edge and yields no finding. Otherwise trace what the component does with the object it received: a typed options object over one scenario, or a framework wrapper over one options class, is compliant; the configuration source, whole or scoped to a section, or a holder object whose only job is to hand out another object, from which the component looks two or more related settings of its own scenario up by key, is the defect; a single keyed read is outside the rule. Validator question: **Does a component outside the composition edge receive the configuration source, or a holder object that only gives access to it, and look two or more related settings of its own scenario up in it by key?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-31`, severity minor, `file`, `symbol`, `code` = the parameter or field typed as the configuration source or holder and the keyed lookups that read its settings from it, quoted verbatim from the diff, `fix` = a typed options type holding exactly the settings the component reads, bound from the source at the composition root and passed into the component's constructor, in the file's language, `rationale` = the component depends on settings it does not use and couples its settings to those of other parts of the application, where an options object isolated by scenario carries only its own).
