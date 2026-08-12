# Independent Reproductions

## v2-candidate — no reproduction yet

Digest `sha256:ba0e3795d75c788fa48313ab462493f22d78759851d1b3275d8117051bb22fd0`, 95 vectors, twelve axes. Published 2026-08-07.

**Nothing here has been reproduced by anyone but the author.**

**Two vectors were added on 2026-08-10 and the digest moved with them.** A mutation-adequacy
check over the whole corpus (`scripts/check_rule_liveness.py`) found that `source_class_ceiling`
declared an `invalid` outcome no vector exercised: deleting the unknown-class and
unknown-strength guard from a conforming implementation reproduced the previous digest. That is
a hole in the contract rather than a gap in confidence, so `scc.edge_unknown_source_class_is_invalid`
and `scc.edge_unknown_claim_strength_is_invalid` close it. Anyone who started against the
90-vector digest `sha256:56d4d41e…` should move to the current one. `ref_example.py` is the author's own
clean-room example and has never counted. The kit's own rule applies to its own release: candidate until
a different author or organisation recomputes every `expected` from `inputs` alone.

What changed, so a reproducer knows where to look:

- **`claim_support` is new** (20 vectors). Its precedence order is contract surface and is numbered in the
  README; the earlier JVM run showed unstated ordering is exactly where a typed reimplementation diverges,
  so expect that to be the friction point again. The steps that discriminate by outcome each have a
  vector; the steps that would produce the same outcome by different routes deliberately do not, because a
  vector that cannot fail for the right reason is not an oracle.
- **An explicitly empty `declared_probe_set` and a `null` one are different answers** — covered-nothing
  versus undeclared. Both are pinned in `scripts/check_contract_edges.py`.
- **`source_class_ceiling` narrowed to three origin classes.** `scc.thirdparty_confirmed` and
  `scc.ca_boundary_within` are gone; `scc.receiver_vantage_overclaim` is new and pins that no origin class
  reaches a vantage strength.
- **`incomplete_visibility` is semantically unchanged.** Only its `non_claims` text moved.

The v1 reproduction below **does not carry over**: it read the five-class ladder this release narrows.


RGE-Bench treats external reproduction as a separate claim from authorship. A
reported reproduction means a different author or organisation recomputed a
specific `vectors_digest` from `inputs` alone and matched the expected per-axis
matrix. Reproduction is digest-scoped: a match against an earlier digest does not
graduate a later corpus.

It does not, by itself, make the broader contract complete or certify any agent,
provider, product, or runtime.

## Reported reproductions

