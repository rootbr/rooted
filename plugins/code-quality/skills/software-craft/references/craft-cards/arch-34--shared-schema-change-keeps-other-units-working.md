---
title: A change that alters or removes a table, column or other schema element that another separately deployed unit reads or writes keeps that unit working until it is deployed with a matching update, since units sharing a schema cannot be deployed atomically
rule_id: ARCH-34
domain: architecture
step: [design, implement, review]
applies_to: [service-boundary]
triggers: ['(?i)\balter\s+table\b', '(?i)\bdrop\s+(?:table|column|view)\b|\brename\s+(?:column|to)\b', '\b(?:drop_column|remove_columns?|rename_column|change_column|alter_column|drop_table|rename_table|RemoveField|RenameField|AlterField|DeleteModel|RenameModel)\b', '(?i)\b(?:dropColumn|renameColumn|removeColumn|changeColumn|dropTable|renameTable|modifyColumn|alterColumn)\b']
scope: callers
check_kind: semantic
severity_default: major
---

# A change that alters or removes a table, column or other schema element that another separately deployed unit reads or writes keeps that unit working until it is deployed with a matching update, since units sharing a schema cannot be deployed atomically

## Thesis
Where separately deployed units read or write the same tables, a change that alters, renames or drops a table, column, view or other schema element another of those units reads or writes keeps that unit's reads and writes working until that unit is deployed with its matching update: the old element stays in place, beside its replacement where there is one, and its removal ships in a later release, once no other unit uses it. The rule holds also when the other unit's code changes in the same commit, because the units still reach production through separate deployments, and a change that spans them cannot be deployed atomically.

## Rationale
Units that share tables are coupled through the schema: a schema change has to be coordinated across every unit that relies on the database, which takes away each unit's lifecycle autonomy. A change that spans several separately deployed units cannot be implemented and deployed atomically; it is introduced unit by unit, each through its own deployment. Between the migration and the other unit's next deployment, that unit's unchanged code therefore runs against the changed schema. In a two-unit reproduction on SQLite, the consumer's read returned 1250 before the provider renamed a column and failed with "no such column" right after it, while the same read made through the provider's published accessor returned 1250 both times. Inside one application the same window lies between a migration and the processes still running: those processes can fail looking up a dropped column, and a plain rename requires downtime because the application may go on using the old name during or after the migration. The procedure that avoids the failure keeps the old and new columns in sync through a rename, and drops a column one release after the code stops using it. During a rolling update, machines running different versions of the code have to communicate, and one study of distributed systems found that these cross-version interactions caused the majority of update failures.

## Example
```typescript
bad:  // billing, deployed separately, still reads orders.total_cents
      await db.schema.alterTable("orders", (t) => t.renameColumn("total_cents", "amount_minor"));
good: await db.schema.alterTable("orders", (t) => t.integer("amount_minor"));
      await db("orders").insert({ id, total_cents: total, amount_minor: total });
      // backfill once every orders instance writes both columns
      await db.raw("UPDATE orders SET amount_minor = total_cents WHERE amount_minor IS NULL");
      // total_cents is dropped in a later release, once billing reads amount_minor
```

## Limits
A schema element that no other separately deployed unit reads or writes falls outside the rule: a private data store limits the scope of change to its owner, and keeping the owner's own running processes working through its migration is a matter of that unit's release procedure. A consumer that reads through a published contract — a view, an accessor, an API — rather than the table keeps working across a change behind that contract, as the reproduction's contract-based read did; the rule then governs changes to the contract itself, and the versioning and deprecation of a published API are rules of their own. The rule takes no side on whether separately deployed units should share tables at all — a cloud vendor's microservice architecture guidance says two services shouldn't share a data store — and governs the change where they do. A release that stops every unit using the element before the migration runs, and restarts each unit only with its update, leaves no unit running against the changed schema and falls outside the rule; such a release accepts downtime for the change. Retries, timeouts, transactions spanning units and messaging guarantees are outside its scope.

## Validator
Grep the hunk for a migration or DDL statement that alters, renames or drops a table, column, view or constraint — ALTER TABLE, DROP, RENAME, or a migration-tool call that drops or renames a column or table. For each changed element, search the callers' scope — the repository and every other deployable unit the project builds or declares — for its table and column names in queries, ORM mappings, views and reports. Establish whether any user of the element is built, released or deployed separately from the unit that carries the change; when every user ships in the same artifact, or the project's release stops every user before the migration runs, stop. Trace whether the change keeps that unit's reads and writes working: the old element is kept beside the new one and still written, a view or alias serves the old name, or the drop waits for a later release. Validator question: **Does the change alter, rename or drop a schema element that a separately deployed unit reads or writes, leaving that unit's reads or writes broken until the unit ships its own update?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-34`, severity major, `file`, `symbol`, `code` = the migration line that alters, renames or drops the element, quoted verbatim from the diff, `fix` = for a rename or a type change, the expand step in the file's language that adds the new element beside the old one and writes both, then backfills the new element once every instance of the changing unit writes both, with the drop moved to a later release; for a drop, the same migration without the drop, which moves to a later release once no other unit uses the element, `rationale` = the separately deployed unit that reads or writes the element and the read or write that breaks once the migration runs).

## Source
- Azure Architecture Center, "Data considerations for microservices", docs/microservices/design/data-considerations.md (fetched): "This rule prevents unintentional coupling between services, which happens when services share the same underlying data schemas. If the data schema changes, the change must be coordinated across every service that relies on that database."; "Two services shouldn't share a data store."; "Isolating each service's data store limits the scope of change and preserves the agility of independent deployments."
- .NET Microservices architecture guide, "Data sovereignty per microservice", data-sovereignty-per-microservice.md (fetched): "If multiple services were accessing the same data, schema updates would require coordinated updates to all the services. This would break the microservice lifecycle autonomy."
- "Towards Modern Development of Cloud Applications", HotOS 2023, doi:10.1145/3593856.3595909, §1 challenge C5 (fetched): "When making changes that affect multiple microservices, developers cannot implement and deploy the changes atomically. They have to carefully plan how to introduce the change across n microservices with their own release schedules."; §4.4 Atomic Rollouts, reporting a SOSP 2021 study of upgrade failures as its reference [78] (fetched; the study itself unfetched): "During a rolling update, machines running different versions of the code have to communicate with each other, which can lead to failures. [78] shows that the majority of update failures are caused by these cross-version interactions."
- Development documentation, "Avoiding downtime in migrations", gitlabhq/gitlabhq doc/development/database/avoiding_downtime_in_migrations.md (fetched): "the running instances can fail trying to look up the removed column"; "first, ignore the column (release M), then, drop it in the next release (release M+1)."; "Renaming columns the standard way requires downtime, as an application might continue to use the old column names during or after a database migration."; the rename helper "takes care of renaming the column, ensuring data stays in sync".
- Two-unit reproduction, SQLite 3.53.4 via the Python standard library (fetched, hands-on): "shared-schema: before=1250 after=ERROR no such column: total_cents"; "via-contract: before=1250 after=1250".
- Caveat: the update-failure share concerns rolling updates of distributed systems in general, and the migration procedure concerns the running processes of one application; neither measures shared schemas specifically.
