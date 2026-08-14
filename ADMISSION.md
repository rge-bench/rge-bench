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
roughly one per branch plus permutations of the one ordinal ladder, rather than one per failure mode,
which is the shape that let an unmutated ordering through once already, with equivalent mutants excluded by
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

The machine-readable form of all of this is the `admission` object in `provenance.json`: `mode`, the
parties who may admit, how many signatures a vector needs, the content-address of the rule text in
force, and `may_be_a_conformance_bar`, which is the sentence above as a boolean a consumer can read
without parsing prose. `scripts/check_provenance.py` reads it rather than trusting it: it recomputes
`rule_digest` over this file's raw bytes, pins `rule` to this file by name so the digest cannot be
satisfied by content-addressing some other file in the repo, requires at least as many admitting
parties as signatures, and refuses any corpus that declares itself usable as a pass-or-fail bar while
requiring fewer than two signatures — the last regardless of `mode`, because otherwise the one MUST
NOT in this document is bypassed by editing one string. Unknown keys are rejected, since a
misspelled key that silently does nothing is the failure this block exists to prevent.

What that buys, stated at its actual size: a consumer can tell which rule text a corpus admitted
under, and a corpus cannot quietly contradict the bar rule. It does not make the declaration true. A
party can still write `multi_party` and list two names that are the same person. **The field is a
statement whose internal consistency is checked, not an attestation that anyone verified the
statement**, and the difference is the same recomputability-versus-admissibility line this document
opens with. A field nobody reads is not a rule, which is the failure this document's A2 exists to
catch one level down; a field that is read but only for self-consistency is a weaker thing than an
audited one, and it is the weaker thing that is shipping here.

## Disagreement and withdrawal

**Two independent implementations that disagree on a vector make it disputed.** A disputed vector is
suspended from the bar until the disagreement resolves, and how it resolved is recorded. The point of a second implementation, in vaaraio's words, is that two graders disagreeing "goes red
on its own instead of waiting for someone to spot it".

**A vector found to be wrong is withdrawn, not deleted.** The record keeps what it claimed, why it
was withdrawn, and which digest it was withdrawn at. A corpus that quietly drops its mistakes cannot
be audited on the thing it exists to audit.

## The residual: one half has a known answer, the other does not

Two questions were left open here: who picks the second implementation, and who signs the admission
rule itself. They are not equally open, and treating them as one gap overstated the difficulty of the
first.

**Who picks the second implementation has a standing answer, and the answer is that nobody picks.**
RFC 6410 §2.2 sets the bar for advancing a specification to Internet Standard: "There are at least two
independent interoperating implementations with widespread deployment and successful operational
experience." Selection is replaced by an existence requirement, and by a public objection window: the
IESG confirms the advancement "in an IETF-wide Last Call of at least four weeks". That formulation is
from 2011; the underlying two-implementation rule is older, RFC 2026 §4.1.2, which required "at least
two independent and interoperable implementations from different code bases". RFC 6410 updates RFC
2026 and, on this criterion, **dropped the different-code-bases clause** — so a corpus that wants
implementations sharing no code is asking for RFC 2026's bar, not RFC 6410's, and should say which.

**This is an adaptation, not an import, and the difference is not cosmetic.** RFC 6410's criterion has
four parts and the version below keeps one. Three places it does not carry:

1. *Interoperation is not oracle replication.* RFC 6410 requires implementations that **interoperate**
   — a symmetric behavioural relation between running systems exchanging data. A corpus's second
   implementation does not interoperate with the first; it independently re-derives a verdict. Those
   are different relations, and the second is weaker.
2. *Deployment and operational experience are dropped entirely.* "Widespread deployment and successful
   operational experience" is what makes RFC 6410's bar expensive. A corpus rule that keeps only
   independence and agreement has kept the cheap half.
3. *Granularity and standing.* RFC 6410 advances a *specification*, not a *vector*, and a vector is the
   smaller and more numerous object — a four-week window per vector would stop a corpus moving, so any
   window belongs to a digest. And the IETF has a standing body to run the Last Call and rule on
   objections. A corpus without one has the rule and nobody to execute it, which is not a
   technicality: an objection window with no one obliged to answer an objection is decoration.

With those stated, the adapted rule is: a vector reaches the bar when two implementations that do not
share an author have independently derived its expected verdict, and it stays proposed until a stated
objection window on the digest has passed with no unresolved dispute. Borrowing the shape of a
standards process does not borrow its weight, and a corpus that cites RFC 6410 while keeping one of
its four criteria should not be read as having met it.

**Who signs the admission rule itself remains open, and RFC 6410 does not help.** The IETF's process
is ratified by the IETF; a rule is self-ratifying only inside a body that already exists. The honest
position is unchanged on this half, and it is vaaraio's. His words, hedged as he hedged them: "I do
not think that has a technical answer, only a written rule with more than one signature on it." What
this section adds is only that the shape such a rule would take is no longer undefined. It does not
add a signature, and nothing here should be read as one.

## Self-application: where RGE-Bench stands

Graded against the above at `v2-candidate`, 95 vectors, digest `sha256:ba0e3795…`.

