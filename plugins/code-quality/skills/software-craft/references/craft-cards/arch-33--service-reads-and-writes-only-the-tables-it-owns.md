---
title: A separately deployed service reads and writes only the tables it owns and reaches another service's data through that service's API or messages, outside a migration that still reuses a monolith's schema unchanged
rule_id: ARCH-33
domain: architecture
step: [design, implement, review]
applies_to: [service-boundary]
triggers: ['(?i)["''`]\s*(?:select\b|insert\s+into\b|update\s+\w+\s+set\b|delete\s+from\b)', '(?i)\b(?:spring[.]datasource[.]url|DATABASE_URL|DB_URL|jdbc:\w+:|(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?)://)', '@Table\s*\(|__tablename__\s*=|\bdb_table\s*=|\bTableName\s*\(\s*\)|\btable_name\s*[:=]', '(?i)\b(?:search_path|currentSchema|default_schema)\s*[=:]\s*["'']?\w+']
scope: callers
check_kind: semantic
severity_default: minor
---

# A separately deployed service reads and writes only the tables it owns and reaches another service's data through that service's API or messages, outside a migration that still reuses a monolith's schema unchanged

## Thesis
Code of a separately deployed service reads and writes only the database tables that service owns, and it reaches data another service owns only through that service's API endpoints or its messages. The finding is a table that two or more deployed services read or write; services that share one physical database server and keep their own tables are outside it. The rule holds for services developed and deployed independently, and the reported exception is a set of services split off a monolith that still reuse its schema unchanged.

## Rationale
When several services read and write the same tables, a change to those tables must be coordinated across every service that relies on them, which breaks each service's lifecycle autonomy. Keeping each service's data private limits the scope of a schema change to that service: its team changes the schema without influencing the work of other teams, and the service evolves and deploys independently. Practitioners largely deal with evolving requirements and the schema changes that follow, and schemas that evolve independently in different services are reported as a major driver of service architectures. Two services that access and manage the same database form the shared-persistence smell, which a detector reports whenever more than one service interacts with one data store. Its three refactorings all aim at each database being accessed by only one service: split the database where the services implement separate business logic on disjoint portions of it, add a data-manager service that alone interacts with the database, or merge the services where the sharing signals an application split into too fine-grained services processing the same data.

## Example
```python
bad:  # orders service connects to the customers service's database, maps its table and queries it
      engine = create_engine("postgresql://customers-db/app", connect_args={"options": "-c search_path=customers"})
      class Customer(Base):
          __tablename__ = "customers"
          id = Column(Integer, primary_key=True)
      email = Session(engine).execute(text("SELECT email FROM customers WHERE id = :id"), {"id": customer_id}).scalar_one()
good: # orders service asks the customers service through its API
      response = customers_api.get(f"/customers/{customer_id}")
      email = response.json()["email"]
```

## Limits
Sharing one physical database server is outside the rule; the problem arises when services read and write the same set of tables. Ownership is per table: private tables per service on a shared server and schema, a schema per service on a common server, and a server per service are the three mainstream layouts reported for services. The rule is contested, and whether the services still reuse a monolith's schema unchanged separates the cases. A mapping study reports six implementations in which all services access one shared database concurrently, without data isolation; the main advantage reported is the simplicity of the migration from monolithic applications, since the existing schema is reused without changes and the data access layer stays identical. While services sit in that state, every schema change is coordinated across all of them, and the same study lists lack of data isolation as that pattern's disadvantage. Migration also proceeds with a database per service: the same study reports a database per service as often used to migrate existing monoliths with existing databases, and lists independent development without influencing others on schema changes as its advantage. The rule carries a cost the other side names: a business process spanning services cannot run one ACID transaction across their databases and relies on eventual consistency, and the study lists data consistency as a disadvantage of a database per service and an advantage of a shared server. The rule reaches table access across deployed services; how the replacing API is versioned and how its calls or messages are retried belong to API-evolution and error-handling rules.

## Validator
Grep the hunk for SQL text in string literals, database connection URLs and settings, ORM table declarations and schema selections. Name the deployable unit the hunk belongs to from the nearest build file, container file or deployment manifest. For each table the hunk reads or writes, open the scope callers and the repository's migrations and model declarations, and find the deployable unit that creates and migrates that table and every other deployable unit whose code reads or writes it; for a connection URL or schema setting, find whose database or schema it names. A migrations job or project whose tables only one service's code reads or writes belongs to that service. Where another deployable unit owns the table, or where no single service owns it (a migrations project or a schema several services use) and another deployed service also reads or writes it, check whether those units were split off a monolith and still reuse its schema unchanged; that state is the reported migration exception and yields no finding. Validator question: **Does code of one separately deployed service read or write a table that another deployed service owns or also reads or writes, outside services that still reuse a monolith's schema unchanged?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ARCH-33`, severity minor, `file`, `symbol`, `code` = the query, table declaration or connection setting quoted verbatim from the diff, `fix` = the call to the owning service's API endpoint or the subscription to its messages that replaces the table access, in the file's language, or, where no single service owns the table, the split of the database, the data-manager service or the merge of the services that gives it one owner, `rationale` = names the table, the service that owns it or the other services that read or write it, and the coordinated schema change across those services that the shared table forces).