| date | reproducer | stack | digest scope | result | artifact status |
| --- | --- | --- | --- | --- | --- |
| 2026-06-30 | JM-Lab | Spring Boot 4 / Jackson 3 | historical v0, 55 vectors, `sha256:575fe0769153c9f366fa7711c0c4243b6350cb54d5aa36b30459dad91dc67881` | 55/55 reproduced, all ten axes pass | historical; superseded by the current-digest reproduction below |
| 2026-07-01 | JM-Lab | Spring Boot 4 / Jackson 3 | historical v0, 60 vectors / 11 axes, `sha256:00f0feda78b35d911d2372646e7e759b61cfb41ae9c38a96fb34fd6263f34fd3` | 60/60 reproduced, all eleven axes pass, including `coverage_honesty` | superseded by the 62-vector v0 digest below |
| 2026-07-03 | JM-Lab | Spring Boot 4 / Jackson 3 | latest reproduced v0, 62 vectors / 11 axes, `sha256:8603868389a18f8de6f593b03c2c9947bf145c79491f2b095e1da380b6abbc95` | 62/62 reproduced, all eleven axes pass; issuer-vantage vectors match the documented ceiling ranking | maintained checker: [JM-Lab/rge-bench-java](https://github.com/JM-Lab/rge-bench-java), standing log: [JM-Lab/rge-bench-java#1](https://github.com/JM-Lab/rge-bench-java/issues/1) |
| 2026-07-03 | JM-Lab | Spring Boot 4 / Jackson 3 | current v1, 71 vectors / 11 axes, `sha256:e769822bc6c9e31085da7b1a17b163b9747fe0d04314fbb8685d4e612087c7cb` | 71/71 reproduced, all eleven axes pass; first run surfaced typed-JVM drift on the new edge vectors, then the checker implemented the declared language-neutral semantics from the contract text | maintained checker commit: [cd788eb](https://github.com/JM-Lab/rge-bench-java/commit/cd788eb9453eb8f13c4d910d968b0776b25e7f76), standing log: [JM-Lab/rge-bench-java#1](https://github.com/JM-Lab/rge-bench-java/issues/1) |

Sources: [JM-Lab reproduction thread](https://github.com/JM-Lab/spring-ai-playground/discussions/31)
and [standing checker log](https://github.com/JM-Lab/rge-bench-java/issues/1).

## First independent implementation

[JM-Lab/rge-bench-java](https://github.com/JM-Lab/rge-bench-java) (Spring Boot 4 /
Jackson 3) is the first independent implementation of the checker written to the
README contract, importing nothing from this kit. It reproduces the current
v1 71-vector, 11-axis corpus from inputs alone and matches the pinned
`vectors_digest` byte-for-byte through sorted-key serialization. Native
insertion-order serialization yields a different digest, which is the
declare-the-canonicalization point surfacing in the provenance pin.

## Current status

The latest reproduced corpus moved to 62 vectors on 2026-07-02
(`sha256:8603868389a18f8de6f593b03c2c9947bf145c79491f2b095e1da380b6abbc95`): two `source_class_ceiling`
vectors were added that pin the issuer-vantage boundary (an issuer-signed record supports
`asserted_signed`; recomputing it does not raise its vantage to `independently_confirmed`). JM-Lab
reran the Java checker against this digest on 2026-07-03 with no checker-code change: only the vendored
corpus, pinned digest constant, and README counts changed. Per the digest-scoping rule above, the
62-vector digest is now **reproduced**.

The repository now carries a reproduced v1 digest,
`sha256:e769822bc6c9e31085da7b1a17b163b9747fe0d04314fbb8685d4e612087c7cb`,
with 71 vectors. JM-Lab reran `rge-bench-java` against the PR branch on 2026-07-03. The first run did
not reproduce: it threw on the non-array vectors and retained the typed-JVM reading for the digest, null,
and numeric edge cases. JM-Lab then implemented the declared language-neutral semantics from the contract
text rather than from the expected values. With that change, the 71-vector digest reproduced
byte-for-byte and all eleven axes passed.

## What the 62-vector reproduction establishes

The latest reproduced v0 corpus (62 vectors, 11 axes,
`sha256:8603868389a18f8de6f593b03c2c9947bf145c79491f2b095e1da380b6abbc95`) was
independently reproduced by a different author on a different implementation
stack, from its declared inputs and expected outcomes alone. Per this kit's
acceptance criteria, reproduction by a different author or organisation of the vectors from inputs is
the step that moves a corpus from candidate to reproduced. The issuer-vantage
boundary reproduced with the intended reading: `issuer_attested` can support
`asserted_signed`, but recomputing the record does not upgrade it to
`independently_confirmed`.

The earlier historical 55-vector and 60-vector reproductions stay recorded above
as evidence for those digests. They are superseded, not graduated, by the
current-digest reproduction.

## Contract edges (resolved as declared)

The first reproduction surfaced three out-of-corpus contract edges. They were
declared language-neutrally in the README under "Contract edge semantics" and
asserted by `scripts/check_contract_edges.py`:

- present vs empty string for digest fields (`""` is missing);
- explicit `null` vs absent keys (both count as missing);
- numeric semantic equality (`1` and `1.0` are equivalent).

The 2026-07-01 and 2026-07-03 reproductions confirmed these three edges unchanged
and surfaced no new divergence. v1 promotes those edge classes into oracled
vectors, which intentionally created a new `vectors_digest`; the fresh rerun gate
cleared on 2026-07-03 after the independent checker adopted the declared
language-neutral semantics.

## Maintained rerun path

JM-Lab has offered to rerun `JM-Lab/rge-bench-java` against future corpus or axis
changes. Treat that as a fresh-digest gate, not as permission to churn the
corpus: any new `vectors_digest` starts unreproduced until that rerun, or another
independent implementation, matches it from inputs alone or reports a concrete
divergence.

## Version label

The current repository state is v1. The v1 digest is
`sha256:e769822bc6c9e31085da7b1a17b163b9747fe0d04314fbb8685d4e612087c7cb`.
It exists because a contract-surface change happened: previously prose-only
edge semantics are now oracle-bearing vectors. JM-Lab reproduced that exact
digest from inputs alone with `rge-bench-java` commit
[`cd788eb`](https://github.com/JM-Lab/rge-bench-java/commit/cd788eb9453eb8f13c4d910d968b0776b25e7f76).

## Claim ceiling

This file records external reproduction of the current RGE-Bench v1 digest
(`sha256:e76982...`) and, historically, the v0 `sha256:860386...`,
`sha256:00f0feda...`, and `sha256:575fe0...` digests. It is not a claim that the RGE-Bench contract is
complete, that a checked system is safe, or that any evidence source proves more
than its source class and coverage allow. Reproduction is a claim about a digest's
reproducibility from inputs, nothing wider.
