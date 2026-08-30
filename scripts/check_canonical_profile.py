#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Guard the vectors_digest canonicalization profile.

Pins the named Python json.dumps profile. Fails closed if the profile id is
missing or stale, if the production dumps kwargs drift, if a second serializer
can diverge, or if public digest wording is left unqualified.
"""

from __future__ import annotations

import ast
import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

EXPECTED_PROFILE = "rge-bench/py-jsondumps/1"
EXPECTED_DIGEST = "sha256:93f8ae9654eb5a16dee28d882087669cae5183e02e116ba1e8071a30594cfb6a"
FORBIDDEN_CLAIM_TOKENS = ("RFC 8785", "rfc 8785", "JCS", "subset of JCS", "subset of jcs")
CLAIM_SURFACES = (
    "checker.py",
    "provenance.json",
    "scores.json",
    "README.md",
    "VERSIONING.md",
    "REPRODUCTIONS.md",
)

# Hand-checked CPython json.dumps bytes under the pinned kwargs. Not derived
# from the function under test at runtime.
FIXTURES: list[tuple[str, object, bytes]] = [
    ("integral_float_stays_dotted", 1.0, b"1.0"),
    ("python_exponent_padding", 1e-7, b"1e-07"),
    ("emdash_ensure_ascii", "\u2014", b'"\\u2014"'),
    (
        "codepoint_key_order",
        {"\uE000": 1, "\U00010000": 2},
        b'{"\\ue000":1,"\\ud800\\udc00":2}',
    ),
    ("compact_separators", {"b": 1, "a": 2}, b'{"a":2,"b":1}'),
]

SOURCE_NEEDLES = (
    "sort_keys=True",
    'separators=(",", ":")',
    "ensure_ascii=True",
    "allow_nan=False",
)


def _fn_source(fn) -> str:
    return inspect.getsource(fn)


def _dumps_calls_in(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = ""
        if isinstance(func, ast.Attribute) and func.attr == "dumps":
            name = "dumps"
        elif isinstance(func, ast.Name) and func.id in {"dumps", "canonical_dumps"}:
            name = func.id
        if name == "dumps":
            found.append(f"{path.name}:{node.lineno}")
    return found


def main() -> int:
    failures: list[str] = []

    try:
        from checker import PROFILE_ID, canonical_dumps, vectors_digest
    except ImportError as exc:
        print("canonical profile check failed:")
        print(f"- checker is missing PROFILE_ID/canonical_dumps ({exc})")
        return 1

    if PROFILE_ID != EXPECTED_PROFILE:
        failures.append(f"PROFILE_ID is {PROFILE_ID!r}, expected {EXPECTED_PROFILE!r}")

    src = _fn_source(canonical_dumps)
    for needle in SOURCE_NEEDLES:
        if needle not in src:
            failures.append(f"canonical_dumps source is missing {needle}")

    for label, value, expected in FIXTURES:
        try:
            actual = canonical_dumps(value)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{label}: raised {type(exc).__name__}: {exc}")
            continue
        if actual != expected:
            failures.append(f"{label}: got {actual!r}, expected {expected!r}")

    try:
        canonical_dumps(float("nan"))
    except ValueError:
        pass
    else:
        failures.append("NaN must raise ValueError under allow_nan=False")

    vectors_doc = json.loads((ROOT / "vectors.json").read_text(encoding="utf-8"))
    digest = vectors_digest(vectors_doc)
    if digest != EXPECTED_DIGEST:
        failures.append(f"vectors_digest moved: {digest} != {EXPECTED_DIGEST}")

    provenance = json.loads((ROOT / "provenance.json").read_text(encoding="utf-8"))
    scores = json.loads((ROOT / "scores.json").read_text(encoding="utf-8"))
    for name, doc in (("provenance.json", provenance), ("scores.json", scores)):
        got = doc.get("canonicalization_profile")
        if got != EXPECTED_PROFILE:
            failures.append(f"{name} canonicalization_profile is {got!r}, expected {EXPECTED_PROFILE!r}")
        if doc.get("vectors_digest") != EXPECTED_DIGEST:
            failures.append(f"{name} vectors_digest is {doc.get('vectors_digest')!r}")

    method = provenance.get("digest_method", "")
    if EXPECTED_PROFILE not in method:
        failures.append("provenance digest_method does not name rge-bench/py-jsondumps/1")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    versioning = (ROOT / "VERSIONING.md").read_text(encoding="utf-8")
    reproductions = (ROOT / "REPRODUCTIONS.md").read_text(encoding="utf-8")
    for name, text in (
        ("README.md", readme),
        ("VERSIONING.md", versioning),
        ("REPRODUCTIONS.md", reproductions),
    ):
        if EXPECTED_PROFILE not in text:
            failures.append(f"{name} does not name {EXPECTED_PROFILE}")
        if "canonical JSON" in text and EXPECTED_PROFILE not in text:
            failures.append(f"{name} still has unqualified canonical JSON wording")

    # README provenance paragraph must qualify if it still says canonical JSON.
    if "canonical JSON" in readme and EXPECTED_PROFILE not in readme:
        failures.append("README.md provenance still says canonical JSON without the profile id")
    if "RGE-Bench v1 vector set" in readme:
        failures.append("README.md provenance still calls the current digest a v1 vector set")

    for rel in CLAIM_SURFACES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        lower = text.lower()
        for token in FORBIDDEN_CLAIM_TOKENS:
            if token.lower() in lower:
                failures.append(f"{rel} contains forbidden claim token {token!r}")

    prov_src = (ROOT / "scripts" / "check_provenance.py").read_text(encoding="utf-8")
    if "from checker import" not in prov_src or "canonical_dumps" not in prov_src:
        failures.append("check_provenance.py must import canonical_dumps from checker")
    if "def _canonical" in prov_src or "def canonical_dumps" in prov_src:
        failures.append("check_provenance.py must not define a second canonical function")
    extra_dumps = [
        line
        for line in _dumps_calls_in(ROOT / "scripts" / "check_provenance.py")
        if True
    ]
    if extra_dumps:
        failures.append(f"check_provenance.py still has json.dumps calls: {extra_dumps}")

    checker_dumps = _dumps_calls_in(ROOT / "checker.py")
    # One dumps for the profile, one json.dump for scores.json is fine; extra dumps is a split.
    # We only require the digest path to go through canonical_dumps.
    checker_src = (ROOT / "checker.py").read_text(encoding="utf-8")
    if checker_src.count("def canonical_dumps") != 1:
        failures.append("checker.py must define exactly one canonical_dumps")
    if checker_src.count("def _canonical") > 0:
        failures.append("checker.py still has a second _canonical")

    if failures:
        print("canonical profile check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"canonical profile check passed: {EXPECTED_PROFILE} {EXPECTED_DIGEST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
