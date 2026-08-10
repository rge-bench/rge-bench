#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check that the declared release is what it claims to be, not a relabel.

One checker, parameterized by the version `vectors.json` declares, rather than one script per
release. A reproduced release and a candidate release have *inverted* obligations — the first must
carry its reproduction, the second must refuse to claim one — and writing that as two scripts would
be two implementations of one rule.

The v1 policy is kept rather than deleted: it is the record of what "reproduced" was made to mean,
and it still runs if `vectors.json` ever declares v1 again.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from checker import vectors_digest  # noqa: E402
from ref_example import evaluate  # noqa: E402

V1_EDGE_VECTORS = {
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

V2_EDGE_VECTORS = dict(V1_EDGE_VECTORS)
V2_EDGE_VECTORS.update({
    # The step order that a typed reimplementation is most likely to get wrong, pinned where the
    # outcomes actually discriminate between two steps.
    "cs.edge_undeclared_probe_set_precedes_uncovered_surface": ("claim_support", "invalid"),
    "cs.edge_probe_set_precedes_contradiction": ("claim_support", "inconclusive_no_coverage"),
    "cs.edge_contradiction_precedes_blinding_cost": ("claim_support", "contradicted"),
    "cs.edge_unknown_observer_class_is_invalid": ("claim_support", "invalid"),
    "cs.edge_unknown_claim_kind_is_invalid": ("claim_support", "invalid"),
})

CLAIM_SUPPORT_OUTCOMES = {
    "supported", "unsupported", "contradicted", "inconclusive_no_coverage", "invalid",
}

POLICIES = {
    "v1": {
        "vector_count": 71,
        "reproduced": True,
        "maturity": "digest-scoped externally reproduced",
        "edge_vectors": V1_EDGE_VECTORS,
        "reproduction_commit": "cd788eb9453eb8f13c4d910d968b0776b25e7f76",
        # A reproduced release must not hedge in its public docs.
        "forbidden_doc_phrases": [
            "v1-candidate", "v1 candidate digest", "not reproduced yet",
            "awaiting external reproduction", "not v1 conformance",
        ],
        "required_doc_phrases": [],
        "required_reproductions_phrase": "current v1, 71 vectors / 11 axes",
    },
    "v2-candidate": {
        "vector_count": 92,
        "reproduced": False,
        "maturity_prefix": "candidate",
        "edge_vectors": V2_EDGE_VECTORS,
        # A candidate release must not borrow the previous digest's badge, and must say so where a
        # reader will see it rather than only in the changelog.
        "forbidden_doc_phrases": [
            "the current v2-candidate digest has one reported independent reproduction",
            "v2-candidate conformance",
        ],
        "required_doc_phrases": [
            "**The current 92-vector `v2-candidate` digest does not, and does not inherit v1's.**",
        ],
        "required_reproductions_phrase": "## v2-candidate — no reproduction yet",
    },
}


def _read_json(name: str) -> dict:
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def _check_reproduction_fields(policy: dict, provenance: dict, failures: list[str]) -> None:
    current = provenance.get("external_reproduction")

    if policy["reproduced"]:
        if not isinstance(current, dict):
            failures.append("a reproduced release must carry external_reproduction")
        else:
            commit = policy["reproduction_commit"]
            if current.get("checker_commit") != commit:
                failures.append(f"external_reproduction checker_commit must pin {commit[:12]}...")
            if current.get("artifact") != f"https://github.com/JM-Lab/rge-bench-java/commit/{commit}":
                failures.append("external_reproduction artifact must pin the JM-Lab checker commit URL")
        if "candidate_reproduction_gate" in provenance:
            failures.append("candidate_reproduction_gate must be removed once the digest is reproduced")
        return

    # Candidate: the obligations invert.
    if current is not None:
        failures.append(
            "a candidate release must not claim an external_reproduction; the previous digest's "
            "reproduction belongs in prior_external_reproductions"
        )
    gate = provenance.get("candidate_reproduction_gate")
    if not isinstance(gate, str) or not gate.strip():
        failures.append("a candidate release must state its candidate_reproduction_gate")
    prior = provenance.get("prior_external_reproductions")
    if not isinstance(prior, list) or not prior:
        failures.append("provenance must retain prior_external_reproductions")
    elif not any(entry.get("scoped_to_digest") for entry in prior if isinstance(entry, dict)):
        failures.append(
            "the inherited reproduction must record scoped_to_digest, so it cannot be read as "
            "covering the current digest"
        )


def main() -> int:
    vectors_doc = _read_json("vectors.json")
    provenance = _read_json("provenance.json")
    vectors = vectors_doc["vectors"]
    by_id = {vector["vector_id"]: vector for vector in vectors}
    failures: list[str] = []

    declared = vectors_doc.get("version")
    policy = POLICIES.get(declared)
    if policy is None:
        print(f"release policy check failed: no policy for declared version {declared!r}", file=sys.stderr)
        return 1

    if provenance.get("version") != declared:
        failures.append(f"provenance.json version is {provenance.get('version')!r}, expected {declared!r}")
    if len(vectors) != policy["vector_count"]:
        failures.append(f"vector count is {len(vectors)}, expected {policy['vector_count']}")
    if provenance.get("vector_count") != policy["vector_count"]:
        failures.append(f"provenance vector_count is {provenance.get('vector_count')}, expected {policy['vector_count']}")
    if provenance.get("vectors_digest") != vectors_digest(vectors_doc):
        failures.append(f"provenance vectors_digest does not match the {declared} vector set")

    maturity = provenance.get("maturity", "")
    if "maturity" in policy and maturity != policy["maturity"]:
        failures.append(f"maturity is {maturity!r}, expected {policy['maturity']!r}")
    if "maturity_prefix" in policy and not maturity.startswith(policy["maturity_prefix"]):
        failures.append(f"maturity is {maturity!r}, expected it to start with {policy['maturity_prefix']!r}")

    _check_reproduction_fields(policy, provenance, failures)

    for vector_id, (axis, expected) in policy["edge_vectors"].items():
        vector = by_id.get(vector_id)
        if vector is None:
            failures.append(f"missing {declared} edge vector {vector_id}")
            continue
        if vector.get("axis") != axis:
            failures.append(f"{vector_id} axis is {vector.get('axis')!r}, expected {axis!r}")
        if vector.get("expected") != expected:
            failures.append(f"{vector_id} expected is {vector.get('expected')!r}, expected {expected!r}")
        actual = evaluate(vector["axis"], vector.get("inputs", {}))
        if actual != expected:
            failures.append(f"{vector_id} ref_example evaluates to {actual!r}, expected {expected!r}")

    # An axis whose corpus does not exercise its whole declared outcome vocabulary is a vocabulary
    # nobody has to implement. Only enforced where the axis exists.
    claim_support = {v["expected"] for v in vectors if v["axis"] == "claim_support"}
    if claim_support and claim_support != CLAIM_SUPPORT_OUTCOMES:
        missing = CLAIM_SUPPORT_OUTCOMES - claim_support
        extra = claim_support - CLAIM_SUPPORT_OUTCOMES
        if missing:
            failures.append(f"claim_support outcomes never exercised by any vector: {sorted(missing)}")
        if extra:
            failures.append(f"claim_support vectors expect undeclared outcomes: {sorted(extra)}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    reproductions = (ROOT / "REPRODUCTIONS.md").read_text(encoding="utf-8")
    for phrase in policy["forbidden_doc_phrases"]:
        if phrase in readme or phrase in reproductions:
            failures.append(f"phrase forbidden for {declared} still appears in public docs: {phrase!r}")
    for phrase in policy["required_doc_phrases"]:
        if phrase not in readme:
            failures.append(f"README.md must state, verbatim: {phrase!r}")
    if "## Version and stability policy" not in readme:
        failures.append("README.md must include Version and stability policy")
    if policy["required_reproductions_phrase"] not in reproductions:
        failures.append(f"REPRODUCTIONS.md must record: {policy['required_reproductions_phrase']!r}")

    if failures:
        print(f"{declared} release policy check failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"{declared} release policy check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
