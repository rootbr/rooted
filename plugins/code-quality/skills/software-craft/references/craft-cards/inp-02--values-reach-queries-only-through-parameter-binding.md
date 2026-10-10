---
title: A value reaches a database query only through the driver's parameter binding, never by concatenating, formatting or interpolating it into the query text
rule_id: INP-02
domain: input
step: [implement]
applies_to: [universal]
triggers: ['(?i)["''`]\s*(SELECT|INSERT|UPDATE|DELETE|MERGE|WITH|MATCH)\b[^"''`]*\b(FROM|INTO|SET|WHERE|VALUES|ORDER\s+BY)\b[^"''`]*["''`]\s*(\+|%\s*[(\w])|"\s*(SELECT|INSERT|UPDATE|DELETE|MERGE|WITH|MATCH)\b[^"]*\b(FROM|INTO|SET|WHERE|VALUES)\b[^"]*"\s*\+|\bf(?P<fq>["''])\s*(SELECT|INSERT|UPDATE|DELETE|MERGE|WITH|MATCH)\b(?:(?!(?P=fq)).)*\{|`\s*(SELECT|INSERT|UPDATE|DELETE|MERGE|WITH|MATCH)\b[^`]*\$\{', '(?i)(Sprintf|format!?)\(\s*["''`](SELECT|INSERT|UPDATE|DELETE|MERGE|WITH|MATCH)\b|(?P<dq>["''])\s*(SELECT|INSERT|UPDATE|DELETE|MERGE|WITH|MATCH)\b(?:(?!(?P=dq)).)*(?P=dq)\s*[.]format(ted)?\(|\b(execute|executemany|executescript|executeQuery|executeUpdate|addBatch|exec|query|queryRow|raw|rawQuery|createQuery|createNativeQuery|prepareStatement|prepare)\(\s*["''`][^"''`]*["''`]\s*\+|\b(ORDER|GROUP)\s+BY\s*["''`]?\s*(\+|\$\{|\{|%s)']
scope: hunk
check_kind: semantic
severity_default: major
---

# A value reaches a database query only through the driver's parameter binding, never by concatenating, formatting or interpolating it into the query text

## Thesis
Every value in a database query (SQL, HQL, NoSQL or Cypher) enters through the driver's or ORM's parameter binding, as a separate argument for a placeholder in query text that is a constant or is composed only from fragments the code controls; a part that cannot be bound, such as a table name, a column name or a sort direction, comes from a fixed allow-list or mapping in code or from the driver's own identifier composition.

## Rationale
Parameter binding fixes all of the query's code first and passes each value in afterwards, so the database always distinguishes code from data, whatever input is supplied. When the program assembles the statement by concatenation or formatting, the whole statement, value included, is sent to the database as one text, and a value that closes the quote and appends `OR TRUE` selects every row. Preparing a statement from such a built string does not help: tainted data used in building that string can still make the prepared statement do something unexpected and undesirable. Escaping every value before splicing it in is database-specific and fragile compared to the other defenses, with no guarantee that it prevents every injection in every situation. Input validation is a secondary defense, recommended alongside bound variables rather than in their place. Static analysers flag the construction itself, query text built by concatenation or format operators, and some flag it without taint analysis, regardless of the data source. In a user study, 36% of participants with access to an AI assistant wrote solutions vulnerable to SQL injection, against 7% of the control group.

## Example
```java
bad:  String sql = String.format("SELECT * FROM orders WHERE owner = '%s'", owner);
      ResultSet rows = statement.executeQuery(sql);
good: PreparedStatement query = connection.prepareStatement(
          "SELECT * FROM orders WHERE owner = ?");
      query.setString(1, owner);
      ResultSet rows = query.executeQuery();
```

## Limits
A table name, column name or sort direction cannot use a bind variable, and identifiers cannot be passed like query arguments; ideally it comes from the code, and otherwise it is validated against an allow-list, used only to select a fixed value to append, or built with the driver's identifier composition. A value converted to a number, boolean, date or enumerated type before it is appended, or used only to select a code-controlled fragment to append, is safe from injection, but that form is still classed as discouraged dynamic query generation; the validator therefore still flags a converted value spliced into the text and treats only the fragment such a value selects as code-controlled. The rule reaches query text built inside a stored procedure as well: parameterized queries apply there too, while such dynamic SQL should be avoided and, where it cannot be, falls back to input validation or escaping, the discouraged last resort. Contested, and the statement type and the query part separate the cases: a value in a statement the server can bind goes through server-side binding where the driver offers it; a statement the server cannot bind, and an identifier, go through the driver's composition objects or an allow-list in code; escaping and splicing stays the discouraged last resort. Parameterization is required to be done server-side, because the client-side parameterization many libraries offer often just builds the query by string concatenation before sending it; server-side binding works for SELECT, INSERT, UPDATE and DELETE but not for many other statements (SET, NOTIFY, any data-definition statement), where a function form that takes parameters replaces the statement if the database offers one, and otherwise the driver's composition objects merge query and value on the client; framing safety as sanitizing and controlling the input while building the query string is the strongly discouraged option.

## Validator
Grep the hunk for query text (a string literal, text block or template that starts with a query keyword or carries a query clause) joined with a non-literal operand by concatenation, a format call, a format operator or string interpolation, and for query-execution, prepare, raw-query and native-query calls whose text argument is such a built string. Open the hunk around each hit and trace every spliced operand: a literal, a named constant, a fragment the code selects from a fixed set (a mapping, a switch, a conditional on a boolean or enumeration), or a table name, column name or sort direction that the code checks for exact membership in a fixed allow-list in code before the splice is code-controlled; a parameter, a field, a request value, a value read from storage and a value passed through an escaping, validation or type-conversion routine are values. Query text composed with the driver's composition objects is not a hit. Validator question: **Does a value that is not code-controlled reach the query text by concatenation, formatting or interpolation instead of through a bound parameter?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: INP-02`, severity major, `file`, `symbol`, `code` = the line that splices the value into the query text and the call that runs it, `fix` = the same query with a placeholder in constant text and the value passed through the driver's binding call, or the identifier chosen from an allow-list in code, in the file's language, `rationale` = names the spliced value, where it comes from and why it goes through binding rather than escaping, validation or type conversion).
