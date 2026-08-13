#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check provenance.json against the live vector set.

Fail-closed: recompute the content-address of the `vectors` array exactly as documented, and assert it
equals the digest, count, and axis list declared in provenance.json. A stale or mis-declared manifest is
a failure, never a soft pass. Imports nothing outside the standard library and the repo-local files.

Run: python3 scripts/check_provenance.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _canonical(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


# The admission modes ADMISSION.md defines. An unknown mode is a failure rather than a pass, because
# the whole point of the field is that a consumer can branch on it without reading prose, and a mode
# this checker does not recognise is one the consumer will not recognise either.
ADMISSION_MODES = ("vendor_owned", "multi_party")

# The rule file this corpus admits under. Pinned by name, not merely content-addressed: an earlier
# version of this check recomputed `rule_digest` over whatever file `rule` named, so pointing it at
# `LICENSE` and declaring LICENSE's digest passed. That satisfies the digest while pinning nothing,
# which is the opposite of what the field is for.
ADMISSION_RULE_FILE = "ADMISSION.md"

ADMISSION_KEYS = frozenset(
    {
        "mode",
        "admitting_parties",
        "signatures_required",
        "rule",
        "rule_digest",
        "may_be_a_conformance_bar",
        "withdrawn",
        "non_claims",
    }
)

WITHDRAWN_KEYS = frozenset({"vector_id", "claimed", "reason", "withdrawn_at_digest"})


def _check_admission(manifest: dict, failures: list[str]) -> None:
    """Assert the admission block is present, internally consistent, and pinned to the rule in force.

    What this establishes and what it does not. It establishes that the declaration does not
    contradict itself or the rule text it names. It does NOT establish that the declaration is true:
    a party can write `multi_party` and list two names that are the same person, and nothing here
    can tell. That is the recomputability-versus-admissibility line ADMISSION.md opens with, applied
    to its own manifest, and it is stated in the file rather than left for a reader to discover.

    `rule_digest` is recomputed over the rule file's raw bytes rather than a canonicalised form: the
    rule is prose, its bytes are what a reader reads, and any normalisation would let the text a
    corpus admitted under drift from the text it published.
    """
    admission = manifest.get("admission")
    if not isinstance(admission, dict):
        failures.append("admission: block missing or not an object")
        return

    # Reject unknown keys before anything else. A misspelled key that silently does nothing is the
    # failure mode this whole block exists to prevent one level up, and `signatures_requred: 99`
    # reading as absent is exactly how a corpus ends up believing it declared something it did not.
    unknown = sorted(set(admission) - ADMISSION_KEYS)
    if unknown:
        failures.append(f"admission: unknown key(s) {unknown}; known keys are {sorted(ADMISSION_KEYS)}")
    missing = sorted(ADMISSION_KEYS - set(admission))
    if missing:
        failures.append(f"admission: missing required key(s) {missing}")

    mode = admission.get("mode")
    if mode not in ADMISSION_MODES:
        failures.append(f"admission.mode: {mode!r} is not one of {ADMISSION_MODES}")

    # `isinstance(True, int)` is True in Python, so a bare int check accepts `signatures_required:
    # true` and prints `signatures_required=True`. Guard the bool explicitly.
    signatures = admission.get("signatures_required")
    if isinstance(signatures, bool) or not isinstance(signatures, int) or signatures < 1:
        failures.append(f"admission.signatures_required: {signatures!r} must be an integer >= 1")
        signatures = None
    elif mode == "vendor_owned" and signatures != 1:
        failures.append(f"admission.mode is vendor_owned but signatures_required is {signatures}")
    elif mode == "multi_party" and signatures < 2:
        failures.append("admission.mode is multi_party but signatures_required is below 2")

    parties = admission.get("admitting_parties")
    if (
        not isinstance(parties, list)
        or not parties
        or any(not isinstance(p, str) or not p.strip() for p in parties)
    ):
        failures.append("admission.admitting_parties: must be a non-empty list of non-empty strings")
    elif signatures is not None and len(parties) < signatures:
        # Declaring more signatures than there are parties who could give one is a corpus claiming a
        # governance state it cannot reach. Cheap to check and it was the whole cost of flipping to
        # `multi_party` before this line existed.
        failures.append(
            f"admission: signatures_required is {signatures} but only {len(parties)} "
            f"admitting part{'y' if len(parties) == 1 else 'ies'} are named"
        )

    # The load-bearing one, and it is keyed on the signature count rather than on `mode`. Keying it on
    # `mode` let a corpus bypass the single MUST NOT in ADMISSION.md by editing one string: set
    # `multi_party` and the bar check stopped applying while nothing else changed. What makes a
    # pass-or-fail bar legitimate is that more than one party admits, so that is what is tested.
    is_bar = admission.get("may_be_a_conformance_bar")
    if not isinstance(is_bar, bool):
        failures.append("admission.may_be_a_conformance_bar: must be a boolean")
    elif is_bar and (signatures is None or signatures < 2):
        failures.append(
            "admission: may_be_a_conformance_bar is true but admission requires fewer than two "
            "signatures; a corpus MUST NOT be another interface's pass-or-fail bar while one party "
            "admits its vectors"
        )

    # `withdrawn` implements ADMISSION.md's "withdrawn, not deleted" rule. An unvalidated list is a
    # place to put a string and call the rule satisfied.
    withdrawn = admission.get("withdrawn")
    if not isinstance(withdrawn, list):
        failures.append("admission.withdrawn: must be a list (empty is fine)")
    else:
        for i, entry in enumerate(withdrawn):
            if not isinstance(entry, dict):
                failures.append(f"admission.withdrawn[{i}]: must be an object")
                continue
            entry_missing = sorted(WITHDRAWN_KEYS - set(entry))
            entry_unknown = sorted(set(entry) - WITHDRAWN_KEYS)
            if entry_missing:
                failures.append(f"admission.withdrawn[{i}]: missing {entry_missing}")
            if entry_unknown:
                failures.append(f"admission.withdrawn[{i}]: unknown key(s) {entry_unknown}")

    non_claims = admission.get("non_claims")
    if not isinstance(non_claims, str) or not non_claims.strip():
        failures.append("admission.non_claims: must be a non-empty string")

    rule_name = admission.get("rule")
    if rule_name != ADMISSION_RULE_FILE:
        failures.append(
            f"admission.rule: {rule_name!r} must be {ADMISSION_RULE_FILE!r}; the digest pins the "
            f"admission rule, and any other file satisfies the digest while pinning nothing"
        )
        return

    rule_path = ROOT / rule_name
    if not rule_path.is_file():
        failures.append(f"admission.rule: {rule_name} does not exist")
        return

    actual = "sha256:" + hashlib.sha256(rule_path.read_bytes()).hexdigest()
    declared = admission.get("rule_digest")
    if declared != actual:
        failures.append(
            f"admission.rule_digest: manifest {declared} != recomputed {actual} "
            f"({rule_name} changed without the manifest moving with it)"
        )


def main() -> int:
    vectors_doc = json.loads((ROOT / "vectors.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "provenance.json").read_text(encoding="utf-8"))

    vectors = vectors_doc["vectors"]
    digest = "sha256:" + hashlib.sha256(_canonical(vectors)).hexdigest()
    count = len(vectors)
    axes = sorted({v["axis"] for v in vectors})

    failures: list[str] = []
    if manifest.get("vectors_digest") != digest:
        failures.append(f"vectors_digest: manifest {manifest.get('vectors_digest')} != recomputed {digest}")
    if manifest.get("vector_count") != count:
        failures.append(f"vector_count: manifest {manifest.get('vector_count')} != actual {count}")
    if manifest.get("axes") != axes:
        failures.append(f"axes: manifest {manifest.get('axes')} != actual {axes}")

    _check_admission(manifest, failures)

    if failures:
        print("provenance check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    admission = manifest["admission"]
    print(f"provenance check passed: {count} vectors, {len(axes)} axes, {digest}")
    print(
        f"admission: mode={admission['mode']} "
        f"signatures_required={admission['signatures_required']} "
        f"may_be_a_conformance_bar={admission['may_be_a_conformance_bar']} "
        f"rule={admission['rule']} @ {admission['rule_digest']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
