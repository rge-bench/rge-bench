# Independent Reproductions

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
| 2026-07-01 | JM-Lab | Spring Boot 4 / Jackson 3 | historical v0, 60 vectors / 11 axes, `sha256:00f0feda78b35d911d2372646e7e759b61cfb41ae9c38a96fb34fd6263f34fd3` | 60/60 reproduced, all eleven axes pass, including `coverage_honesty` | superseded by the current 62-vector digest below |
| 2026-07-03 | JM-Lab | Spring Boot 4 / Jackson 3 | current v0, 62 vectors / 11 axes, `sha256:8603868389a18f8de6f593b03c2c9947bf145c79491f2b095e1da380b6abbc95` | 62/62 reproduced, all eleven axes pass; issuer-vantage vectors match the documented ceiling ranking | maintained checker: [JM-Lab/rge-bench-java](https://github.com/JM-Lab/rge-bench-java), standing log: [JM-Lab/rge-bench-java#1](https://github.com/JM-Lab/rge-bench-java/issues/1) |

Sources: [JM-Lab reproduction thread](https://github.com/JM-Lab/spring-ai-playground/discussions/31)
and [standing checker log](https://github.com/JM-Lab/rge-bench-java/issues/1).

## First independent implementation

[JM-Lab/rge-bench-java](https://github.com/JM-Lab/rge-bench-java) (Spring Boot 4 /
Jackson 3) is the first independent implementation of the checker written to the
README contract, importing nothing from this kit. It reproduces the current
62-vector, 11-axis corpus from inputs alone and matches the pinned
`vectors_digest` byte-for-byte through sorted-key serialization. Native
insertion-order serialization yields a different digest, which is the
declare-the-canonicalization point surfacing in the provenance pin.

## Current status

The corpus moved to 62 vectors on 2026-07-02
(`sha256:8603868389a18f8de6f593b03c2c9947bf145c79491f2b095e1da380b6abbc95`): two `source_class_ceiling`
vectors were added that pin the issuer-vantage boundary (an issuer-signed record supports
`asserted_signed`; recomputing it does not raise its vantage to `independently_confirmed`). JM-Lab
reran the Java checker against this digest on 2026-07-03 with no checker-code change: only the vendored
corpus, pinned digest constant, and README counts changed. Per the digest-scoping rule above, the
62-vector digest is now **reproduced**.

## What the 62-vector reproduction establishes

The current v0 corpus (62 vectors, 11 axes,
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

The first reproduction surfaced three out-of-corpus contract edges. These are now
declared language-neutrally in the README under "Contract edge semantics" and
asserted by `scripts/check_contract_edges.py`:

- present vs empty string for digest fields (`""` is missing);
- explicit `null` vs absent keys (both count as missing);
- numeric semantic equality (`1` and `1.0` are equivalent).

The 2026-07-01 and 2026-07-03 reproductions confirmed these three edges unchanged
and surfaced no new divergence. They do not change the current `vectors_digest`;
they pin how future edge vectors will be interpreted.

## Maintained rerun path

JM-Lab has offered to rerun `JM-Lab/rge-bench-java` against future corpus or axis
changes. Treat that as a fresh-digest gate, not as permission to churn the
corpus: any new `vectors_digest` starts unreproduced until that rerun, or another
independent implementation, matches it from inputs alone or reports a concrete
divergence.

## Version label

The current corpus is now externally reproduced from inputs. Whether to relabel
it from `v0` to `v1` is a separate, deliberate decision. This file records the
reproduction fact, not a version bump.

## Claim ceiling

This file records external reproduction of the current RGE-Bench v0 digest
(`sha256:860386...`) and, historically, the `sha256:00f0feda...` and
`sha256:575fe0...` digests. It is not a claim that the RGE-Bench contract is
complete, that a checked system is safe, or that any evidence source proves more
than its source class and coverage allow. Reproduction is a claim about a digest's
reproducibility from inputs, nothing wider.
