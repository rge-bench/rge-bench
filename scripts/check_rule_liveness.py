#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Mutation adequacy of the corpus, measured against the rules it claims to fix.

Outcome coverage is not rule coverage. `check_release_policy.py` requires that every declared
`claim_support` outcome is reached by some vector, and a corpus can satisfy that while a rule never
decides anything, because another rule reaches the same outcome first on every vector it would have
caught. Mutation adequacy is the criterion that catches this, and it is well established to
outperform structural criteria such as line and branch coverage for exactly this reason.

**Why the bar here is higher than the usual one.** In ordinary mutation testing the artifact under
test is a test suite, a surviving mutant is a gap in confidence, and a score around 80% is a
reasonable working target. Here the artifact under test is a *published conformance corpus whose
digest is the contract*. A surviving mutant means an implementer can delete that rule, reproduce the
pinned digest, and be indistinguishable from a conforming implementation. That is not a confidence
gap, it is a hole in the contract. So the required score is **100% of non-equivalent mutants**, or
the mutant is declared equivalent with its reason.

**Operators are domain-specific, not generic.** Each mutant removes one *declared rule* rather than
flipping an arbitrary operator, so a surviving mutant names the rule an implementation could omit
instead of naming a line. Generic operators would generate mostly-equivalent noise over rules this
small; the field's direction is domain-specific operators for the same reason.

**An ordinal rule is not omitted, it is re-ordered.** Deletion is the wrong operator for a ladder,
because the ordering lives in a table that a comparison reads rather than in a branch a mutant can
cut, and every deletion mutant for `source_class_ceiling` stayed killed while its ceiling map was
inverted. Ordinal axes therefore also carry permutation mutants: flatten to the top, flatten to the
bottom, invert. `source_class_ceiling` is the only such axis in this corpus today.

**Equivalent mutants are declared, never inferred.** Deciding mutant equivalence is undecidable in
general, so a tool cannot discard them for you and a corpus that silently counts them as failures
teaches its maintainers to ignore the check. `EQUIVALENT` below lists each one with the reason it
cannot be killed, and those are excluded from the denominator exactly as the standard score does.

Two properties this file is built around, both learned from getting them wrong elsewhere:

1. **A no-op edit produces zero differences for the wrong reason** and reads exactly like a passing
   test. Every anchor is asserted present and every mutated source asserted different, and a missing
   anchor is a FAILURE rather than a skip. Rewrite a rule and this breaks loudly instead of quietly
   passing.
