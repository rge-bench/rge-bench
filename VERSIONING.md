# Versioning and Stability Policy

RGE-Bench versions name the contract surface, not the amount of attention a
digest has received. A vector count change, a documentation clarification, or an
external reproduction does not by itself make a new major version.

## Current candidate

The current repository state is `v1-candidate`: the externally reproduced v0
62-vector corpus plus nine language-neutral contract-edge vectors surfaced by
the first independent implementation:

- empty digest strings fail closed as missing;
- explicit `null` and non-array values fail as missing or invalid where the
  contract expects a present string or array;
- semantic equality ignores object key order, preserves array order, and treats
  JSON numbers by numeric value rather than host boxed type.

The v1 candidate digest is
`sha256:e769822bc6c9e31085da7b1a17b163b9747fe0d04314fbb8685d4e612087c7cb`.
It is not externally reproduced until JM-Lab/rge-bench-java or another
independent implementation reruns against that exact digest from inputs alone
and matches the per-axis matrix.

## Stable labels

- `v0`: first reproduced contract surface. The latest reproduced v0 digest is
  the 62-vector corpus,
  `sha256:8603868389a18f8de6f593b03c2c9947bf145c79491f2b095e1da380b6abbc95`.
- `v1-candidate`: proposed contract-surface release that promotes the
  previously prose-only contract edges into oracled vectors.
- `v1`: only after the v1-candidate digest is independently reproduced, or the
  candidate is revised and that revised digest is independently reproduced.

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
