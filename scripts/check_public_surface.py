#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the public kit surface stays neutral and self-contained.

This is intentionally small and repo-local: RGE-Bench should be reproducible without importing a product
implementation, and the public docs should not drift into product attribution or strategy wording.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {".git", ".ruff_cache", "__pycache__", "out"}
TEXT_SUFFIXES = {".md", ".py", ".sh", ".json", ".yml", ".yaml", ".toml", ".txt", ""}

FORBIDDEN_SURFACE = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"\bassay\b",
        r"\bplimsoll\b",
        r"\bproduct whitespace\b",
        r"\bon the map\b",
        r"\bgo[- ]to[- ]market\b",
    ]
]

FORBIDDEN_IMPORTS = [
    re.compile(pattern)
    for pattern in [
        r"^\s*(from|import)\s+assay\b",
        r"^\s*(from|import)\s+plimsoll\b",
    ]
]


def _iter_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if path.suffix not in TEXT_SUFFIXES:
            continue
        files.append(path)
    return files


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []
    for path in _iter_files():
        rel = path.relative_to(ROOT)
        if rel == Path("scripts/check_public_surface.py"):
            continue
        try:
            text = _read(path)
        except UnicodeDecodeError:
            continue

        for line_no, line in enumerate(text.splitlines(), start=1):
            for pattern in FORBIDDEN_IMPORTS:
                if pattern.search(line):
                    failures.append(f"{rel}:{line_no}: forbidden product import: {line.strip()}")
            for pattern in FORBIDDEN_SURFACE:
                if pattern.search(line):
                    failures.append(f"{rel}:{line_no}: forbidden public-surface term: {line.strip()}")

    if failures:
        print("public-surface check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("public-surface check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