2. **A crash is a kill.** Removing a fail-closed guard makes untypeable input raise rather than
   return a verdict. That is reported separately, because "raises without this rule" says more about
   the rule than "moves".
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# axis -> [(rule label, anchor, replacement)]. Each entry deletes exactly one declared rule.
MUTANTS: dict[str, list[tuple[str, str, str]]] = {
    "claim_support": [
        (
            "0 unknown vocabulary fails closed",
            'if observer.get("class") not in _SUBJECT_CONTROLLABLE or kind not in ("occurrence", "absence"):\n        return "invalid"',
            'if False:\n        return "invalid"',
        ),
        (
            "1 undeclared probe set is invalid",
            'if declared is None:\n        if is_absence:\n            return "invalid"',
            'if declared is None:\n        if False:\n            return "invalid"',
        ),
        (
            "2 surface outside the declared set",
            'elif claim.get("surface") not in declared:\n        return "inconclusive_no_coverage"',
            'elif False:\n        return "inconclusive_no_coverage"',
        ),
        (
            "3 reported gap removes absence support",
            'if observation.get("observation_gap") and is_absence:\n        return "inconclusive_no_coverage"',
            'if False:\n        return "inconclusive_no_coverage"',
        ),
        (
            "4 occurrence branch",
            '    if not is_absence:\n        return "supported" if observation.get("saw_event") else "unsupported"',
            '    if False:\n        return "supported" if observation.get("saw_event") else "unsupported"',
        ),
        (
            "5 a seen event contradicts absence",
            'if observation.get("saw_event"):\n        return "contradicted"',
            'if False:\n        return "contradicted"',
        ),
        (
            "6 blinding cost bounds silence",
            'if _SUBJECT_CONTROLLABLE[observer["class"]] and not observer.get("routing_enforced_by"):\n        return "inconclusive_no_coverage"',
            'if False:\n        return "inconclusive_no_coverage"',
        ),
        (
            "6b independently enforced routing escape",
            'if _SUBJECT_CONTROLLABLE[observer["class"]] and not observer.get("routing_enforced_by"):',
            'if _SUBJECT_CONTROLLABLE[observer["class"]]:',
        ),
    ],
    "coverage_honesty": [
        (
            "declared set must be a non-empty list and results a dict",
            'if not isinstance(declared, list) or not declared or not isinstance(results, dict):\n        return "invalid"',
            'if False:\n        return "invalid"',
        ),
        (
            "a missing result reads not_run rather than passing",
            'states = [results.get(case_id, "not_run") for case_id in declared]',
            'states = [results.get(case_id, "passed") for case_id in declared]',
        ),
        (
            "an explicit failure refutes, ahead of confirmation",
            'if any(state == "failed" for state in states):\n        return "refuted"',
            'if False:\n        return "refuted"',
        ),
        (
            "confirmation requires every declared case to pass",
            'if all(state == "passed" for state in states):\n        return "confirmed"',
            'if any(state == "passed" for state in states):\n        return "confirmed"',
        ),
    ],
    "hard_soft_digest": [
        (
            "a missing or mismatched hard digest fails closed",
            'if not _present_string(hs) or not _present_string(hr) or hs != hr:\n        return "rejected_hard"',
            'if False:\n        return "rejected_hard"',
        ),
        (
            "an empty hard digest counts as missing",
            'if not _present_string(hs) or not _present_string(hr) or hs != hr:',
            'if hs is None or hr is None or hs != hr:',
        ),
    ],
    "retained_replay": [
        (
            "carrier validity is a precondition",
            'if not inp.get("carrier_valid"):\n        return "rejected_carrier"',
            'if False:\n        return "rejected_carrier"',
        ),
        (
            "a valid carrier over absent records is incomplete",
            'if not inp.get("records_retained"):\n        return "incomplete"',
            'if False:\n        return "incomplete"',
        ),
    ],
    "delegated_scope": [
        (
            "granted and used must both be lists",
            'if not isinstance(granted, list) or not isinstance(used, list):\n        return "invalid"',
            'if False:\n        return "invalid"',
        ),
        (
            "used must stay within granted",
            'return "within_grant" if set(used) <= set(granted) else "exceeds_grant"',
            'return "within_grant" if True else "exceeds_grant"',
        ),
    ],
    "mcp_description_code": [
        (
            "undeclared effect takes precedence over over-declaration",
            'if code - declared:\n        return "undeclared_effect"',
            'if False:\n        return "undeclared_effect"',
        ),
        (
            "an interface declaring unexercised effects is over_declared",
            'if declared - code:\n        return "over_declared"',
            'if False:\n        return "over_declared"',
        ),
    ],
    "tamper_fail_closed": [
        (
            "a missing digest fails closed",
            'return "accepted" if _present_string(stored) and _present_string(recomputed) and stored == recomputed else "rejected"',
            'return "accepted" if stored == recomputed else "rejected"',
        ),
    ],
    "sufficiency": [
        (
            "sufficiency requires a valid record AND complete coverage",
            '        if inp.get("record_valid") and inp.get("coverage") == "complete"',
            '        if inp.get("record_valid")',
        ),
    ],
    "incomplete_visibility": [
        (
            "only a present observation is observed",
            'return "observed" if inp.get("observation") == "present" else "incomplete"',
            'return "observed" if inp.get("observation") != "not_checked" else "incomplete"',
        ),
    ],
    "source_class_ceiling": [
        (
            "an unknown class or strength is invalid, not a pass",
            'if ceiling is None or strength is None:\n        return "invalid"',
            'if False:\n        return "invalid"',
        ),
        (
            "claim strength must not exceed the origin ceiling",
            'return "within_ceiling" if strength <= ceiling else "exceeds_ceiling"',
            'return "within_ceiling" if True else "exceeds_ceiling"',
        ),
        # The three below permute the ladder instead of deleting a rule. The ordering of the origin
        # classes is a declared rule that lives in a table read by a comparison, not in a branch, so
        # the one-mutant-per-branch habit above generates nothing that can see it: both mutants
        # above stay killed under an inverted ceiling map, and the axis scored 100% while ranking a
        # producer self-report above a receiver receipt. Flattening upward and downward are the two
        # collapses, and inversion is the permutation that keeps three distinct ranks, so a corpus
        # that kills all three pins the order rather than the mere existence of a comparison.
        (
            "the ceiling ladder ranks origin classes, flattened to the highest",
            '_CEILING = {\n    "producer_reported": 1,\n    "issuer_attested": 2,\n    "receiver_receipt": 3,\n}',
            '_CEILING = {\n    "producer_reported": 3,\n    "issuer_attested": 3,\n    "receiver_receipt": 3,\n}',
        ),
        (
            "the ceiling ladder ranks origin classes, flattened to the lowest",
            '_CEILING = {\n    "producer_reported": 1,\n    "issuer_attested": 2,\n    "receiver_receipt": 3,\n}',
            '_CEILING = {\n    "producer_reported": 1,\n    "issuer_attested": 1,\n    "receiver_receipt": 1,\n}',
        ),
        (
            "the ceiling ladder is ordered, not merely three-valued: inverted",
            '_CEILING = {\n    "producer_reported": 1,\n    "issuer_attested": 2,\n    "receiver_receipt": 3,\n}',
            '_CEILING = {\n    "producer_reported": 3,\n    "issuer_attested": 2,\n    "receiver_receipt": 1,\n}',
        ),
    ],
    "format_equivalence": [
        (
            "equivalence is over semantic fields, not the envelope shape",
            '        if _json_semantic_equal(inp.get("a", {}).get("semantic"), inp.get("b", {}).get("semantic"))',
            '        if inp.get("a", {}).get("shape") == inp.get("b", {}).get("shape")',
        ),
    ],
    "recompute": [
        (
            "observed must be a subset of declared",
            'return "match" if set(inp.get("observed", [])) <= set(inp.get("declared", [])) else "mismatch"',
            'return "match" if True else "mismatch"',
        ),
    ],
}

