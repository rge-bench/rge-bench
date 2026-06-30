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
| 2026-06-30 | JM-Lab | Spring Boot 4 / Jackson 3 | historical v0, 55 vectors, `sha256:575fe0769153c9f366fa7711c0c4243b6350cb54d5aa36b30459dad91dc67881` | 55/55 reproduced, all ten axes pass | Discussion output published; checker publication pending |

Source: [JM-Lab reproduction report](https://github.com/JM-Lab/spring-ai-playground/discussions/31#discussioncomment-17483980).

## What this establishes

The historical 55-vector corpus was independently reproduced by a different
author on a different implementation stack. This is evidence that the 55-vector
digest was runnable from its declared inputs and expected outcomes, not only by
the reference example in this repository.

## Current reproduction gate

The current v0 corpus has 60 vectors across 11 axes and is pinned by
`sha256:00f0feda78b35d911d2372646e7e759b61cfb41ae9c38a96fb34fd6263f34fd3`.
It adds the `coverage_honesty` axis. That digest has not yet been externally
reproduced, so the current corpus remains candidate, not conformance.

## What remains candidate

The reproduction also surfaced three out-of-corpus contract edges that need a
language-neutral clarification pass before broader conformance wording should be
strengthened:

- present vs empty string for digest fields;
- explicit `null` vs absent keys;
- numeric semantic equality, such as `1` vs `1.0`.

Those probes do not change the 55-vector reproduction result. They are queued as
contract-clarification work so future vectors do not rely on Python/JVM default
behavior.

## Claim ceiling

This file records external reproduction of a historical RGE-Bench v0 digest. It
is not a claim that the current 60-vector digest is externally reproduced, that
the RGE-Bench contract is complete, that a checked system is safe, or that any
evidence source proves more than its source class and coverage allow.
