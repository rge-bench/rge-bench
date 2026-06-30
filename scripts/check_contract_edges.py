#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Assert language-neutral contract-edge semantics without changing vectors."""

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
