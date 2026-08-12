# Versioning and Stability Policy

RGE-Bench versions name the contract surface, not the amount of attention a
digest has received. A vector count change, a documentation clarification, or an
external reproduction does not by itself make a new major version.

## Current version

The current repository state is **`v2-candidate`**: 95 vectors across twelve axes.
Digest `sha256:ba0e3795d75c788fa48313ab462493f22d78759851d1b3275d8117051bb22fd0`.

**No external reproduction. It does not inherit v1's.** The digest moved once on 2026-08-10, when a
corpus-wide mutation-adequacy check found a declared `source_class_ceiling` outcome that no vector
exercised; two vectors closed it. A digest that moves before anyone has reproduced it costs nothing,
which is the argument for running that check before asking rather than after. Three changes each independently require a
candidate label under the rules below, and this release makes all three:

- a **new axis**, `claim_support`, which grades what an observer's report licenses given the claim kind,
  the observer class and its declared probe set;
- a **new outcome vocabulary** on that axis, including `inconclusive_no_coverage`, anchored on AR4SI's
  inconclusive tier rather than coined;
- **narrowed contract-surface semantics** on `source_class_ceiling`, which drops `boundary_observed` and
  `third_party_observed` and now ranks origin only.

The defect this closes: claim kind was not an input to any of v1's 71 vectors on any of its 11 axes, so
one total order over source classes was applied to occurrence and absence alike. For an absence claim
that order can run backwards — a neutral third party outside the action path is blinded by a free routing
choice, while an observer at a vantage the subject cannot write to is not.

JM-Lab's v1 reproduction read `source_class_ceiling` per the old five-class ladder and is therefore scoped
to the v1 digest.

## Previous version

The current repository state is `v1`: the externally reproduced v0 62-vector
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
- `v2-candidate`: **candidate, not reproduced.** Splits the origin question
  from the vantage question across two axes. No conformance claim attaches to
  this digest until a different author or organisation reproduces it from
  inputs alone.

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
