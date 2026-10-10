---
title: A temporary feature flag a change introduces is declared with its owner and its expiry date or the event that will retire it, while a flag meant to stay, such as a kill switch, is declared as permanent
rule_id: CHG-36
domain: change
step: [design, implement]
applies_to: [universal]
triggers: ['(?i)\b(feature[_-]?flags?|feature[_-]?toggles?|experiments?)\b', '(?i)\b(new|define|register|create|add)_?(feature_?)?(flag|toggle|experiment)s?\b', '(?i)\b(flag|toggle|gate)\s*\(\s*["'']\w']
scope: file
check_kind: semantic
severity_default: minor
---

# A temporary feature flag a change introduces is declared with its owner and its expiry date or the event that will retire it, while a flag meant to stay, such as a kill switch, is declared as permanent

## Thesis
A feature flag that a change introduces for concurrent development, an experiment, a release or a migration's switch between an old and a new path is declared, when it is created, with its owner and either an expiry date or the event that will make it obsolete, such as the completion of the feature, the end of the experiment or the release of the feature; a flag meant to stay, such as a kill switch or a permission flag, is declared with a permanent lifetime instead.

## Rationale
Flags for concurrent development, experimentation and releases are due for removal once the feature is completed, the experiment is done and the feature is released, yet developers often do not clean up code related to obsolete flags, and that code accumulates as technical debt. When flags are not cleaned up for a long period, determining their owners becomes problematic, since some engineers who worked on them have moved to other teams or left the organization, and a flag whose owner has left the organization can be left with the final status of its rollout unclear. Deciding whether a flag is stale is itself non-trivial, because even a rolled-out flag may be one its developer is not ready to eliminate, such as a kill switch whose value can be changed for emergency purposes. An owner who defines an expiry date when the flag is created states a clear intent, which lets automated cleanup tools generate cleanup diffs without confusing developers, and the recorded owner makes known who is responsible for the flag and for its cleanup. Interviewed practitioners name that metadata, the flag owner and an expiration date or event such as successful integration, as useful yet rarely tracked formally in their organizations. One open-source flag server encodes the same split as an expected lifetime per flag type, about 40 days for release and experiment flags, about 7 days for operational flags that switch between implementations, and permanent for kill-switch and permission flags, and marks a flag potentially stale once its creation time plus its lifetime has passed.

## Example
```python
bad:  CHECKOUT_V2 = Flag("checkout_v2", default=False)
      feature_flags.register_flag(CHECKOUT_V2)
good: CHECKOUT_V2 = Flag("checkout_v2", default=False,
                         owner="checkout-team",
                         retire_when="checkout_v2 serves all traffic")
      feature_flags.register_flag(CHECKOUT_V2)
      PAYMENTS_OFF = Flag("payments_off", default=False,
                          owner="payments-team", permanent=True)
```

## Limits
A configuration option is not a feature flag: configuration options are usually intended to be permanent, whereas feature flags are generally temporary, so the lifetime record, an expiry or a permanent declaration, applies to the flag only, a kill switch or permission flag included. Where the project's flag system assigns a lifetime to a flag type, a declaration that names the type and the owner records the expiry, since staleness is then computed from the flag's creation time plus that type's lifetime; a lifetime set on the flag itself overrides the type's. The rule reaches the declaration the repository holds; a flag created only in an external flag-management service carries its type and lifetime in that service's records.

## Validator
Grep the hunk for an added flag declaration: a constructor, registration call or registry entry that creates a feature flag, toggle or experiment. Open the file and read the fields the declaration sets; a flag type the declaration names stands for the lifetime the project's flag system assigns that type. Check for an owner together with an expiry date or a retiring event, or for a permanent lifetime. Validator question: **Does the hunk add a feature-flag declaration that records neither an owner with an expiry date or retiring event nor a permanent lifetime?** Yes → flag.

## Finding output
When the validator answers yes, the finder emits one finding (`rule_id: CHG-36`, severity minor, `file`, `symbol` = the flag's name, `code` = the added flag declaration quoted verbatim from the diff, `fix` = the same declaration with its owner and its expiry date or retiring event, or with its permanent lifetime, in the file's language, `rationale` = names the missing field and that a flag with no owner or expiry outlives its purpose and leaves its cleanup without a responsible owner).
