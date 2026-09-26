---
title: An expression-language string is never built from or evaluated on untrusted input, and no evaluation context makes that safe
rule_id: SEC-05
domain: security
triggers: ['parseExpression\(', 'SpelExpressionParser|ExpressionParser', 'StandardEvaluationContext|SimpleEvaluationContext', '#\{', 'Ognl|OgnlUtil|OgnlContext', 'ExpressionFactory|ELProcessor|ValueExpression']
scope: file
check_kind: semantic
severity_default: critical
---

# An expression-language string is never built from or evaluated on untrusted input, and no evaluation context makes that safe

## Thesis
The text handed to a SpEL, Jakarta EL, OGNL or template-expression parser is a constant the code owns — a literal in `@Value("#{...}")`, `@PreAuthorize`, `@Cacheable(key = ...)`, or a string assembled from code-owned parts. A value that originates outside the code is supplied to an expression as a variable or root object, never spliced into the expression text; a request parameter passed to `parseExpression` is the defect, and a `SimpleEvaluationContext` around it does not remove it. `@Value("${...}")` resolves a property and is not expression evaluation.

## Rationale
SpEL can invoke constructors and methods, read and write fields, and reference beans through reflection, so evaluating an expression from an untrusted source grants that source arbitrary code execution in the application — `T(java.lang.Runtime).getRuntime().exec(...)` is a valid expression. `StandardEvaluationContext` exposes the whole language. `SimpleEvaluationContext` restricts the language on a best-effort basis and its documentation says it must not be considered safe for an expression from an untrusted source: anything reachable from the root object, accessors and functions is still callable, and a getter is not guaranteed side-effect free. The same holds for OGNL and Jakarta EL. A `#{...}` in `@Value` is evaluated at bean creation with the code's literal — safe as long as the literal is a constant; a `${...}` placeholder is property resolution.

## Example
```java
bad:  Expression e = parser.parseExpression(req.getParameter("rule"));
      Object v = e.getValue(SimpleEvaluationContext.forReadOnlyDataBinding().build(), order);
good: Expression e = parser.parseExpression("total > #threshold");     // code-owned text
      EvaluationContext ctx = SimpleEvaluationContext.forReadOnlyDataBinding().build();
      ctx.setVariable("threshold", Integer.parseInt(req.getParameter("threshold")));
      Object v = e.getValue(ctx, order);
```

## Limits
Applies when the expression text depends on a value from outside the code. Expression text chosen from a fixed set the code defines (an enum of named rules with literal expressions), or stored rules that only application administrators can edit, is a trust decision the project context can state; absent that statement, a rule text loaded from a table that end users write is flagged. Values carried into an expression through `setVariable` or as the root object are the correct form, provided the root object exposes no dangerous operations.

## Validator
On the triggered hunk find each `parseExpression`, `getValue`, OGNL or EL evaluation call, and each `#{` inside an annotation. Open the file and trace the expression string's operands: a literal, a code-owned constant, or a value from a request, message, file or user-edited store. Validator question: **does text from outside the code become part of the expression that is parsed, rather than a variable the expression reads?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: SEC-05`, severity critical, `file`, `symbol`, `code` = the parse or evaluation call and the expression source quoted verbatim from the diff, `fix` = the constant expression with the value passed as a variable, `rationale` naming the arbitrary code execution an evaluated expression grants and that the evaluation context does not bound it).

## Source
Spring Framework reference, "Expression Evaluation" §Security Considerations — "evaluating a SpEL expression obtained from an untrusted source is inherently dangerous and should generally be avoided, since doing so can effectively grant that source the ability to execute arbitrary code within the application, regardless of which EvaluationContext implementation is used"; `StandardEvaluationContext` "must never be used to evaluate an expression obtained from an untrusted source". `org.springframework.expression.spel.support.SimpleEvaluationContext` Javadoc — "must not be considered safe for evaluating a SpEL expression obtained from an untrusted source". OWASP ASVS 5.0 requirement 1.3.2. CWE-94.
