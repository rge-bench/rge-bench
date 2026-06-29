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

    if failures:
        print("provenance check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(f"provenance check passed: {count} vectors, {len(axes)} axes, {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
