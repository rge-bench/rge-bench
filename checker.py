#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""RGE-Bench checker (commodity scorer).

Reads the spec-owned vectors and each reference impl's emitted outcomes (out/*.json), and scores each
impl PER AXIS as pass / partial / fail (reproduced / total). It emits a matrix (impls x axes) and the
content-addressed `vectors_digest`. By design it computes NO aggregate / scalar score: a single number
is exactly the reduction the 2026 benchmark critique warns against, and it would re-introduce a
"winner". Reference impls are scored, never blessed.

Run: python3 checker.py
"""

import glob
import hashlib
import json
import os

BENCH = os.path.dirname(os.path.abspath(__file__))


def _canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def load_vectors():
    with open(os.path.join(BENCH, "vectors.json")) as f:
        return json.load(f)


def vectors_digest(doc):
    return "sha256:" + hashlib.sha256(_canonical(doc["vectors"])).hexdigest()


def score(vectors, outcomes_by_impl):
    """Return (matrix, axes). matrix[impl][axis] = {reproduced, total, status}."""
    axes = sorted({v["axis"] for v in vectors})
    by_axis = {ax: [v for v in vectors if v["axis"] == ax] for ax in axes}
    matrix = {}
    for impl, outcomes in sorted(outcomes_by_impl.items()):
        matrix[impl] = {}
        for ax in axes:
            vs = by_axis[ax]
            reproduced = sum(1 for v in vs if outcomes.get(v["vector_id"]) == v["expected"])
            total = len(vs)
            status = "pass" if reproduced == total else ("fail" if reproduced == 0 else "partial")
            matrix[impl][ax] = {"reproduced": reproduced, "total": total, "status": status}
    return matrix, axes


def _read_impl_outputs():
    out = {}
    for path in sorted(glob.glob(os.path.join(BENCH, "out", "*.json"))):
        with open(path) as f:
            doc = json.load(f)
        out[doc["impl"]] = doc["outcomes"]
    return out


def main():
    doc = load_vectors()
    vectors = doc["vectors"]
    outcomes_by_impl = _read_impl_outputs()
    if not outcomes_by_impl:
        print("no impl outputs in out/; run the reference impls first")
        return 1
    matrix, axes = score(vectors, outcomes_by_impl)
    impls = sorted(matrix)

    print(f"RGE-Bench {doc['version']}: per-axis reviewability (NO aggregate score by design)")
    print(f"vectors_digest: {vectors_digest(doc)}")
    print()
    width = max(len(a) for a in axes) + 2
    header = "axis".ljust(width) + "".join(i.ljust(18) for i in impls)
    print(header)
    for ax in axes:
        row = ax.ljust(width)
        for impl in impls:
            cell = matrix[impl][ax]
            row += f"{cell['status']} {cell['reproduced']}/{cell['total']}".ljust(18)
        print(row)
    print()
    # surface the neutrality result explicitly, without inventing a scalar
    not_topping = [i for i in impls if any(matrix[i][a]["status"] != "pass" for a in axes)]
    if not_topping:
        print(
            "Neutrality check: these reference impls do NOT top every axis -> "
            + ", ".join(not_topping)
        )
    print("No single 'winner' score is computed; read the matrix per axis.")

    with open(os.path.join(BENCH, "scores.json"), "w") as f:
        json.dump(
            {"vectors_digest": vectors_digest(doc), "matrix": matrix, "axes": axes},
            f,
            indent=2,
            sort_keys=True,
        )
        f.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
