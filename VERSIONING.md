# Versioning and Stability Policy

RGE-Bench versions name the contract surface, not the amount of attention a
digest has received. A vector count change, a documentation clarification, or an
external reproduction does not by itself make a new major version.

## Current version

The current repository state is **`v3-candidate`**: 104 vectors across twelve axes.
Digest `sha256:93f8ae9654eb5a16dee28d882087669cae5183e02e116ba1e8071a30594cfb6a`.
Profile `rge-bench/py-jsondumps/1`.

**No external reproduction. It does not inherit v2's.** The policy requires candidate status for a
fresh digest; it does not force the next major number. This label is a new candidate identity, not a
reuse of historical `v2-candidate`. The 95 original vector entries are preserved. What required the
candidate is newly oracle-bearing contract behavior, not a new axis or outcome vocabulary:

- removed v1 origin names (`boundary_observed`, `third_party_observed`) are `invalid` on
  `source_class_ceiling` even at a strength the old five-class ladder accepted;
- an explicit empty `declared_probe_set` is declared and covers nothing, distinct from missing or
  `null`;
- surface membership is decided before the occurrence branch;
- `receiver_receipt` is subject-controllable, so a covered, gap-free, unseen absence from that
  observer is inconclusive;
- `routing_enforced_by` uses the existing non-empty JSON string presence rule, and a non-string
  value is `invalid` only where step 6 consults routing.

A version bump is not a published reproduction. The JM-Lab v2 run remains scoped to
`sha256:ba0e3795d75c788fa48313ab462493f22d78759851d1b3275d8117051bb22fd0`.

## Previous version

The previous repository state is **`v2`**: 95 vectors across twelve axes.
Digest `sha256:ba0e3795d75c788fa48313ab462493f22d78759851d1b3275d8117051bb22fd0`.
Profile `rge-bench/py-jsondumps/1`.

**Externally reproduced. It does not inherit v1's.** JM-Lab/rge-bench-java reproduced that exact
digest from inputs alone on 2026-08-24 at checker commit
[`a1f7df8`](https://github.com/JM-Lab/rge-bench-java/commit/a1f7df862eec4e8480e6c3f3f4f4cec2ec334982)
([report](https://github.com/JM-Lab/rge-bench-java/issues/1#issuecomment-5391653260)). Three changes
each independently required a candidate label, and v2 made all three:

- a **new axis**, `claim_support`, which grades what an observer's report licenses given the claim kind,
  the observer class and its declared probe set;
- a **new outcome vocabulary** on that axis, including `inconclusive_no_coverage`, anchored on AR4SI's
  inconclusive tier rather than coined;
- **narrowed contract-surface semantics** on `source_class_ceiling`, which drops `boundary_observed` and
  `third_party_observed` and now ranks origin only.

JM-Lab's v1 reproduction read `source_class_ceiling` per the old five-class ladder and is therefore scoped
to the v1 digest.

The earlier `v1` release is the externally reproduced v0 62-vector
corpus plus nine language-neutral contract-edge vectors surfaced by the first
independent implementation:

- empty digest strings fail closed as missing;
- explicit `null` and non-array values fail as missing or invalid where the
  contract expects a present string or array;
- semantic equality ignores object key order, preserves array order, and treats
  JSON numbers by numeric value rather than host boxed type.

The v1 digest is
`sha256:e769822bc6c9e31085da7b1a17b163b9747fe0d04314fbb8685d4e612087c7cb`.
JM-Lab/rge-bench-java reproduced that exact digest from inputs alone on
2026-07-03 with checker commit
[`cd788eb`](https://github.com/JM-Lab/rge-bench-java/commit/cd788eb9453eb8f13c4d910d968b0776b25e7f76).

## Stable labels

- `v0`: first reproduced contract surface. The latest reproduced v0 digest is
  the 62-vector corpus,
  `sha256:8603868389a18f8de6f593b03c2c9947bf145c79491f2b095e1da380b6abbc95`.
- `v1`: reproduced contract-surface release that promotes the previously
  prose-only contract edges into oracled vectors. The latest reproduced v1
  digest is the 71-vector corpus,
  `sha256:e769822bc6c9e31085da7b1a17b163b9747fe0d04314fbb8685d4e612087c7cb`.
- `v2-candidate`: historical candidate label for the same 95-vector digest
  before the 2026-08-24 JM-Lab reproduction. Splits the origin question from
  the vantage question across two axes.
- `v2`: reproduced contract-surface release of that digest. Latest reproduced
  v2 digest is the 95-vector corpus,
  `sha256:ba0e3795d75c788fa48313ab462493f22d78759851d1b3275d8117051bb22fd0`.
- `v3-candidate`: current candidate. Turns the five issue-29 discriminations into
  oracle-bearing corpus behavior and makes malformed routing `invalid` only where
  step 6 consults it. No new axis or outcome vocabulary. No inherited reproduction.

## Change rules

- A fresh `vectors_digest` starts candidate, even if a standing rerun path
  exists.
- Reproduction is digest-scoped; a match for an older digest does not graduate a
  newer one.
- Additive vectors can stay on the same version only when they do not add or
  alter contract-surface semantics.
- New axes, outcome vocabulary changes, or vectors that turn prose-only
  semantics into oracle-bearing corpus behavior require a candidate label and a
  fresh external rerun before a conformance claim.
- The checker emits a per-axis matrix only. No version label may introduce an
  aggregate score, product ranking, or safety/compliance claim.
