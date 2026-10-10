---
title: Bindings are grouped into one wiring module or registration function per feature, which the composition root installs or calls whole, not into modules that each gather one kind of class across features
rule_id: ARCH-26
domain: architecture
step: [design, refactor, review]
applies_to: [universal]
triggers: ['\bclass\s+\w*(?:Repositories|Services|Controllers|Handlers|Filters|Clients|Daos|Adapters)(?:Module|Config|Configuration|Registration|Installer)\b', '\b(?:(?:Add|add|register|Register|provide|Provide)(?:Repositories|Services|Handlers|Clients|Controllers|Filters|Adapters)|(?:add|register|provide)_(?:repositories|services|handlers|clients|controllers|filters|adapters))\s*\(', '\bextends\s+(?:Abstract|Private)Module\b|@Module\b']
scope: callers
check_kind: semantic
severity_default: suggestion
---

# Bindings are grouped into one wiring module or registration function per feature, which the composition root installs or calls whole, not into modules that each gather one kind of class across features

## Thesis
Bindings are grouped by feature: one wiring module or registration function registers all of the services one working feature requires, such as authenticating requests or making requests to one backend, so that installing that single module in the injector, or leaving it out, ideally enables or disables the entire feature. A module that gathers the bindings of every class implementing one type across features, such as all filters in one module and all graphs in another, is reorganized by feature. The entry routine that creates the injector installs or calls each feature's module whole.

## Rationale
Grouping by feature gives each feature one switch: one module installed in the injector, or one registration call, brings in every service the feature requires, and leaving it out removes the entire feature. A module grouped by class type binds every implementation of one interface whichever feature it serves, so installing or omitting it switches a slice of several features rather than one whole feature. One major framework's guidance states that most applications create the injector exactly once, in their entry routine, from one or more modules; with modules grouped by feature, that list is where a feature is installed or left out. Another major framework documents, as its convention for registration functions, a single function per group of related services that registers all of the services a framework feature requires, under a meaningful and descriptive name.

## Example
```typescript
bad:  @Module({ providers: [UserRepo, OrderRepo] }) class RepositoriesModule {}
      function registerRepositories(c: Container) { c.bind(UserRepo); c.bind(OrderRepo); }
      function registerHandlers(c: Container) { c.bind(UserHandler); c.bind(OrderHandler); }
      registerRepositories(container); registerHandlers(container);
good: @Module({ providers: [UserRepo, UserHandler] }) class UsersModule {}
      function registerUsers(c: Container) { c.bind(UserRepo); c.bind(UserHandler); }
      function registerOrders(c: Container) { c.bind(OrderRepo); c.bind(OrderHandler); }
      registerUsers(container); registerOrders(container);
```

## Limits
The grouping is stated as an ideal and a convention (ideally, try to, by convention), so a module grouped by class type is a suggestion rather than a defect. A feature need not be user-facing: a module that lets the process make requests to one backend is grouped by feature. A module whose name carries a class type but whose bindings all serve one feature mixes no features and is not flagged; the rule reaches a module that binds classes of one type for two or more features, not the name. Several classes of one type that serve the routes or operations of one feature, such as its command handlers, belong in that feature's module and are not flagged. The rule reaches bindings written into explicit modules or registration functions; components a framework discovers and registers by scanning have no module to regroup.

## Validator
Grep the hunk for a wiring module or registration function: a class that extends a module base or carries a module annotation, or a function that registers, adds or provides bindings, especially one named for a class type in the plural (repositories, services, controllers, handlers, filters, clients). Open the file and list every binding that module or function makes; for each, name the working feature it serves: the capability it takes part in, such as authenticating requests or managing orders, or the external backend it lets the process call, never its technical layer and never a single route or operation inside one feature, so a repository for users and one for orders serve two features even when they share a layer package and one database, while a handler for logging in and one for logging out both serve authentication. Trace the entry routine that installs or calls the module, and check whether other modules bind the remaining pieces of the same features. Validator question: **does one wiring module or registration function in the hunk bind classes of one type for two or more distinct features, so that no single module install or call enables or disables one of those features whole?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-26`, severity suggestion, `file`, `symbol`, `code` = the module's or registration function's declaration line and the bindings that belong to different features, `fix` = one module or registration function per feature that binds every class the feature requires, and the entry routine installing or calling each one, in the file's language, `rationale` = the features whose bindings the module mixes and the install line that cannot switch one of them alone).