| | Criterion | Status |
|---|---|---|
| A1 | Vector names the rule it pins | **Not met.** No vector carries a rule reference. The fields are `vector_id`, `axis`, `property`, `inputs`, `expected`, `non_claims`, and 0 of 95 resolve to a numbered rule. `axis` is a category and `property` is prose. The README numbers the `claim_support` precedence steps and no other axis, and nothing checks the link. |
| A2 | Vector discriminates | **Enforced for declared rules only.** `check_rule_liveness.py` deletes or permutes each hand-declared rule and requires some vector to notice: 30 non-equivalent mutants, 100%, one declared equivalent with reason, and a surviving mutant fails the build under positive control. Two limits it does not carry. The mutant set is written by hand and nothing checks it against the rules `ref_example.py` actually contains. And A2 is stated as a property of a vector while the script checks the converse property of a rule, so 31 of 92 vectors were moved by no declared mutant at the digest before this one. Adversarial review of this document found the consequence: the `source_class_ceiling` ladder could be flattened to rank every origin class identically and the whole suite stayed green, because every rejecting vector used a strength above every ceiling. Three vectors close it and the digest moved to `sha256:ba0e3795…`. **What that fix claimed, corrected.** `43f20f5` closes its message with "flattened, the axis now scores 9/11 and `run.sh` exits 1", and the second half is false. Measured at that commit and at `aa316d9`: flattening the ladder to the highest ceiling, flattening it to the lowest, and inverting it each move exactly two vectors, drop the axis to `partial 9/11`, and leave `run.sh` at **exit 0**. `checker.py` returns 0 unconditionally after printing the matrix and has not been modified since the initial commit, so a `partial` axis carries no exit-code consequence and never did. The claim was wrong when it shipped; it is corrected here rather than by rewriting the commit, which is what this file's withdrawal rule already asks of a wrong vector and has no reason to excuse in a claim about the suite. Whether `run.sh` *should* gate on a partial axis is left open deliberately, not settled by this correction: `checker.py` prints that these reference impls do not top every axis, so a partial score is expected output for some implementations, and gating on it would change what the runner means. **What the fix did not carry.** Three vectors closed the hole with no mutant guarding them, so the ladder could be re-ordered and the adequacy check still scored 100%. `source_class_ceiling` now carries three permutation mutants — flatten up, flatten down, invert — each killed by two vectors, and for each of them, removing its killers makes it survive and the check exit 1. Ordering is the one rule shape a deletion mutant cannot reach, since it lives in a table read by a comparison rather than in a branch; this is the only ordinal axis here, so no other axis carries one. One consequence worth stating exactly: as of this change an edited ladder does turn `run.sh` red, but through the anchor guard reporting that the mutant's literal source substring is gone, which detects the rewrite rather than the axis scoring partial. The partial score still means nothing to the exit code. None of this touches the vector-side half of A2, that every vector is moved by some mutant, which remains unenforced. |
| A3 | Verdict follows from the rule, not the implementation | **Failed, and this is the weakest point.** The vectors and `ref_example.py` were authored together. An expected outcome that encodes a misreading of our own rule would reproduce perfectly and no check here would catch it. The only thing that ever has is an independent implementer reading the README instead of the code: JM-Lab's first v1 run diverged on the contract-edge semantics before it converged. That covers the v1 corpus, not this digest. |
| A4 | Rejecting vectors are single-fault with an accepting twin | **Unmeasured.** Every axis carries both accepting and rejecting vectors, 2 to 5 distinct expected outcomes each, but that is outcome coverage rather than minimal pairing. Whether a given rejecting vector has an accepting counterpart differing in exactly one respect is not measured anywhere, and no check enforces it. An earlier draft of this row claimed a distribution across vector families that had not been measured, which is the failure this table exists to make expensive. |
| | Admission is multi-party | **No.** One author admits every vector. There is no second signature, no admission rule prior to this document, and no withdrawal procedure. |
| | Vendor ownership is machine-readable | **Met, and it was the one open row this file could close by itself.** `provenance.json` now carries an `admission` object: `mode: "vendor_owned"`, `admitting_parties`, `signatures_required: 1`, `rule: "ADMISSION.md"`, `rule_digest`, `may_be_a_conformance_bar: false`, and an empty `withdrawn` list. `scripts/check_provenance.py` recomputes `rule_digest` over this file's bytes and fails closed on a mismatch, so the row cannot rot back into prose the way it started. What it does **not** do is upgrade anything: the mode it publishes is `vendor_owned`, which is the same fact the previous version of this row confessed, now stated where a consumer reads it instead of where a reader has to. **Prior state, kept rather than overwritten:** "No field names the admission mode... Single-party admission is inferable only from prose. Adding the key is open work, and this row is the rule at the top of this file failing against its own author." |

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
`check_rule_liveness.py` is 359 lines, of which 183 are a mutant table written against literal source
substrings of this `ref_example.py`, and the machinery assumes a single `evaluate(axis, inputs)` entry
point and vectors carrying `vector_id`, `axis` and `inputs`. Budget the machinery and expect to
rewrite the table per corpus. The ownership block is cheaper: seven keys in `provenance.json` and the
`_check_admission` function in `check_provenance.py`, which is corpus-independent apart from the
filename it pins. A corpus that adopts it and publishes the grade it actually earns has done the
useful thing, whatever the grade says.
