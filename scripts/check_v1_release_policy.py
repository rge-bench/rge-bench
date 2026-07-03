#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check that v1 is a reproduced contract-surface release, not a relabel."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from checker import vectors_digest  # noqa: E402
from ref_example import evaluate  # noqa: E402

EXPECTED_VERSION = "v1"
EXPECTED_VECTOR_COUNT = 71
EXPECTED_EDGE_VECTORS = {
    "tmp.edge_empty_digest_rejected": ("tamper_fail_closed", "rejected"),
    "hsd.edge_empty_hard_rejected": ("hard_soft_digest", "rejected_hard"),
    "dsc.edge_null_granted_invalid": ("delegated_scope", "invalid"),
    "dsc.edge_null_used_invalid": ("delegated_scope", "invalid"),
    "dsc.edge_non_array_granted_invalid": ("delegated_scope", "invalid"),
    "cov.edge_non_array_declared_cases_invalid": ("coverage_honesty", "invalid"),
    "fmt.edge_numeric_semantic_equivalent": ("format_equivalence", "equivalent"),
    "fmt.edge_object_key_order_equivalent": ("format_equivalence", "equivalent"),
    "fmt.edge_array_order_distinct": ("format_equivalence", "distinct"),
}


def _read_json(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def main() -> int:
    vectors_doc = _read_json("vectors.json")
    provenance = _read_json("provenance.json")
    vectors = vectors_doc["vectors"]
    by_id = {vector["vector_id"]: vector for vector in vectors}

    failures: list[str] = []

    if vectors_doc.get("version") != EXPECTED_VERSION:
        failures.append(f"vectors.json version is {vectors_doc.get('version')!r}, expected {EXPECTED_VERSION!r}")
    if provenance.get("version") != EXPECTED_VERSION:
        failures.append(f"provenance.json version is {provenance.get('version')!r}, expected {EXPECTED_VERSION!r}")
    if len(vectors) != EXPECTED_VECTOR_COUNT:
        failures.append(f"vector count is {len(vectors)}, expected {EXPECTED_VECTOR_COUNT}")
    if provenance.get("vector_count") != EXPECTED_VECTOR_COUNT:
        failures.append(f"provenance vector_count is {provenance.get('vector_count')}, expected {EXPECTED_VECTOR_COUNT}")
    if provenance.get("vectors_digest") != vectors_digest(vectors_doc):
        failures.append("provenance vectors_digest does not match the v1 vector set")

    maturity = provenance.get("maturity", "")
    if maturity != "digest-scoped externally reproduced":
        failures.append(f"maturity is {maturity!r}, expected 'digest-scoped externally reproduced'")
    current_reproduction = provenance.get("external_reproduction")
    if not isinstance(current_reproduction, dict):
        failures.append("provenance must carry the v1 reproduction as external_reproduction")
    else:
        expected_commit = "https://github.com/JM-Lab/rge-bench-java/commit/cd788eb9453eb8f13c4d910d968b0776b25e7f76"
        if current_reproduction.get("checker_commit") != "cd788eb9453eb8f13c4d910d968b0776b25e7f76":
            failures.append("external_reproduction checker_commit must pin JM-Lab commit cd788eb9453e...")
        if current_reproduction.get("artifact") != expected_commit:
            failures.append("external_reproduction artifact must pin the JM-Lab checker commit URL")
    if "prior_external_reproductions" not in provenance:
        failures.append("provenance must retain prior_external_reproductions for v0 digests")
    if "candidate_reproduction_gate" in provenance:
        failures.append("candidate_reproduction_gate must be removed after v1 digest reproduction")

    for vector_id, (axis, expected) in EXPECTED_EDGE_VECTORS.items():
        vector = by_id.get(vector_id)
        if vector is None:
            failures.append(f"missing v1 edge vector {vector_id}")
            continue
        if vector.get("axis") != axis:
            failures.append(f"{vector_id} axis is {vector.get('axis')!r}, expected {axis!r}")
        if vector.get("expected") != expected:
            failures.append(f"{vector_id} expected is {vector.get('expected')!r}, expected {expected!r}")
        actual = evaluate(vector["axis"], vector.get("inputs", {}))
        if actual != expected:
            failures.append(f"{vector_id} ref_example evaluates to {actual!r}, expected {expected!r}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    reproductions = (ROOT / "REPRODUCTIONS.md").read_text(encoding="utf-8")
    forbidden_candidate_phrases = [
        "v1-candidate",
        "v1 candidate digest",
        "not reproduced yet",
        "awaiting external reproduction",
        "not v1 conformance",
    ]
    for phrase in forbidden_candidate_phrases:
        if phrase in readme or phrase in reproductions:
            failures.append(f"candidate-only phrase still appears in public docs: {phrase!r}")
    if "## Version and stability policy" not in readme:
        failures.append("README.md must include Version and stability policy")
    if "current v1, 71 vectors / 11 axes" not in reproductions:
        failures.append("REPRODUCTIONS.md must record the current v1 reproduction")

    if failures:
        print("v1 release policy check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"v1 release policy check passed: {EXPECTED_VECTOR_COUNT} vectors, {len(EXPECTED_EDGE_VECTORS)} edge vectors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
