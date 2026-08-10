#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Assert every declared precedence step decides at least one vector.

Outcome coverage is not rule coverage. `check_release_policy.py` already requires that every
declared `claim_support` outcome is reached by some vector, and a corpus can satisfy that while a
step never decides anything, because an earlier step reaches the same outcome first on every vector
it would have caught. A rule nobody has to implement is not a contract, and a rule the corpus cannot
exercise is a rule an implementer can omit and still reproduce the digest.

Method: remove one step from the reference implementation's source, re-import it, and require that
at least one vector moves. A step whose removal changes nothing is not exercised here.

Two properties this file is built around, both learned the hard way:

1. **The mutation must be able to fire.** A no-op edit produces zero differences for the wrong
   reason and reads exactly like a passing test. So every anchor below is asserted present and every
   mutated source is asserted different from the original, and a missing anchor is a FAILURE rather
   than a skip. If the rule is rewritten, this file breaks loudly instead of quietly passing.

2. **A crash is a difference.** Removing the fail-closed vocabulary step makes an unknown observer
   class raise instead of returning `invalid`. That counts as the step being exercised, and is
   reported separately because "crashes without this step" says more than "moves".

## Declared limit

The relative order of steps 2 and 3 is NOT pinnable by this corpus and is not asserted here. Both
return `inconclusive_no_coverage`, so no vector can distinguish which fired. That is stated in the
README as a deliberate boundary rather than discovered as a gap, and `ORDER_UNPINNABLE` below keeps
the statement in code next to the check that would otherwise look incomplete.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (label, anchor, replacement). Each disables exactly one numbered step of `_claim_support`.
STEP_MUTATIONS = [
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
]

# Stated rather than checked, because no vector can decide it. See the module docstring.
ORDER_UNPINNABLE = [
    ("2", "3", "both return inconclusive_no_coverage, so no vector distinguishes which fired"),
]

AXIS = "claim_support"


def _load(source: str, tag: str, tmp: Path):
    path = tmp / f"impl_{tag}.py"
    path.write_text(source, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"liveness_{tag}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _outcomes(module, vectors: list[dict]) -> tuple[dict, list[str]]:
    """Return (outcome per vector, ids that raised). A raise is a difference, not a skip."""
    outcomes, crashed = {}, []
    for vector in vectors:
        try:
            outcomes[vector["vector_id"]] = module.evaluate(vector["axis"], vector["inputs"])
        except Exception:  # noqa: BLE001 - any raise is a behaviour change, and that is the signal
            crashed.append(vector["vector_id"])
    return outcomes, crashed


def main() -> int:
    source = (ROOT / "ref_example.py").read_text(encoding="utf-8")
    vectors = [
        v for v in json.loads((ROOT / "vectors.json").read_text(encoding="utf-8"))["vectors"]
        if v["axis"] == AXIS
    ]
    if not vectors:
        print(f"rule-liveness check failed: no {AXIS} vectors found", file=sys.stderr)
        return 1

    failures: list[str] = []

    with tempfile.TemporaryDirectory() as raw:
        tmp = Path(raw)
        baseline, baseline_crashed = _outcomes(_load(source, "base", tmp), vectors)
        if baseline_crashed:
            failures.append(f"the unmutated implementation raises on {baseline_crashed}")

        for index, (label, anchor, replacement) in enumerate(STEP_MUTATIONS):
            if anchor not in source:
                # Loud, not skipped: an anchor that no longer matches means this file has stopped
                # testing the rule it claims to test.
                failures.append(f"step {label!r}: anchor not found in ref_example.py")
                continue
            mutated = source.replace(anchor, replacement, 1)
            if mutated == source:
                failures.append(f"step {label!r}: mutation was a no-op")
                continue

            outcomes, crashed = _outcomes(_load(mutated, str(index), tmp), vectors)
            moved = [vid for vid, out in baseline.items() if outcomes.get(vid) != out]
            if not moved and not crashed:
                failures.append(
                    f"step {label!r} is not exercised: removing it moves no vector, so an "
                    f"implementation omitting it reproduces this corpus"
                )
            else:
                note = f", {len(crashed)} crash" if crashed else ""
                print(f"  live  {label:44s} {len(moved)} moved{note}")

    for earlier, later, why in ORDER_UNPINNABLE:
        print(f"  n/a   order {earlier} before {later}: not pinnable, {why}")

    if failures:
        print("rule-liveness check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"rule-liveness check passed: {len(STEP_MUTATIONS)} steps, each decides at least one vector")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
