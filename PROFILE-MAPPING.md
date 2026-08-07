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

> **Changed in `v2-candidate`.** `boundary_observed` and `third_party_observed` are no longer values
> of `source_class_ceiling`; that axis ranks **origin** only. They are observer classes on the new
> `claim_support` axis, so a format now maps to both a *who asserts* value and a *where observed*
> value. A format that never says where its facts were observed maps to "not stated", which is a
> finding rather than a gap in this table.

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

## Ceiling readings for public record formats

The `source_class_ceiling` axis can be read against any public record format. The readings below
classify the vantage each format's own public documentation describes, pinned as of 2026-07-02. They
are readings of public artifacts, not conformance verdicts; if a format's documentation changes or a
reading is wrong, a correction as a pull request is welcome.

Two rules from the axis do all the work here. A ceiling caps the claim rather than rejecting the
record. And signing, hash-chaining, or time-anchoring raise tamper-evidence, never vantage: recomputing
a record confirms what its issuer recorded, it does not upgrade who observed it.

| format (public source) | what the record is, per its own docs | origin class (`source_class_ceiling`) | ceiling (max claim) | observer class (`claim_support`) |
| --- | --- | --- | --- | --- |
| in-toto `agent-decision/v0.1`, proposed predicate ([in-toto/attestation#554](https://github.com/in-toto/attestation/issues/554)) | DSSE-signed record of the authorization decision the agent runtime reports | `issuer_attested` | `asserted_signed` | not stated |
| MCP tool-call execution record, SEP-2828 shape, with published vector suites ([vaaraio/vaara `conformance/sep2828`](https://github.com/vaaraio/vaara/tree/main/conformance/sep2828)) | an in-path proxy or server signs its own decision and outcome record; the published checker recomputes digests and the decision from the record | `issuer_attested` | `asserted_signed` | `boundary_observed` (in-path proxy) |
| AAPR v1 audit chain ([sammysltd/MakerChecker#66](https://github.com/sammysltd/MakerChecker/issues/66), `docs/audit-spec.md`) | hash-chained events a system records about its own actions, with a signed export bundle | `producer_reported` (chain); `issuer_attested` (signed export) | `asserted`; `asserted_signed` | `producer_reported` |
| GuardrailDecision / action-chain records ([safal207/ibex-agent-verification](https://github.com/safal207/ibex-agent-verification)) | framework-recorded decision and action records, with explicit verification-level labels in the profile itself | `producer_reported` | `asserted` | `producer_reported` |
| MCP `evidenceRef` ([experimental-ext-tool-annotations](https://github.com/modelcontextprotocol/experimental-ext-tool-annotations), trust-annotations draft) | a pointer (`type`/`digest`/`canonicalization`), not a record: it enables local re-derivation of whatever it references | inherits the referenced record's class | inherits | inherits |
| observed-effect v0, boundary carrier ([Rul1an/observed-effect-v0](https://github.com/Rul1an/observed-effect-v0)) | an observer below the harness emits the record; the observer is not the component whose behaviour it describes | `boundary_observed` | `observed_in_path` | `independently_observed` |
| gateway replay pack ([Rul1an/gateway-evidence-replay](https://github.com/Rul1an/gateway-evidence-replay)) | replay of captured gateway evidence; replay confirms recomputability and is agnostic to who captured | inherits the capture's class | inherits | inherits |

Two consequences are worth stating plainly. First, none of the issuer-side formats above reach
`independently_confirmed` on this axis, including the ones with the strongest signing and anchoring.
That is not a defect of those formats; it is what an issuer vantage supports, and several of the
formats say so themselves in their own non-claims. Second, the observed-effect row is capped too, and `v2-candidate` splits how. Its **origin** ceiling
is unchanged; its **observer class** is `independently_observed`, which is what lets its silence
support an absence claim at all. A same-organisation boundary observer supports `observed_in_path`, and
`independently_confirmed` requires an observer that a different party operates. The ceiling applies to
every row, including formats by this kit's author.
