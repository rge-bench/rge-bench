#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# RGE-Bench external reproduction kit: example impl -> checker. Self-contained: nothing outside this dir.
set -euo pipefail
cd "$(dirname "$0")"

echo "== example reference impl (clean-room) =="
python3 ref_example.py

echo
echo "== checker (per-axis matrix; NO aggregate score) =="
python3 checker.py
