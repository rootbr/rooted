---
title: orphanRemoval and cascade REMOVE are declared only on an association whose target is privately owned by the parent
rule_id: REL-46
domain: reliability
triggers: ['orphanRemoval\s*=\s*true', 'CascadeType[.]ALL', 'CascadeType[.]REMOVE', '@ManyToMany', 'cascade\s*=']
scope: callers
check_kind: semantic
severity_default: critical
---

# orphanRemoval and cascade REMOVE are declared only on an association whose target is privately owned by the parent

## Thesis
`orphanRemoval = true`, `CascadeType.REMOVE` and `CascadeType.ALL` appear on a `@OneToMany` or `@OneToOne` whose target entities belong to that parent alone; they never appear on a `@ManyToMany`, on an association whose children can be moved to another parent, or on one whose target is referenced from elsewhere, and an orphaned entity is never reassigned to another relationship.

## Rationale
With `orphanRemoval`, an entity "removed from the relationship (either by removal from the collection or by setting the relationship to null)" has the remove operation applied to it at flush; the functionality "is intended for entities that are privately 'owned' by their parent entity", and portable applications "must not reassign an entity that has been orphaned to another relationship or otherwise attempt to persist it". Moving a child from one parent's collection to another's therefore deletes the child row while the code believes it re-parented it, and `CascadeType.REMOVE` on a many-to-many deletes rows still referenced by other parents — the removal "will propagate beyond the link table" and ends in a constraint violation or a lost row.

## Example
```java
bad:  @ManyToMany(cascade = CascadeType.ALL) Set<Tag> tags;
      @OneToMany(mappedBy = "post", orphanRemoval = true) List<Comment> comments;   // comments are moved between posts
good: @ManyToMany(cascade = {CascadeType.PERSIST, CascadeType.MERGE}) Set<Tag> tags;
      @OneToMany(mappedBy = "post", cascade = {CascadeType.PERSIST, CascadeType.MERGE}) List<Comment> comments;
```

## Limits
A child that exists only as part of its parent — line items of an order, addresses embedded in a customer — is privately owned and the declarations are correct. A `@ManyToMany` cascading only `PERSIST` and `MERGE` is correct. A project context stating that children are never re-parented or shared rejects the finding for that association.

## Validator
On the triggered hunk find each `orphanRemoval = true`, `CascadeType.REMOVE` or `CascadeType.ALL` and open the file for the association's cardinality, then the usages of the target type across the repository: whether other entities reference it, and whether any code moves the target between parents or removes it from one collection to add it to another. Validator question: **can a removal cascade or orphan removal delete a row that another parent or relationship still needs?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: REL-46`, severity critical, `file`, `symbol`, `code` = the mapping annotation quoted verbatim from the diff, `fix` = `PERSIST`/`MERGE` cascades without `orphanRemoval` or `REMOVE`, `rationale` naming the shared or re-parented row that is deleted).

## Source
Jakarta Persistence specification, chapter "Metadata for Object/Relational Mapping", `OneToMany` — "If orphanRemoval is true and an entity that is the target of the relationship is removed from the relationship (either by removal from the collection or by setting the relationship to null), the remove operation will be applied to the entity being orphaned"; "The orphanRemoval functionality is intended for entities that are privately 'owned' by their parent entity. Portable applications must otherwise not depend upon a specific order of removal, and must not reassign an entity that has been orphaned to another relationship or otherwise attempt to persist it". Hibernate ORM user guide, chapter "Associations" — "For @ManyToMany associations, the REMOVE entity state transition doesn't make sense to be cascaded because it will propagate beyond the link table".
