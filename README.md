# RGE-Bench external reproduction kit (v0)

[![DOI](https://zenodo.org/badge/1280018754.svg)](https://doi.org/10.5281/zenodo.20842502)

A self-contained, neutral conformance kit for **reviewer-grade evidence for agentic actions**: can a third
party, from records + coverage + source-class alone, recompute and honestly conclude? It scores the
**reviewability of the evidence**, not agent performance, safety, or compliance.

This kit exists so a **different author or organisation** can implement the spec and reproduce the vectors
independently. Two independent, interoperable implementations are the RFC bar for spec maturity; an
external-party reproduction (a different author/org, not the kit's author) is the step that graduates these
vectors from **candidate** to **conformance**. The kit needs nothing outside this directory.

- `vectors.json`: the spec-owned vectors (content-addressed; `vectors_digest` below).
- `checker.py`: the commodity scorer, per-axis pass/partial/fail, **no aggregate score**.
- `ref_example.py`: a clean-room worked example implementation.
- `run.sh`: example impl -> checker.

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
`expected` is the outcome a correct reviewer must reach from `inputs` alone. v0 has 32 vectors across the
six axes (a `base` family that defines each axis minimally, and a `ca_*` coding-agent family).

## Axes (six; literature-anchored, with the rule and the outcome vocabulary)

| axis | rule (recompute from `inputs`) | outcomes | anchor |
| --- | --- | --- | --- |
| `sufficiency` | `sufficient` iff `record_valid` AND `coverage == "complete"`; else `incomplete` | sufficient / incomplete | Beyond Task Success 2604.19818; Evidence-Tracing 2606.04990 |
| `source_class_ceiling` | rank `claim` strength vs the `source_class` ceiling; `within_ceiling` iff strength <= ceiling, else `exceeds_ceiling`; `invalid` if either is unknown | within_ceiling / exceeds_ceiling / invalid | Notarized Agents 2606.04193 |
| `recompute` | `match` iff `set(observed) <= set(declared)`; else `mismatch`. The `description` prose is ignored | match / mismatch | format-agnostic recompute |
| `format_equivalence` | `equivalent` iff `a.semantic == b.semantic` (the envelope `shape` is metadata, excluded); else `distinct` | equivalent / distinct | semantic-digest / equivalence-index |
| `tamper_fail_closed` | `accepted` iff `stored_digest` and `recomputed_digest` are both present and equal; else `rejected` (missing digest fails closed) | accepted / rejected | integrity discipline |
| `incomplete_visibility` | `observed` iff `observation == "present"`; else `incomplete` (absent / not-checked is never clean) | observed / incomplete | Evidence-Tracing 2606.04990 |

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

## Neutrality

The axes derive from the literature, not from any one product's feature list. In the full bench the
authoring lab's own implementation is **scored by these same criteria and is deliberately `partial` on
`format_equivalence`** (a clean-room non-author implementation passes it). A bench that its own author does
not top is the evidence that it is neutral and discriminating, not a rubber stamp.

## Claim ceiling

Measures the **reviewability of evidence**, not agent safety, correctness, or compliance. A passing vector
means "this evidence is reviewer-gradeable on this axis", never "the agent is safe / governed / compliant".
No scalar winner. Candidate, not conformance, until an external party reproduces the vectors.

## Provenance

`vectors_digest: sha256:26bff719142c31aa5a5cb2ebe621d1354961a3ac8a0cc77d7e79ad5eeb5d706f`. This is `sha256`
over the **canonical JSON of the `vectors` array** (`json.dumps(doc["vectors"], sort_keys=True,
separators=(",", ":"))` encoded UTF-8), NOT the SHA of the `vectors.json` file bytes (which differs).
Recompute it that exact way to match. Snapshot of the canonical RGE-Bench v0 vector set; the digest pins
it, so an external reproduction is over the same bytes.

Zenodo archive: concept DOI `10.5281/zenodo.20842502`; v0.1.1 version DOI
`10.5281/zenodo.20842503`.

## License

Code (`checker.py`, `ref_example.py`, `run.sh`): Apache-2.0. Vectors, spec, and docs (`vectors.json`, this
README): CC-BY-4.0. Copyright 2026 RGE-Bench authors. Full canonical texts in `LICENSES/`; see
`LICENSE`. CC-BY-4.0 reuse requires attribution to RGE-Bench. Authored by the Assay project lab; licensed as
an RGE-Bench artifact.
