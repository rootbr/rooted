---
title: The release of a resource is registered immediately after the acquisition is known to have succeeded, never before its error is checked and never after a later step that can fail
rule_id: ERR-30
domain: errors
step: [implement, handle-errors]
applies_to: [universal]
triggers: ['^\s*defer\s+[\w.]+[.](Close|Release|Stop|Rollback|Remove)\(', '^\s*(\}\s*)?finally\s*(:|\{)', '\bif\s*\(?\s*(\w*(stream|Stream|reader|Reader|writer|Writer|conn|Conn|sock|Sock|file|File|fh|fd|stmt|channel|Channel|handle|Handle)\w*|in|out|f|fp|fis|fos|br|bw|rs|r|w)\s*(!=|!==|is\s+not)\s*(null|nil|None|undefined)\b', '\bnew\s+\w+\s*\([^()]*\bnew\s+\w*(InputStream|OutputStream|Reader|Writer|Socket|Channel)\s*\(', '\w\(\s*(\w+\s*=\s*)?open\(', '[.](defer|adopt)\(']
scope: hunk
check_kind: mechanical
severity_default: major
---

# The release of a resource is registered immediately after the acquisition is known to have succeeded, never before its error is checked and never after a later step that can fail

## Thesis
The release of a resource is registered in the statement right after the acquisition is known to have succeeded. The scoped-release construct, the deferred release call, or the protected block whose cleanup releases the resource begins after the check of the error that says whether the resource exists, and before any other call that can fail, such as another acquisition, an operation on the resource, or the constructor of a wrapper built around it. A resource that would be passed straight into the constructor of a wrapper that can fail is acquired in a statement of its own, and its release is registered before the wrapper is built. A release registered before the acquisition's error check, a release registered after a later call that can fail, and a resource created inside the argument list of such a constructor all break the rule.

## Rationale
A release registered before the error check targets a resource that was never acquired: the failed acquisition leaves a null or nil handle, and a registration or release that reaches through it fails with a null or nil dereference. Raised from a cleanup block, that dereference ends the protected block abruptly and propagates in place of the exception the protected code raised, so no handler for that exception can recover from that specific problem. A registration placed after a later step that can fail is never reached when that step fails: the routine returns or throws without releasing the resource. When the constructor of a wrapper fails, a resource created inside its argument list is held by nothing, and nothing can close it; naming it in a statement of its own and registering its release first lets it be closed when the wrapper's construction goes wrong. Registering the release right after the acquisition places the release next to the acquisition, and the release then runs before every later return or thrown error, however many return statements the routine has. Where registrations are kept on a stack that releases first in, last out, registering each one immediately after creating its resource also helps avoid dependency issues between the resources.

## Example
```typescript
bad:  using parser = new RecordParser(new FileReader(path));
      return parser.readAll();
good: using file = new FileReader(path);
      using parser = new RecordParser(file);
      return parser.readAll();
```

## Limits
A cleanup block that also runs when an acquisition inside its protected block failed is correct when each release in it first tests that its resource exists and sits in a cleanup of its own, so that a release that fails cannot skip the ones after it; the release with no existence test is the defect, and a release that can skip the next one leaks it. A scoped-release statement whose header performs the acquisition registers the release in the acquisition's own statement and meets the rule; in it, the check narrows to a resource created inside the argument list of a wrapper's constructor. A value whose type runs its release automatically when it goes out of scope has its release registered by the binding that holds it. A constructor whose argument is not itself a resource, such as a path or a file-name object, and a wrapper whose constructor cannot fail leave nothing unreachable. A routine that returns the resource to its caller does not release it on the path that hands it back, since the standard acquire-then-protect idiom applies when the resource is not handed back, and a release it registers right after the acquisition on a cleanup stack, whose contents it moves out once nothing before the hand-back can fail, meets the rule; how that transfer is stated is judged by its own rule, as are a release made by hand with no registration at all and the order of several releases.

## Validator
Grep the added lines for a deferred release call, a cleanup block, a null or nil test on a resource variable, a resource created inside another constructor's argument list, and a registration on a disposal stack. For each hit, find in the hunk the acquisition the release belongs to and the statement that registers its release: the scoped-release statement, the deferred call, the start of the protected block whose cleanup releases it, or the stack registration. Mark the hit when that registration comes before the check of the acquisition's error; when a call that can fail sits between the successful acquisition and the registration; when a resource is created in the argument list of a wrapper's constructor that can fail and has no registration of its own; or when a cleanup block releases, with no existence test, a resource acquired inside its own protected block. Treat a call or a constructor as able to fail unless the hunk shows it cannot; where signatures declare the errors they raise, a standard-library wrapper whose constructor declares none, such as a buffering wrapper's, cannot fail. Skip a shared cleanup whose releases each test existence and sit in cleanups of their own, a scoped-release statement whose header performs the acquisition and nests no resource inside a wrapper's constructor, a value the language releases when its binding goes out of scope, a constructor whose argument is not a resource, and the path on which the routine hands a resource back to its caller. Validator question: **Is the release of a resource acquired in an added line registered before its acquisition's error check, after a later call that can fail, or never because the resource was created inside a wrapper's constructor that can fail, or is the resource released with no existence test in a cleanup that also runs when its acquisition failed?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: ERR-30`, severity major, `file`, `symbol`, `code` = the acquisition and the misplaced registration, or the nested constructor call, quoted verbatim from the diff, `fix` = the acquisition in a statement of its own, its error check, and directly after it the scoped release, deferred call or protected block, with any wrapper built after that registration, in the file's language, `rationale` = which failure — the acquisition's own, the intervening call's, the wrapper constructor's or, in a shared cleanup, an earlier release's — makes the release run on a missing resource or leaves the resource unreleased).
