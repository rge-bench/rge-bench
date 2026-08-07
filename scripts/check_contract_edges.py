#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Assert language-neutral contract-edge semantics directly."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ref_example import evaluate  # noqa: E402


CASES = [
    (
        "empty digest is missing",
        "tamper_fail_closed",
        {"stored_digest": "", "recomputed_digest": ""},
        "rejected",
    ),
    (
        "empty hard digest fails hard",
        "hard_soft_digest",
        {"hard_stored": "", "hard_recomputed": "", "soft_a": "x", "soft_b": "x"},
        "rejected_hard",
    ),
    (
        "null granted scope is missing",
        "delegated_scope",
        {"granted": None, "used": ["read"]},
        "invalid",
    ),
    (
        "null used scope is missing",
        "delegated_scope",
        {"granted": ["read"], "used": None},
        "invalid",
    ),
    (
        "numeric semantic equality ignores host boxed type",
        "format_equivalence",
        {"a": {"shape": "json", "semantic": {"n": 1}}, "b": {"shape": "yaml", "semantic": {"n": 1.0}}},
        "equivalent",
    ),
    (
        "object key order is not semantic drift",
        "format_equivalence",
        {
            "a": {"shape": "json", "semantic": {"p": "1", "q": "2"}},
            "b": {"shape": "yaml", "semantic": {"q": "2", "p": "1"}},
        },
        "equivalent",
    ),
    # claim_support: the two ways a probe set can be "not useful" are not the same answer.
    (
        "an explicitly empty probe set is DECLARED and covers nothing",
        "claim_support",
        {
            "claim": {"kind": "absence", "surface": "network_connect"},
            "observer": {"class": "independently_observed", "declared_probe_set": []},
            "observation": {"saw_event": False, "observation_gap": False},
        },
        "inconclusive_no_coverage",
    ),
    (
        "a null probe set is UNDECLARED and makes the absence claim unjudgeable",
        "claim_support",
        {
            "claim": {"kind": "absence", "surface": "network_connect"},
            "observer": {"class": "independently_observed", "declared_probe_set": None},
            "observation": {"saw_event": False, "observation_gap": False},
        },
        "invalid",
    ),
    (
        "a missing observer object is untypeable, not permissive",
        "claim_support",
        {
            "claim": {"kind": "absence", "surface": "network_connect"},
            "observation": {"saw_event": False, "observation_gap": False},
        },
        "invalid",
    ),
    (
        "an absent saw_event flag is not a sighting",
        "claim_support",
        {
            "claim": {"kind": "occurrence", "surface": "network_connect"},
            "observer": {"class": "independently_observed", "declared_probe_set": ["network_connect"]},
            "observation": {},
        },
        "unsupported",
    ),
    (
        "an absent observation_gap flag does not manufacture a gap",
        "claim_support",
        {
            "claim": {"kind": "absence", "surface": "network_connect"},
            "observer": {"class": "independently_observed", "declared_probe_set": ["network_connect"]},
            "observation": {"saw_event": False},
        },
        "supported",
    ),
]


def main():
    failures = []
    for name, axis, inputs, expected in CASES:
        actual = evaluate(axis, inputs)
        if actual != expected:
            failures.append(f"{name}: expected {expected}, got {actual}")
    if failures:
        for failure in failures:
            print(f"contract-edge check failed: {failure}", file=sys.stderr)
        raise SystemExit(1)
    print(f"contract-edge check passed: {len(CASES)} probes")


if __name__ == "__main__":
    main()
