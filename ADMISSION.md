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

The distinction is not ours, and neither is most of the language for it. It was put plainly by
vaaraio, answering who ratifies a vector in his own corpus: "Recompute is checkable by strangers.
Authorship is not." Sixteen minutes later safal207 named the two properties and proposed the
invariant, quoted whole because the second half is the one we most need:

> A suite MUST NOT claim neutrality solely because its verdicts are independently recomputable; its
> vector-admission and ratification process must also be externally governed or explicitly identified
> as vendor-owned.

His terms are **Recomputability** and **Ratifiability**. This document says "admissibility" for the
second, which is a narrower word for the mechanics of admitting a vector rather than for the
governance around it, and the substitution is ours rather than his. Two further formulations below
are vaaraio's and are marked where they appear.

Both comments are on [crewAIInc/crewAI#4877](https://github.com/crewAIInc/crewAI/issues/4877):
[vaaraio](https://github.com/crewAIInc/crewAI/issues/4877#issuecomment-5263327237) and
[safal207](https://github.com/crewAIInc/crewAI/issues/4877#issuecomment-5263451205). Neither author
has seen or endorsed this document. The criteria below are ours, and so are the errors in them.

This is the admission half, written so that it can be adopted by a corpus this project does not own,
and graded against one that it does.

## What makes a vector admissible

Four criteria. Three are machine-checkable in principle and one is checked in this repository today, and that gap is deliberate to state: the point is not to eliminate
human judgement, which is impossible, but to shrink the surface on which it operates and to name
exactly where it remains.

**A1. It names the rule it pins.** A vector cites the stated rule whose behaviour it fixes. A vector
that pins behaviour no rule states is pinning an implementation, and the next implementation is
entitled to differ. *Machine-checkable: every vector carries a rule reference and every reference
resolves.*

**A2. It discriminates.** There must exist an implementation that fails it, and fails it because of
the rule it names. The mechanical form: delete the rule from a reference implementation and the
vector must move. A vector that no implementation can fail is not an oracle, whatever it costs to
write. *Machine-checkable in part: this is mutation adequacy. `scripts/check_rule_liveness.py` enforces the
rule-side half, that every declared rule is killed by some vector, over a mutant set declared by hand,
roughly one per branch rather than one per failure mode, with equivalent mutants excluded by
declaration rather than inferred. The vector-side half, that every vector is moved by some mutant, is
not enforced anywhere.*

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
suspended from the bar until the disagreement resolves, and how it resolved is recorded. The point of a second implementation, in vaaraio's words, is that two graders disagreeing "goes red
on its own instead of waiting for someone to spot it".

**A vector found to be wrong is withdrawn, not deleted.** The record keeps what it claimed, why it
was withdrawn, and which digest it was withdrawn at. A corpus that quietly drops its mistakes cannot
be audited on the thing it exists to audit.

## The residual, stated rather than solved

None of this settles who picks the second implementation, or who signs the admission rule itself. That question, again in vaaraio's words, does not have a technical answer, "only a written rule with
more than one signature on it". Anyone
adopting this document inherits that gap, and stating it is the only honest thing available until
somebody actually sets such a rule up.

## Self-application: where RGE-Bench stands

Graded against the above at `v2-candidate`, 95 vectors, digest `sha256:ba0e3795…`.

| | Criterion | Status |
|---|---|---|
| A1 | Vector names the rule it pins | **Not met.** No vector carries a rule reference. The fields are `vector_id`, `axis`, `property`, `inputs`, `expected`, `non_claims`, and 0 of 95 resolve to a numbered rule. `axis` is a category and `property` is prose. The README numbers the `claim_support` precedence steps and no other axis, and nothing checks the link. |
| A2 | Vector discriminates | **Enforced for declared rules only.** `check_rule_liveness.py` deletes each hand-declared rule and requires some vector to notice: 27 non-equivalent mutants, 100%, one declared equivalent with reason, and a surviving mutant fails the build under positive control. Two limits it does not carry. The mutant set is written by hand and nothing checks it against the rules `ref_example.py` actually contains. And A2 is stated as a property of a vector while the script checks the converse property of a rule, so 31 of 92 vectors were moved by no declared mutant at the digest before this one. Adversarial review of this document found the consequence: the `source_class_ceiling` ladder could be flattened to rank every origin class identically and the whole suite stayed green, because every rejecting vector used a strength above every ceiling. Three vectors close it and the digest moved to `sha256:ba0e3795…`. |
| A3 | Verdict follows from the rule, not the implementation | **Failed, and this is the weakest point.** The vectors and `ref_example.py` were authored together. An expected outcome that encodes a misreading of our own rule would reproduce perfectly and no check here would catch it. The only thing that ever has is an independent implementer reading the README instead of the code: JM-Lab's first v1 run diverged on the contract-edge semantics before it converged. That covers the v1 corpus, not this digest. |
| A4 | Rejecting vectors are single-fault with an accepting twin | **Unmeasured.** Every axis carries both accepting and rejecting vectors, 2 to 5 distinct expected outcomes each, but that is outcome coverage rather than minimal pairing. Whether a given rejecting vector has an accepting counterpart differing in exactly one respect is not measured anywhere, and no check enforces it. An earlier draft of this row claimed a distribution across vector families that had not been measured, which is the failure this table exists to make expensive. |
| | Admission is multi-party | **No.** One author admits every vector. There is no second signature, no admission rule prior to this document, and no withdrawal procedure. |
| | Vendor ownership is machine-readable | **No.** No field names the admission mode. `maturity` and `external_reproduction` record whether anyone has reproduced this digest, which is the recomputability question this document opens by separating from admissibility, and `spec_owner: "RGE-Bench authors"` names a party rather than a process. Single-party admission is inferable only from prose. Adding the key is open work, and this row is the rule at the top of this file failing against its own author. |

One thing that must not be miscounted in our favour. JM-Lab has reproduced **earlier digests** of
this corpus from inputs alone on an unrelated stack, and on the v1 run reported a mismatch before
reporting the match: his typed-JVM checker read several edge semantics the JVM way, which is what
those vectors were promoted to catch. **No one has reproduced this digest**, and `provenance.json`
says so with `external_reproduction: null`. `REPRODUCTIONS.md` carries four of his runs, at 55, 60,
62 and 71 vectors; `provenance.json` carries the last two. Those four are not a tally: they are four
digests across two corpus generations, so there is no single count to run hot or cold, and what
matters is that none of them covers this one. That is independent **reproduction**, and it is the
reason the recomputability claim is not self-asserted. It is not **admission**: he re-derives
verdicts, he does not vote on which vectors exist or what they should mean. Presenting a reproducer as a ratifier would be exactly the conflation
this document is written to prevent, and his run is scoped to the digest it covered in
`prior_external_reproductions[].scoped_to_digest` so it cannot travel to a corpus it never saw.

So: RGE-Bench is a vendor-owned corpus with one machine-enforced admission criterion, one criterion
it fails outright, and no admission process. It should not be anyone's pass-or-fail bar on that basis,
and this file exists so that reading the artifact tells you so.

## Adopting this

The criteria are properties of a corpus and do not depend on this repository. The enforcement does.
`check_rule_liveness.py` is 331 lines, of which 161 are a mutant table written against literal source
substrings of this `ref_example.py`, and the machinery assumes a single `evaluate(axis, inputs)` entry
point and vectors carrying `vector_id`, `axis` and `inputs`. Budget the machinery and expect to
rewrite the table per corpus. The ownership field is one key, and this corpus does not have it yet. A corpus that adopts it and publishes the grade it actually earns has done the useful thing, whatever
the grade says.
