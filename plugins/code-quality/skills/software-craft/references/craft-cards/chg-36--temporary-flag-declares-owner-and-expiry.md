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

## Source
- Piranha: Reducing Feature Flag Debt at Uber, ICSE-SEIP 2020, DOI 10.1145/3377813.3381350 (author copy raw.githubusercontent.com/uber/piranha/master/report.pdf) (fetched). §6 Recommendations: "When a feature flag is created initially, the owner of the flag should also define an expiry date for the flag. This clear intent enables automated cleanup tools to generate diffs without confusing developers. Further, the owner for each flag should be tracked precisely." §2: "Oftentimes, developers do not cleanup code related to obsolete flags, causing accumulation of technical debt."; "Orphaned flags: Flags whose owners have left the organization and the final status of the flag roll out is unclear." §3: "Determining whether a flag is stale or not is surprisingly non-trivial"; "Even when it is rolled out, the developer may still not be ready to eliminate the flag. For example, certain flags are used as kill switches whose values can be modified for emergency purposes"; "Since flags were not cleaned up for a long period of time, determining ownership information for stale flags became problematic. A few engineers who worked on the flags either had moved to other teams or had left the organization."
- Exploring Differences and Commonalities between Feature Flags and Configuration Options, ICSE-SEIP 2020, DOI 10.1145/3377813.3381366 (fetched). Sect. 4.4: "configuration options are usually intended to be permanent whereas feature flags are intended to be temporary"; "feature flags for concurrent development, experimentation, and releases should be removed once the feature is completed, the experiment is done, and the feature is released"; "Key differences: Feature flags are generally temporary and should be scheduled for removal, which is not usually a concern for configuration options."; "Recommendation: Be explicit about the expected lifetime of a feature flag and the condition when it will become obsolete." Sect. 4.6: "useful metadata, that is currently rarely tracked formally, such as (a) the flag owner, to know who is responsible for it and who should eventually be blamed for failures and for cleanup, (b) an expiration date or event such as successful integration".
- Unleash flag server, Unleash/unleash main, src/migrations/20260617115403-update-flag-descriptions.js (fetched): "Roll out new or incomplete features. Expected lifetime ~40 days"; "A/B and multivariate testing. Expected lifetime ~40 days"; "Quickly disable certain functionalities or features. Expected lifetime: permanent"; "Transition between technical implementations with minimal risk. Expected lifetime: ~7 days"; "Control feature access based on user roles or entitlements. Expected lifetime: permanent". src/lib/features/feature-toggle/feature-toggle-store.ts, updatePotentiallyStaleFeatures (fetched): "(? > (features.created_at + (NULLIF(COALESCE(features.lifetime_days, (SELECT feature_types.lifetime_days ...".
- kubernetes/community, `contributors/devel/sig-architecture/feature-gates.md` (fetched): "Feature gates are _not_ intended to be long-term APIs. Individual gates are expected to be deprecated and removed after a feature becomes GA (or is dropped)."; "Typically, we add a comment in the code such as: `// remove in 1.23` to signal when we plan to remove the feature gate."; "Truly optional capabilities which are permanently intended to be enabled or disabled by users (even once the feature is GA) should include a mechanism for enabling or disabling the feature (like a command-line flag or config file option) in addition to the associated feature gate."
- Caveat: both papers report industrial practice, one company's flag-cleanup experience and interviews across organizations; the owner-and-expiry record is their recommendation, not a measured effect.
