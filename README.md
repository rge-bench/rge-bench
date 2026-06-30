# RGE-Bench external reproduction kit (v0)

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
concluded from it** (an unobserved surface reads as incomplete, never clean; integrity fails closed). And it
stays **candidate, not conformance, until a different author or organisation reproduces the vectors from
inputs alone**. You run it rather than take it on trust.

This kit exists so a **different author or organisation** can implement the spec and reproduce the vectors
independently. Two independent, interoperable implementations are the RFC bar for spec maturity; an
external-party reproduction (a different author/org, not the kit's author) is the step that graduates these
vectors from **candidate** to **conformance**. The kit needs nothing outside this directory.

- `vectors.json`: the spec-owned vectors (content-addressed; `vectors_digest` below).
- `checker.py`: the commodity scorer, per-axis pass/partial/fail, **no aggregate score**.
- `ref_example.py`: a clean-room worked example implementation.
- `run.sh`: example impl -> checker.
- `PROFILE-MAPPING.md`: how the axes can anchor the evidence-reviewability layer under a lifecycle
  profile without replacing that profile.

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
`expected` is the outcome a correct reviewer must reach from `inputs` alone. v0 has 60 vectors across the
eleven axes (`base` minimal axis vectors, `ca_*` coding-agent vectors, and `cov.*` coverage-honesty
vectors). The version stays `v0` until an external party reproduces the vectors; the count growing does not
make it `v1`.

## Axes (eleven; literature-anchored, with the rule and the outcome vocabulary)

| axis | rule (recompute from `inputs`) | outcomes | anchor |
| --- | --- | --- | --- |
| `sufficiency` | `sufficient` iff `record_valid` AND `coverage == "complete"`; else `incomplete` | sufficient / incomplete | Beyond Task Success 2604.19818; Evidence-Tracing 2606.04990 |
| `source_class_ceiling` | rank `claim` strength vs the `source_class` ceiling; `within_ceiling` iff strength <= ceiling, else `exceeds_ceiling`; `invalid` if either is unknown | within_ceiling / exceeds_ceiling / invalid | Notarized Agents 2606.04193 |
| `recompute` | `match` iff `set(observed) <= set(declared)`; else `mismatch`. The `description` prose is ignored | match / mismatch | format-agnostic recompute |
| `format_equivalence` | `equivalent` iff `a.semantic == b.semantic` (the envelope `shape` is metadata, excluded); else `distinct` | equivalent / distinct | semantic-digest / equivalence-index |
| `tamper_fail_closed` | `accepted` iff `stored_digest` and `recomputed_digest` are both present and equal; else `rejected` (missing digest fails closed) | accepted / rejected | integrity discipline |
| `incomplete_visibility` | `observed` iff `observation == "present"`; else `incomplete` (absent / not-checked is never clean) | observed / incomplete | Evidence-Tracing 2606.04990 |
| `coverage_honesty` | Given `declared_cases` and retained `case_results`, `refuted` if any declared case explicitly failed; `confirmed` only if every declared case passed; `incomplete` for any not-run, errored, or missing-result case; `invalid` if the declared set is missing. Partial evidence can refute but never confirm | confirmed / refuted / incomplete / invalid | OTel GenAI eval/test telemetry coverage-honesty |
| `delegated_scope` | `within_grant` iff `set(used) <= set(granted)`; else `exceeds_grant`; `invalid` if either is missing. An empty grant authorizes nothing; sub-delegation may narrow, never widen | within_grant / exceeds_grant / invalid | Agent delegation receipts draft-nelson-...; Partial Evidence Bench 2605.05379 |
| `hard_soft_digest` | `rejected_hard` if the hard digest is missing or mismatched (fail closed, soft never consulted); else `soft_equivalent` iff `soft_a == soft_b`, else `soft_divergent` | rejected_hard / soft_equivalent / soft_divergent | C2PA hard/soft binding |
| `retained_replay` | `rejected_carrier` if `carrier_valid` is false (an invalid carrier cannot support replay); else `incomplete` if `records_retained` is false (a valid carrier over absent records); else `replayed_match` iff `set(replayed) == set(recorded)`, else `replayed_mismatch`. Carrier validity is a precondition, not the verdict | replayed_match / replayed_mismatch / incomplete / rejected_carrier | gateway-path replay; SLSA VSA / SCITT |
| `mcp_description_code` | `undeclared_effect` if `code_effects` exceeds `declared_interface`; `over_declared` if the interface declares effects the code never exercises; else `consistent`. When both hold, `undeclared_effect` takes precedence (pinned). The `description` prose is ignored | consistent / undeclared_effect / over_declared | MCP description-code inconsistency 2606.04769 |

Ceiling order (RGE-Bench's proposed ranking, not a standard): `producer_reported` (1) < `issuer_attested`
(2) < `receiver_receipt` (3) < `boundary_observed` (4) < `third_party_observed` (5). Claim strength:
`asserted` (1) < `asserted_signed` (2) < `observed_at_receiver` (3) < `observed_in_path` (4) <
`independently_confirmed` (5).

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

Reproduction is digest-scoped: this 60-vector corpus, including `coverage_honesty`, needs reproduction
against the `vectors_digest` below. A match against an earlier digest does not graduate this corpus.

## Neutrality

Neutrality here rests on what this repository demonstrably enforces, not on a claim about any private bench:

- the axes derive from the literature (anchors above), not from any one product's feature list;
- there is **no scalar / blended score** and so no "winner" — you read the per-axis matrix;
- reference implementations are **scored, never blessed**; `ref_example.py` is the author's own clean-room
  example, explicitly *not* an external reproduction;
- the vectors stay **candidate, not conformance**, until a different author or organisation reproduces them
  from inputs alone — the bench does not certify itself.

## Claim ceiling

Measures the **reviewability of evidence**, not agent safety, correctness, or compliance. A passing vector
means "this evidence is reviewer-gradeable on this axis", never "the agent is safe / governed / compliant".
No scalar winner. Candidate, not conformance, until an external party reproduces the vectors. Every claim in
this kit is something you recompute from the bytes, not something you take on the kit's word.

## Provenance

`vectors_digest: sha256:00f0feda78b35d911d2372646e7e759b61cfb41ae9c38a96fb34fd6263f34fd3`. This is `sha256`
over the **canonical JSON of the `vectors` array** (`json.dumps(doc["vectors"], sort_keys=True,
separators=(",", ":"))` encoded UTF-8), NOT the SHA of the `vectors.json` file bytes (which differs).
Recompute it that exact way to match. Snapshot of the canonical RGE-Bench v0 vector set; the digest pins
it, so an external reproduction is over the same bytes.

A machine-readable manifest is in [`provenance.json`](provenance.json) (digest, vector count, axis list,
family layout, license split, and the candidate-not-conformance non-claim). `scripts/check_provenance.py`
recomputes the digest from `vectors.json` and fails closed if the manifest is stale; it runs in `run.sh`
and CI.

Zenodo archive: concept DOI `10.5281/zenodo.20842502`; v0.1.1 version DOI
`10.5281/zenodo.20842503`.

## License

RGE-Bench uses an explicit dual-license layout, so GitHub may show the repository license as `Other`.
That is expected; the intended split is:

| material | license |
| --- | --- |
| Code (`checker.py`, `ref_example.py`, `run.sh`, CI helpers) | Apache-2.0 |
| Vectors, spec, and docs (`vectors.json`, `README.md`, `PROFILE-MAPPING.md`) | CC-BY-4.0 |

Copyright 2026 RGE-Bench authors. Full canonical texts live in `LICENSES/`; see `LICENSE` for the
human-readable split. CC-BY-4.0 reuse requires attribution to RGE-Bench.
