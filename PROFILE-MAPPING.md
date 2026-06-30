# Profile Mapping Note

RGE-Bench is an evidence-reviewability kit. It is not a lifecycle protocol and
does not replace a transition profile that carries separate authorization,
observation, and response-integrity records.

The useful fit is narrower:

```text
lifecycle profile = which records exist, how they join, and which dimension failed
RGE-Bench       = whether retained evidence can support bounded review conclusions
```

That distinction keeps the claim ceiling honest. A three-record profile can say
which authorization, observation, and response claims belong to one transition.
RGE-Bench can then test whether a reviewer can recompute bounded conclusions
from records, coverage, and source class without treating one clean dimension as
proof that all dimensions are clean.

## Mapping to a three-record transition profile

| transition concern | RGE-Bench axis | What the axis checks |
| --- | --- | --- |
| Is there enough evidence to judge this dimension? | `sufficiency` | A valid record with complete coverage can support a positive conclusion. Missing or partial coverage stays incomplete. |
| Did every declared case actually produce a resolvable result? | `coverage_honesty` | A declared expected set bounds confirmation: not-run, errored, or missing-result cases are incomplete; explicit failures may refute. |
| How strong is the observation source? | `source_class_ceiling` | A claim cannot exceed the evidentiary ceiling of the source that captured the observation. |
| Does the observed content match the declared claim? | `recompute` | The reviewer recomputes from retained inputs and ignores prose that is not backed by observed content. |
| Do equivalent records survive envelope changes? | `format_equivalence` | Semantic equality is tested separately from the carrier shape. |
| Does integrity failure stop review? | `tamper_fail_closed` | Missing or mismatched digests are rejected before a positive conclusion. |
| Is absence represented honestly? | `incomplete_visibility` | Absent or unchecked observation is incomplete, not clean. |

## Source-class boundary

The `source_class_ceiling` axis is the bridge between a lifecycle profile and a
bounded reviewer. It separates evidence origin from evidence content.

For example, manifest-bound local observations can be valuable because they bind
bytes to a producer workflow, manifest, path, size, and digest. That is not the
same claim as independent observation-source integrity. A profile should not let
both sources support the same maximum claim unless it can prove they have the
same vantage.

RGE-Bench encodes this as a ceiling rule rather than as a generic pass/fail:

```text
the stronger the claim, the stronger the source class needed to support it
```

This is why the kit reports per-axis pass, partial, or fail and never computes a
single aggregate score. One verified dimension cannot launder a missing or weaker
dimension into a global success.

## How to use this kit with another profile

1. Keep the other profile responsible for record shape, join keys, and lifecycle
   dimensions.
2. Map each profile case onto the RGE-Bench axes it exercises.
3. Recompute the expected outcome from inputs alone.
4. Preserve incomplete and invalid as first-class outcomes.
5. Treat an independent reproduction by a different author or organisation as
   the candidate-to-conformance step.

This mapping is intentionally one-way. RGE-Bench can anchor reviewability
semantics for a profile, but a profile must still define its own records,
canonicalization, identifiers, and negative cases.
