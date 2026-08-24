#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Guard: the current 95-vector digest is v2 and carries the JM-Lab reproduction.

Fails while the public surface still calls this digest v2-candidate or leaves
external_reproduction null. Does not score axes or change vectors.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DIGEST = "sha256:ba0e3795d75c788fa48313ab462493f22d78759851d1b3275d8117051bb22fd0"
CHECKER = "a1f7df862eec4e8480e6c3f3f4f4cec2ec334982"
REPORT = "https://github.com/JM-Lab/rge-bench-java/issues/1#issuecomment-5391653260"
ARTIFACT = f"https://github.com/JM-Lab/rge-bench-java/commit/{CHECKER}"

STALE_PHRASES = [
    "## v2-candidate — no reproduction yet",
    "**Nothing here has been reproduced by anyone but the author.**",
    "**The current 95-vector `v2-candidate` digest does not, and does not inherit v1's.**",
    "**It has no external reproduction.**",
    "No external reproduction. It does not inherit v1's.",
    "**No one has reproduced this digest**",
    "`external_reproduction: null`",
    "which `v2-candidate` narrows",
    "changed in `v2-candidate`",
    "> **Changed in `v2-candidate`.**",
    "`v2-candidate` splits how",
]

REQUIRED_CURRENT_LABELS = [
    ("README.md", "# RGE-Bench external reproduction kit (v2)"),
    ("README.md", "### Two questions, two axes (changed in `v2`)"),
    ("PROFILE-MAPPING.md", "> **Changed in `v2`.**"),
    ("PROFILE-MAPPING.md", "`v2` splits how"),
    ("ADMISSION.md", "Graded against the above at `v2`, 95 vectors"),
]


def main() -> int:
    vectors_doc = json.loads((ROOT / "vectors.json").read_text(encoding="utf-8"))
    provenance = json.loads((ROOT / "provenance.json").read_text(encoding="utf-8"))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    reproductions = (ROOT / "REPRODUCTIONS.md").read_text(encoding="utf-8")
    versioning = (ROOT / "VERSIONING.md").read_text(encoding="utf-8")
    profile_mapping = (ROOT / "PROFILE-MAPPING.md").read_text(encoding="utf-8")
    admission = (ROOT / "ADMISSION.md").read_text(encoding="utf-8")
    failures: list[str] = []

    if provenance.get("vectors_digest") != DIGEST:
        failures.append(f"guard is pinned to {DIGEST}, provenance has {provenance.get('vectors_digest')}")
    if vectors_doc.get("version") != "v2":
        failures.append(f"vectors.json version is {vectors_doc.get('version')!r}, expected 'v2'")
    if provenance.get("version") != "v2":
        failures.append(f"provenance.json version is {provenance.get('version')!r}, expected 'v2'")

    current = provenance.get("external_reproduction")
    if not isinstance(current, dict):
        failures.append("external_reproduction is absent or not an object")
    else:
        if current.get("checker_commit") != CHECKER:
            failures.append(f"external_reproduction.checker_commit must be {CHECKER}")
        if current.get("report") != REPORT:
            failures.append("external_reproduction.report must pin issuecomment-5391653260")
        if current.get("artifact") != ARTIFACT:
            failures.append("external_reproduction.artifact must pin the JM-Lab checker commit URL")
        if current.get("scoped_to_digest") != DIGEST:
            failures.append("external_reproduction.scoped_to_digest must be the current digest")

    if "candidate_reproduction_gate" in provenance:
        failures.append("candidate_reproduction_gate must be removed once this digest is reproduced")

    if "v2-candidate narrows" in json.dumps(provenance, sort_keys=True):
        failures.append("historical reproduction scope still names the current release v2-candidate")

    maturity = provenance.get("maturity", "")
    if "candidate" in maturity.lower() and "no external reproduction" in maturity.lower():
        failures.append(f"stale candidate maturity remains: {maturity!r}")

    surface = readme + "\n" + reproductions + "\n" + versioning + "\n" + profile_mapping + "\n" + admission
    for phrase in STALE_PHRASES:
        if phrase in surface:
            failures.append(f"stale no-reproduction wording remains: {phrase!r}")

    current_surfaces = {
        "README.md": readme,
        "PROFILE-MAPPING.md": profile_mapping,
        "ADMISSION.md": admission,
    }
    for filename, phrase in REQUIRED_CURRENT_LABELS:
        if phrase not in current_surfaces[filename]:
            failures.append(f"{filename} is missing current v2 label: {phrase!r}")

    if "current v2, 95 vectors / 12 axes" not in reproductions:
        failures.append("REPRODUCTIONS.md must record the current v2 row (95 vectors / 12 axes)")

    if failures:
        print("v2 reproduction guard failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("v2 reproduction guard passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