# Mutants that no vector can kill, with the reason. Deciding equivalence is undecidable in general,
# so these are declared rather than inferred, and excluded from the score's denominator.
EQUIVALENT: dict[str, list[tuple[str, str]]] = {
    "claim_support": [
        (
            "order of rules 2 and 3",
            "both return inconclusive_no_coverage, so no vector can distinguish which one fired; "
            "stated in the README as a deliberate boundary rather than found as a gap",
        ),
    ],
}


def _load(source: str, tag: str, tmp: Path):
    path = tmp / f"impl_{tag}.py"
    path.write_text(source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"liveness_{tag}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _outcomes(module, vectors: list[dict]) -> tuple[dict, list[str]]:
    """Return (outcome per vector, ids that raised). A raise is a kill, not a skip."""
    outcomes, raised = {}, []
    for vector in vectors:
        try:
            outcomes[vector["vector_id"]] = module.evaluate(vector["axis"], vector["inputs"])
        except Exception:  # noqa: BLE001 - any raise is a behaviour change, which is the signal
            raised.append(vector["vector_id"])
    return outcomes, raised


def main() -> int:
    source = (ROOT / "ref_example.py").read_text(encoding="utf-8")
    all_vectors = json.loads((ROOT / "vectors.json").read_text(encoding="utf-8"))["vectors"]
    failures: list[str] = []
    killed_total = survived_total = equivalent_total = 0

    # The reach of this check must not narrow silently. An axis that exists in the corpus and
    # declares no mutant is exactly the defect this file exists to catch, one level up.
    corpus_axes = {v["axis"] for v in all_vectors}
    unmutated = sorted(corpus_axes - set(MUTANTS))
    if unmutated:
        failures.append(
            f"axes present in the corpus with no declared mutants: {unmutated}. "
            f"Declare a mutant per rule, or this check silently covers less than its name claims"
        )
    stale = sorted(set(MUTANTS) - corpus_axes)
    if stale:
        failures.append(f"mutants declared for axes not in the corpus: {stale}")

    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        base = _load(source, "base", tmp)

        for axis in sorted(MUTANTS):
            vectors = [v for v in all_vectors if v["axis"] == axis]
            if not vectors:
                failures.append(f"{axis}: no vectors found, so its mutants cannot be scored")
                continue
            baseline, baseline_raised = _outcomes(base, vectors)
            if baseline_raised:
                failures.append(f"{axis}: the unmutated implementation raises on {baseline_raised}")

            killed, survived = [], []
            for index, (label, anchor, replacement) in enumerate(MUTANTS[axis]):
                if anchor not in source:
                    failures.append(f"{axis} / {label!r}: anchor not found in ref_example.py")
                    continue
                mutated = source.replace(anchor, replacement, 1)
                if mutated == source:
                    failures.append(f"{axis} / {label!r}: mutation was a no-op")
                    continue

                outcomes, raised = _outcomes(_load(mutated, f"{axis}_{index}", tmp), vectors)
                moved = [vid for vid, out in baseline.items() if outcomes.get(vid) != out]
                if moved or raised:
                    note = f", {len(raised)} raised" if raised else ""
                    killed.append(f"{label} ({len(moved)} moved{note})")
                else:
                    survived.append(label)
                    failures.append(
                        f"{axis} / {label!r} SURVIVED: no vector kills it, so an implementation "
                        f"omitting this rule reproduces the pinned digest"
                    )

            equivalent = EQUIVALENT.get(axis, [])
            killed_total += len(killed)
            survived_total += len(survived)
            equivalent_total += len(equivalent)
            denom = len(killed) + len(survived)
            score = "n/a" if denom == 0 else f"{100 * len(killed) // denom}%"
            print(f"{axis:22s} killed {len(killed):2d}  survived {len(survived):2d}  "
                  f"equivalent {len(equivalent):2d}  score {score}")
            for line in killed:
                print(f"    killed      {line}")
            for line in survived:
                print(f"    SURVIVED    {line}")
            for label, why in equivalent:
                print(f"    equivalent  {label}: {why}")

    denom = killed_total + survived_total
    score = 0 if denom == 0 else 100 * killed_total // denom
    print()
    print(f"mutation score {score}% over {denom} non-equivalent mutants "
          f"({equivalent_total} declared equivalent and excluded)")

    if failures:
        print("mutation-adequacy check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("mutation-adequacy check passed: every non-equivalent mutant is killed by some vector")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
