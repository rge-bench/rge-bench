<!-- SPDX-License-Identifier: Apache-2.0 -->
# Vector admission

A conformance corpus makes two different promises, and only one of them is about computation.

**Recomputability.** Can an unrelated implementation derive the same verdict from the published
bytes? This corpus answers yes: `ref_example.py` and `checker.py` are stdlib-only, the vectors carry
their inputs, and `vectors_digest` is a content address over them. Anyone who thinks an expected
outcome is wrong can re-derive it and show their work.

**Admissibility.** Who decides which cases are in the set, and what the expected verdict *means*?
Recomputability says nothing about this. A corpus can be perfectly reproducible and still be one
party's opinion about what matters, because reproducibility governs whether you get the same answer,
not who chose the question.

The distinction is not ours. It was put plainly by vaaraio, answering who ratifies a vector in his
own corpus: "Recompute is checkable by strangers. Authorship is not." safal207 then separated the two
as properties a suite can hold independently, and proposed that a suite must not claim neutrality
solely because its verdicts are independently recomputable. This document is the admission half,
written so that it can be adopted by a corpus this project does not own, and graded against one that
it does.

## What makes a vector admissible

Four criteria. Three are machine-checkable, and that is deliberate: the point is not to eliminate
human judgement, which is impossible, but to shrink the surface on which it operates and to name
exactly where it remains.

**A1. It names the rule it pins.** A vector cites the stated rule whose behaviour it fixes. A vector
that pins behaviour no rule states is pinning an implementation, and the next implementation is
entitled to differ. *Machine-checkable: every vector carries a rule reference and every reference
resolves.*

**A2. It discriminates.** There must exist an implementation that fails it, and fails it because of
the rule it names. The mechanical form: delete the rule from a reference implementation and the
vector must move. A vector that no implementation can fail is not an oracle, whatever it costs to
write. *Machine-checkable: this is mutation adequacy, and `scripts/check_rule_liveness.py` enforces
it here.*

**A3. Its expected verdict follows from the stated rule, not from the implementation.** This is the
criterion that separates a specification corpus from a regression suite. A verdict read off the
reference implementation encodes that implementation's reading, including the parts it got wrong, and
an independent implementer who disagrees has no text to appeal to. *Not machine-checkable. It is the
irreducible judgement, and it is where a second signature earns its keep.*

**A4. A rejecting vector is single-fault.** It carries exactly one defect, and an accepting twin
differing in only that respect ships beside it. Without the twin, a vector that rejects for an
unintended second reason grades as a pass and pins nothing. *Machine-checkable in part: the twin's
existence and its diff can be checked; that the diff isolates the intended fault cannot.*

## Who admits

A corpus states which of these it satisfies, and by whom.

- **Vendor-owned.** One party admits vectors. This is a legitimate state and most corpora are in it.
  What is not legitimate is holding it while claiming neutrality. A vendor-owned corpus says so in a
  machine-readable field, so a consumer reading the artifact rather than the README can tell.
- **Multi-party.** Admission requires signatures from parties who do not share an implementation.
  The rule states how many and what happens when they disagree.

A corpus MUST NOT be another interface's pass-or-fail bar while it is vendor-owned. It may be
published, run, and cited as one vendor's public test set that happens to be independently runnable.
That sentence is vaaraio's own conclusion about his corpus and it applies to ours identically.

## Disagreement and withdrawal

**Two independent implementations that disagree on a vector make it disputed.** A disputed vector is
suspended from the bar until the disagreement resolves, and how it resolved is recorded. The point of
a second implementation is that a disagreement goes red on its own rather than waiting for someone to
notice it.

**A vector found to be wrong is withdrawn, not deleted.** The record keeps what it claimed, why it
was withdrawn, and which digest it was withdrawn at. A corpus that quietly drops its mistakes cannot
be audited on the thing it exists to audit.

## The residual, stated rather than solved

None of this settles who picks the second implementation, or who signs the admission rule itself. That
question has no technical answer; it needs a written rule with more than one signature on it. Anyone
adopting this document inherits that gap, and stating it is the only honest thing available until
somebody actually sets such a rule up.

## Self-application: where RGE-Bench stands

Graded against the above at `v2-candidate`, 92 vectors, digest `sha256:6ccf0593…`.

| | Criterion | Status |
|---|---|---|
| A1 | Vector names the rule it pins | **Partial.** Every vector carries `axis` and `property`, and the README numbers the precedence steps, but no field resolves a vector to a numbered rule. The link is prose. |
| A2 | Vector discriminates | **Enforced.** `check_rule_liveness.py` deletes each declared rule and requires some vector to notice; 27 non-equivalent mutants, 100%, one declared equivalent with its reason. A surviving mutant fails the build. |
| A3 | Verdict follows from the rule, not the implementation | **Failed, and this is the weakest point.** The vectors and `ref_example.py` were authored together. An expected outcome that encodes a misreading of our own rule would reproduce perfectly and nothing here would catch it. |
| A4 | Rejecting vectors are single-fault with an accepting twin | **Unmeasured.** Every axis carries both accepting and rejecting vectors, 2 to 5 distinct expected outcomes each, but that is outcome coverage rather than minimal pairing. Whether a given rejecting vector has an accepting counterpart differing in exactly one respect is not measured anywhere, and no check enforces it. An earlier draft of this row claimed a distribution across vector families that had not been measured, which is the failure this table exists to make expensive. |
| — | Admission is multi-party | **No.** One author admits every vector. There is no second signature, no admission rule prior to this document, and no withdrawal procedure. |
| — | Vendor ownership is machine-readable | **Yes.** `provenance.json` carries `maturity: "candidate (no external reproduction of this digest)"` and `external_reproduction: null`. |

One thing that must not be miscounted in our favour. JM-Lab has reproduced this corpus from inputs
alone on an unrelated stack, and on the v1 run reported a mismatch before reporting the match: his
typed-JVM checker read several edge semantics the JVM way, which is what those vectors were promoted
to catch. `provenance.json` records two of those runs, at 62 and 71 vectors. His own standing log
carries two earlier ones, at 55 and 60, which our record does not, so the artifact under-counts him
rather than over-counting. That is independent **reproduction**, and it is the reason the
recomputability claim is not self-asserted. It is not **admission**: he re-derives verdicts, he does
not vote on which vectors exist or what they should mean. Presenting a reproducer as a ratifier would be exactly the conflation
this document is written to prevent, and his run is scoped to the digest it covered in
`prior_external_reproductions[].scoped_to_digest` so it cannot travel to a corpus it never saw.

So: RGE-Bench is a vendor-owned corpus with one machine-enforced admission criterion, one criterion
it fails outright, and no admission process. It should not be anyone's pass-or-fail bar on that basis,
and this file exists so that reading the artifact tells you so.

## Adopting this

Nothing here depends on this repository. The criteria are properties of a corpus, the enforcement for
A2 is thirty lines over any reference implementation, and the ownership field is one key. A corpus
that adopts it and grades itself worse than this one has done the more useful thing.
