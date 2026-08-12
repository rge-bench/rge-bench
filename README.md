# RGE-Bench external reproduction kit (v2-candidate)

[![DOI](https://zenodo.org/badge/1280018754.svg)](https://doi.org/10.5281/zenodo.20842502)
[![CI](https://github.com/rge-bench/rge-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/rge-bench/rge-bench/actions/workflows/ci.yml)
![Code license: Apache-2.0](https://img.shields.io/badge/code%20license-Apache--2.0-blue)
![Vectors and docs license: CC-BY-4.0](https://img.shields.io/badge/vectors%20%2B%20docs-CC--BY--4.0-green)

A self-contained, neutral conformance kit for **reviewer-grade evidence for agentic actions**: can a third
party, from records + coverage + source-class alone, recompute and honestly conclude? It scores the
**reviewability of the evidence**, not agent performance, safety, or compliance.

It is a **runnable conformance fixture, not a general theory of truth**: content-addressed vectors plus a commodity
checker that grades **per axis, never a single scalar cleanliness score**. The axes encode what an honest
conclusion is allowed to rest on, so **the source class and the coverage of a record bound what can be
concluded from it** (an unobserved surface reads as incomplete, never clean; integrity fails closed). A digest
stays **candidate, not conformance, until a different author or organisation reproduces the vectors from
inputs alone**. The 71-vector **v1** digest has that evidence: JM-Lab's Spring/Jackson checker reproduced
it from inputs alone, byte-for-byte against the pinned digest.

**The current 95-vector `v2-candidate` digest does not, and does not inherit v1's.** It adds an axis and
an outcome vocabulary and narrows another axis, which `VERSIONING.md` requires be re-reproduced rather
than carried over. Read it as a proposal until someone else runs it.

This kit exists so a **different author or organisation** can implement the spec and reproduce the vectors
independently. Two independent, interoperable implementations are the RFC bar for spec maturity; an
external-party reproduction (a different author/org, not the kit's author) is the step that graduates a
specific digest from **candidate** to **conformance**. v1 has one reported independent reproduction;
`v2-candidate` has none. The kit needs nothing outside this directory.

- `vectors.json`: the spec-owned vectors (content-addressed; `vectors_digest` below).
- `checker.py`: the commodity scorer, per-axis pass/partial/fail, **no aggregate score**.
- `ref_example.py`: a clean-room worked example implementation.
- `run.sh`: example impl -> checker.
- `scripts/check_contract_edges.py`: direct checks for language-neutral edge semantics surfaced by
  independent reproduction.
- `VERSIONING.md`: version-label and fresh-digest stability policy.
- `PROFILE-MAPPING.md`: how the axes can anchor the evidence-reviewability layer under a lifecycle
  profile without replacing that profile.
- `REPRODUCTIONS.md`: reported independent reproductions and the remaining contract edges.

## Reproduce in one contract

Write a program (any language) that:
1. reads `vectors.json`,
2. for each vector recomputes its `expected` outcome **from `inputs` alone** (never read `expected`),
   using the per-axis rules below,
3. writes `out/<your_impl>.json` as `{"impl": "<your_impl>", "outcomes": {"<vector_id>": "<outcome>"}}`,
4. imports nothing from this kit (no shared code; a genuinely independent implementation).

Then run `python3 checker.py`. You have reproduced the vectors when your `outcomes` equal each vector's
`expected` on every axis. Do not transliterate `ref_example.py`; write to this contract, so the
reproduction is independent.

## Vector format

```json
{ "vector_id", "axis", "property", "inputs", "expected", "non_claims" }
```
`expected` is the outcome a correct reviewer must reach from `inputs` alone. `v2-candidate` has 95
vectors across twelve axes: the externally reproduced v0 62-vector corpus, nineteen contract-edge vectors
(`*.edge_*`) that promote previously prose-only semantics into oracle-bearing corpus behavior, and the
`claim_support` axis with the narrowed origin ceiling described below.

## Contract edge semantics

The rules below are intentionally language-neutral. An independent implementation should not inherit Python,
JVM, JavaScript, or YAML library defaults for boundary cases:

- A digest field is **present** only when it is a non-empty JSON string. Missing keys, explicit `null`, and
  `""` all fail closed as missing for digest-gated axes.
- When a rule says an input is missing, an absent key and an explicit `null` both count as missing. If the
  rule expects an array, a non-array value is invalid rather than an empty set.
- Semantic equality for JSON-like values ignores object key order and preserves array order. JSON numbers
  compare by numeric value rather than host boxed type, so `1` and `1.0` are equivalent for
  `format_equivalence` if all other semantic fields match.

These clarifications came from the first independent reproduction report. They were prose-only checks in
v0; v1 makes them part of the corpus and therefore created a fresh digest that required a fresh
external reproduction.

## Version and stability policy

RGE-Bench versions name the contract surface, not the amount of attention a digest has received. Vector
count changes and external reproductions do not by themselves create a new major version. A new
`vectors_digest` starts candidate until a different author or organisation reproduces that exact digest
from inputs alone.

The current digest is `v2-candidate` with 95 vectors:
`sha256:ba0e3795d75c788fa48313ab462493f22d78759851d1b3275d8117051bb22fd0`. **It has no external reproduction.**

The last reproduced digest is v1 with 71 vectors:
`sha256:e769822bc6c9e31085da7b1a17b163b9747fe0d04314fbb8685d4e612087c7cb`.
JM-Lab/rge-bench-java reproduced that exact digest from inputs alone after first surfacing the expected
typed-JVM drift on the newly oracled edge vectors. That reproduction read `source_class_ceiling` per the
old five-class ladder, which `v2-candidate` narrows, so it is scoped to v1 and does not travel. See
[`VERSIONING.md`](VERSIONING.md) and [`REPRODUCTIONS.md`](REPRODUCTIONS.md).

## Axes (twelve; literature-anchored, with the rule and the outcome vocabulary)

| axis | rule (recompute from `inputs`) | outcomes | anchor |
| --- | --- | --- | --- |
| `sufficiency` | `sufficient` iff `record_valid` AND `coverage == "complete"`; else `incomplete` | sufficient / incomplete | Beyond Task Success 2604.19818; Evidence-Tracing 2606.04990 |
| `source_class_ceiling` | **origin only.** Rank `claim` strength vs the `source_class` ceiling; `within_ceiling` iff strength <= ceiling, else `exceeds_ceiling`; `invalid` if either is unknown | within_ceiling / exceeds_ceiling / invalid | Notarized Agents 2606.04193 |
| `recompute` | `match` iff `set(observed) <= set(declared)`; else `mismatch`. The `description` prose is ignored | match / mismatch | format-agnostic recompute |
| `format_equivalence` | `equivalent` iff `a.semantic == b.semantic` (the envelope `shape` is metadata, excluded); else `distinct` | equivalent / distinct | semantic-digest / equivalence-index |
| `tamper_fail_closed` | `accepted` iff `stored_digest` and `recomputed_digest` are both present and equal; else `rejected` (missing digest fails closed) | accepted / rejected | integrity discipline |
| `incomplete_visibility` | `observed` iff `observation == "present"`; else `incomplete` (absent / not-checked is never clean). **Grades whether an observation was made, never whether the resulting silence is supported** | observed / incomplete | Evidence-Tracing 2606.04990 |
| `coverage_honesty` | Given `declared_cases` and retained `case_results`, `refuted` if any declared case explicitly failed; `confirmed` only if every declared case passed; `incomplete` for any not-run, errored, or missing-result case; `invalid` if the declared set is missing. Partial evidence can refute but never confirm | confirmed / refuted / incomplete / invalid | OTel GenAI eval/test telemetry coverage-honesty |
| `delegated_scope` | `within_grant` iff `set(used) <= set(granted)`; else `exceeds_grant`; `invalid` if either is missing. An empty grant authorizes nothing; sub-delegation may narrow, never widen | within_grant / exceeds_grant / invalid | Agent delegation receipts draft-nelson-...; Partial Evidence Bench 2605.05379 |
| `hard_soft_digest` | `rejected_hard` if the hard digest is missing or mismatched (fail closed, soft never consulted); else `soft_equivalent` iff `soft_a == soft_b`, else `soft_divergent` | rejected_hard / soft_equivalent / soft_divergent | C2PA hard/soft binding |
| `retained_replay` | `rejected_carrier` if `carrier_valid` is false (an invalid carrier cannot support replay); else `incomplete` if `records_retained` is false (a valid carrier over absent records); else `replayed_match` iff `set(replayed) == set(recorded)`, else `replayed_mismatch`. Carrier validity is a precondition, not the verdict | replayed_match / replayed_mismatch / incomplete / rejected_carrier | gateway-path replay; SLSA VSA / SCITT |
| `claim_support` | **vantage.** Given `claim.kind`, `claim.surface`, `observer.class`, its `declared_probe_set` and any `routing_enforced_by`, and the `observation`, decide what this observer's report licenses. Precedence below is contract surface | supported / unsupported / contradicted / inconclusive_no_coverage / invalid | blinding cost (ARMO 2026-05-22); AR4SI `draft-ietf-rats-ar4si`; kernel vantage AgentSight 2508.02736 |
| `mcp_description_code` | `undeclared_effect` if `code_effects` exceeds `declared_interface`; `over_declared` if the interface declares effects the code never exercises; else `consistent`. When both hold, `undeclared_effect` takes precedence (pinned). The `description` prose is ignored | consistent / undeclared_effect / over_declared | MCP description-code inconsistency 2606.04769 |

### Two questions, two axes (changed in `v2-candidate`)

Until v1 one ordinal ladder answered two different questions: **who asserts this** and **where was it
observed**. A single total order cannot be right for both, because it is applied to every claim and the
right order depends on what is being claimed. So they are split.

**`source_class_ceiling` — origin.** Ceiling order (RGE-Bench's proposed ranking, not a standard):
`producer_reported` (1) < `issuer_attested` (2) < `receiver_receipt` (3). Claim strength: `asserted` (1) <
`asserted_signed` (2) < `observed_at_receiver` (3) < `observed_in_path` (4) < `independently_confirmed`
(5). The two strengths above the top of the ladder are reachable by **no origin class at all**, which is
the statement the narrowing makes: origin never licenses a vantage claim.

**A note on the field name, because this repository is one of several places it is in use.** Three
vocabularies in this project already spell it the same way and rank different things.
[`source-class-v0`](https://github.com/Rul1an/source-class-v0) types seven classes and says of itself
that it is typing, not ranking. Here, `source_class_ceiling` ranks three of those values as *origin*.
`claim_support` uses five of them as observer classes for *vantage*. Adjacent work carries a standing
ladder under the same name, running from a self-report to a registered-independent issuer. At least one
proposal decomposing independence carries both a `source_class` and a `relationship_class`, and puts the
issuer-standing value in the first while the second carries the stake claim.

We know what conflation costs because v1 paid it: the ceiling ranked origin and vantage together, mixing
`producer_reported` and `issuer_attested` with `third_party_observed` and `boundary_observed`.
Separating them took a release, a narrowed axis, a new one (`claim_support`), and a digest that
deliberately did not inherit v1's reproduction. If you are mapping this corpus onto another vocabulary,
map on what the field ranks rather than on what it is called.

**`claim_support` — vantage.** Observer classes, taken from
[`source-class-v0`](https://github.com/Rul1an/source-class-v0) rather than coined here:
`producer_reported`, `receiver_receipt`, `boundary_observed`, `third_party_observed`,
`independently_observed`. A class this reader cannot type yields `invalid`, fail-closed.

**`blinding_cost` is derived, never declared.** A producer cannot assert that it is hard to blind. The
predicate is computed from the class and from `routing_enforced_by`: an observer the subject can blind
without privilege cannot support an absence claim *unless* its routing is enforced by a party the subject
does not control. That escape is why this is a typing and not a demotion — the class is not a caste.

Note that `producer_reported` and `receiver_receipt` appear on **both** lists. That is not an error: a
party that asserts is also a party that saw. It is precisely why one ordinal axis over the union cannot
work, since the same value sits at different heights depending on which question is asked.

### `claim_support` precedence (contract surface; each step has a vector where the outcomes discriminate)

0. `observer.class` untypeable, or `claim.kind` outside `occurrence`/`absence` → `invalid`
1. no `declared_probe_set` and `kind == absence` → `invalid` — a reader cannot tell a covered silence
   from an uncovered one, so the claim is unjudgeable rather than weak. This outranks step 2.
2. `declared_probe_set` present and `claim.surface` not in it → `inconclusive_no_coverage`
3. `observation.observation_gap` and `kind == absence` → `inconclusive_no_coverage`
4. `kind == occurrence` → `supported` if `saw_event`, else `unsupported`
5. `kind == absence` and `saw_event` → `contradicted`
6. `kind == absence` and the subject can blind this observer (see above) → `inconclusive_no_coverage`
7. otherwise → `supported`

An explicitly empty `declared_probe_set` is **declared and covers nothing** (step 2); a `null` or absent
one is **undeclared** (step 1). The two are different answers on purpose.

**On `inconclusive_no_coverage`.** Borrowed rather than coined: AR4SI
([`draft-ietf-rats-ar4si`](https://datatracker.ietf.org/doc/draft-ietf-rats-ar4si/)) reserves a tier for an
appraisal that is *inconclusive rather than a pass or a fail*, and that is this outcome's shape. It is not
a weaker `unsupported`; it says the question was not reachable from this vantage.

## Scoring (per-axis; NO aggregate score, by design)

The checker grades each impl per axis as `pass` (all reproduced), `partial` (some), or `fail` (none), and
emits a matrix (impls x axes). It computes **no scalar / blended score**: a single number is exactly the
reduction the 2026 benchmark critique warns against and would re-introduce a "winner". Read the matrix per
axis. Reference implementations are **scored, never blessed**.

## Acceptance: what counts as an external-party reproduction

A reproduction is an **independent** program by a different author/org that reads `vectors.json`, recomputes
each `expected` from `inputs`, imports nothing from this kit, and matches the per-axis matrix. That is the
step that graduates the vectors from candidate to conformance. (Within this kit, `ref_example.py` is the
author's own clean-room example, not an external reproduction.)

Reproduction is digest-scoped: the 71-vector v1 corpus has one reported independent reproduction and the
current 95-vector `v2-candidate` corpus has none.
A match against an earlier digest would not graduate this corpus; earlier 55-vector, 60-vector, and
62-vector digests are recorded separately. See
[`REPRODUCTIONS.md`](REPRODUCTIONS.md) for both reproductions and for contract-clarification work surfaced
by the first run.

## Neutrality

Neutrality here rests on what this repository demonstrably enforces, not on a claim about any private bench:

- the axes derive from the literature (anchors above), not from any one product's feature list;
- there is **no scalar / blended score** and so no "winner"; you read the per-axis matrix;
- reference implementations are **scored, never blessed**; `ref_example.py` is the author's own clean-room
  example, explicitly *not* an external reproduction;
- a digest stays **candidate, not conformance**, until a different author or organisation reproduces it from
  inputs alone; v1 has one reported independent reproduction, `v2-candidate` has none, and the bench does
  not certify itself.

## Claim ceiling

Measures the **reviewability of evidence**, not agent safety, correctness, or compliance. A passing vector
means "this evidence is reviewer-gradeable on this axis", never "the agent is safe / governed / compliant".
No scalar winner. Reproduction status is digest-scoped: the 60-vector and 62-vector v0 digests and the
71-vector v1 digest have reported independent reproduction; the current `v2-candidate` digest does not. Every claim in this kit is
something you recompute from the bytes, not something you take on the kit's word.

## Provenance

`vectors_digest: sha256:ba0e3795d75c788fa48313ab462493f22d78759851d1b3275d8117051bb22fd0`. This is `sha256`
over the **canonical JSON of the `vectors` array** (`json.dumps(doc["vectors"], sort_keys=True,
separators=(",", ":"))` encoded UTF-8), NOT the SHA of the `vectors.json` file bytes (which differs).
Recompute it that exact way to match. Snapshot of the canonical RGE-Bench v1 vector set; the
digest pins it, so an external reproduction is over the same bytes.

A machine-readable manifest is in [`provenance.json`](provenance.json) (digest, vector count, axis list,
family layout, license split, and the digest-scoped conformance non-claim). `scripts/check_provenance.py`
recomputes the digest from `vectors.json` and fails closed if the manifest is stale; it runs in `run.sh`
and CI.

Zenodo archive: concept DOI `10.5281/zenodo.20842502`; v0.1.1 version DOI
`10.5281/zenodo.20842503`.

## License

RGE-Bench uses an explicit dual-license layout. The root `LICENSE` file carries the Apache-2.0 text
(the code license) so the repository license is machine-detectable; the split itself is unchanged:

| material | license |
| --- | --- |
| Code (`checker.py`, `ref_example.py`, `run.sh`, CI helpers) | Apache-2.0 |
| Vectors, spec, and docs (`vectors.json`, `README.md`, `PROFILE-MAPPING.md`) | CC-BY-4.0 |

Copyright 2026 RGE-Bench authors. Full canonical texts live in `LICENSES/`; see `LICENSING.md` for the
human-readable split. CC-BY-4.0 reuse requires attribution to RGE-Bench.
