#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Guard: the historical 95-vector v2 digest stays recorded and is not the current one.

Validates the frozen JM-Lab v2 record (digest, checker, report) without requiring the
live corpus to still be v2. Fails if that record is missing or corrupt, or if it is
attached as the current candidate's reproduction. Does not score axes or change vectors.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DIGEST = "sha256:ba0e3795d75c788fa48313ab462493f22d78759851d1b3275d8117051bb22fd0"
CHECKER = "a1f7df862eec4e8480e6c3f3f4f4cec2ec334982"
REPORT = "https://github.com/JM-Lab/rge-bench-java/issues/1#issuecomment-5391653260"
ARTIFACT = f"https://github.com/JM-Lab/rge-bench-java/commit/{CHECKER}"

FORBIDDEN_REPLICATION_RATIONALE = (
    "ACM assumes the author-supplied artifact is the author's",
    "Replicated is not reachable here, and that is a property of conformance corpora",
    "no reproduction can avoid using it",
)


def _folded(text: str) -> str:
    return " ".join(text.split())


def _historical_entry(provenance: dict) -> dict | None:
    prior = provenance.get("prior_external_reproductions")
    if not isinstance(prior, list):
        return None
    matches = [
        entry
        for entry in prior
        if isinstance(entry, dict) and entry.get("scoped_to_digest") == DIGEST
    ]
    return matches[0] if len(matches) == 1 else None


def historical_record_failures(provenance: dict) -> list[str]:
    """Failures about the frozen v2 record. Independent of the live version label."""
    failures: list[str] = []
    historical = _historical_entry(provenance)
    if historical is None:
        failures.append(
            f"prior_external_reproductions must contain exactly one record scoped to {DIGEST}"
        )
        return failures
    if historical.get("checker_commit") != CHECKER:
        failures.append(f"historical v2 checker_commit must be {CHECKER}")
    if historical.get("report") != REPORT:
        failures.append("historical v2 report must pin issuecomment-5391653260")
    if historical.get("artifact") != ARTIFACT:
        failures.append("historical v2 artifact must pin the JM-Lab checker commit URL")
    return failures


def attachment_failures(provenance: dict) -> list[str]:
    """The historical run must not be claimed as the current digest's reproduction."""
    failures: list[str] = []
    current_digest = provenance.get("vectors_digest")
    current = provenance.get("external_reproduction")
    if current_digest == DIGEST:
        failures.append(
            "live vectors_digest is still the historical v2 digest; a new candidate must move it"
        )
    if isinstance(current, dict):
        if current.get("scoped_to_digest") == DIGEST:
            failures.append(
                "historical v2 reproduction is attached as current external_reproduction"
            )
        if current.get("checker_commit") == CHECKER and current_digest != DIGEST:
            failures.append(
                "the v2 checker commit is attached as the current digest's reproduction"
            )
    return failures


def _self_test_boundary_breaks() -> list[str]:
    """Prove both break directions fail this guard, not only the live files."""
    good_historical = {
        "scoped_to_digest": DIGEST,
        "checker_commit": CHECKER,
        "report": REPORT,
        "artifact": ARTIFACT,
    }
    candidate_digest = "sha256:" + ("ab" * 32)
    base = {
        "vectors_digest": candidate_digest,
        "external_reproduction": None,
        "prior_external_reproductions": [good_historical],
    }
    failures: list[str] = []

    missing = copy.deepcopy(base)
    missing["prior_external_reproductions"] = []
    if not historical_record_failures(missing):
        failures.append("self-test: missing historical record must fail the v2 guard")

    corrupt = copy.deepcopy(base)
    corrupt["prior_external_reproductions"][0]["checker_commit"] = "deadbeef"
    if not historical_record_failures(corrupt):
        failures.append("self-test: corrupt historical checker must fail the v2 guard")

    attached = copy.deepcopy(base)
    attached["external_reproduction"] = dict(good_historical)
    if not attachment_failures(attached):
        failures.append("self-test: old reproduction attached to the candidate must fail")

    intact = historical_record_failures(base) + attachment_failures(base)
    if intact:
        failures.append(f"self-test: intact historical record must pass, got {intact}")
    return failures


def main() -> int:
    provenance = json.loads((ROOT / "provenance.json").read_text(encoding="utf-8"))
    reproductions = (ROOT / "REPRODUCTIONS.md").read_text(encoding="utf-8")
    failures: list[str] = []

    failures.extend(historical_record_failures(provenance))
    failures.extend(attachment_failures(provenance))
    failures.extend(_self_test_boundary_breaks())

    if f"historical v2, 95 vectors / 12 axes, `{DIGEST}`" not in reproductions:
        failures.append(
            "REPRODUCTIONS.md must record the historical v2 row (95 vectors / 12 axes) "
            "with the frozen digest"
        )
    if CHECKER not in reproductions or "issuecomment-5391653260" not in reproductions:
        failures.append("REPRODUCTIONS.md must keep the historical v2 checker and report pins")

    folded_reproductions = _folded(reproductions)
    if "not established by these runs" not in folded_reproductions:
        failures.append("REPRODUCTIONS.md must say Replicated is not established by these runs")
    for phrase in FORBIDDEN_REPLICATION_RATIONALE:
        if phrase in folded_reproductions:
            failures.append(f"false Replicated rationale remains: {phrase!r}")

    if failures:
        print("v2 reproduction guard failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("v2 reproduction guard passed: historical record intact, not attached to candidate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
