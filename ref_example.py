#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""RGE-Bench external-repro kit: EXAMPLE reference implementation (clean-room).

Imports nothing from the bench or any producer (no RGE-Bench code, no external libraries). It recomputes
an outcome for every vector from `inputs` alone (never reading `expected`), then writes
out/ref_example.json. It implements each axis rule directly, as a worked example for anyone writing their
own conforming implementation. To produce an INDEPENDENT reproduction, write your own program to the
README contract (do not transliterate this one) and emit out/<your_impl>.json.

Run: python3 ref_example.py
"""

import json
import os

KIT = os.path.dirname(os.path.abspath(__file__))

# source-class ceiling ranks (RGE-Bench's proposed ordering; see README, anchor 2606.04193)
_CEILING = {
    "producer_reported": 1,
    "issuer_attested": 2,
    "receiver_receipt": 3,
    "boundary_observed": 4,
    "third_party_observed": 5,
}
_STRENGTH = {
    "asserted": 1,
    "asserted_signed": 2,
    "observed_at_receiver": 3,
    "observed_in_path": 4,
    "independently_confirmed": 5,
}


def _sufficiency(inp):
    return (
        "sufficient"
        if inp.get("record_valid") and inp.get("coverage") == "complete"
        else "incomplete"
    )


def _source_class_ceiling(inp):
    ceiling = _CEILING.get(inp.get("source_class"))
    strength = _STRENGTH.get(inp.get("claim"))
    if ceiling is None or strength is None:
        return "invalid"
    return "within_ceiling" if strength <= ceiling else "exceeds_ceiling"


def _recompute(inp):
    # prose is not read; the verdict is recomputed from declared vs observed effects only
    return "match" if set(inp.get("observed", [])) <= set(inp.get("declared", [])) else "mismatch"


def _format_equivalence(inp):
    # envelope shape is metadata; equivalence is over semantic fields, normalized across shapes
    return "equivalent" if inp["a"].get("semantic") == inp["b"].get("semantic") else "distinct"


def _tamper_fail_closed(inp):
    stored, recomputed = inp.get("stored_digest"), inp.get("recomputed_digest")
    return "accepted" if stored and recomputed and stored == recomputed else "rejected"


def _incomplete_visibility(inp):
    return "observed" if inp.get("observation") == "present" else "incomplete"


AXES = {
    "sufficiency": _sufficiency,
    "source_class_ceiling": _source_class_ceiling,
    "recompute": _recompute,
    "format_equivalence": _format_equivalence,
    "tamper_fail_closed": _tamper_fail_closed,
    "incomplete_visibility": _incomplete_visibility,
}


def evaluate(axis, inputs):
    fn = AXES.get(axis)
    return fn(inputs) if fn else "unsupported"


def main():
    with open(os.path.join(KIT, "vectors.json")) as f:
        vectors = json.load(f)["vectors"]
    outcomes = {v["vector_id"]: evaluate(v["axis"], v["inputs"]) for v in vectors}
    os.makedirs(os.path.join(KIT, "out"), exist_ok=True)
    with open(os.path.join(KIT, "out", "ref_example.json"), "w") as f:
        json.dump({"impl": "ref_example", "outcomes": outcomes}, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"ref_example: {len(outcomes)} vectors -> out/ref_example.json")


if __name__ == "__main__":
    main()
