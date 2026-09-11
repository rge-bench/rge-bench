#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Assert language-neutral contract-edge semantics directly."""

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from ref_example import evaluate  # noqa: E402

_ABSENT = object()


def _controllable_absence(routing=_ABSENT):
    observer = {
        "class": "boundary_observed",
        "declared_probe_set": ["network_connect", "file_open"],
    }
    if routing is not _ABSENT:
        observer["routing_enforced_by"] = routing
    return {
        "claim": {"kind": "absence", "surface": "network_connect"},
        "observer": observer,
        "observation": {"saw_event": False, "observation_gap": False},
    }


def _retained_replay(carrier=_ABSENT):
    # Records retained and replayed == recorded, so a carrier flag read as valid would
    # fall through to replayed_match. Only the carrier flag varies.
    inputs = {"records_retained": True, "replayed": ["read"], "recorded": ["read"]}
    if carrier is not _ABSENT:
        inputs["carrier_valid"] = carrier
    return inputs


CASES = [
    (
        "empty digest is missing",
        "tamper_fail_closed",
        {"stored_digest": "", "recomputed_digest": ""},
        "rejected",
    ),
    (
        "empty hard digest fails hard",
        "hard_soft_digest",
        {"hard_stored": "", "hard_recomputed": "", "soft_a": "x", "soft_b": "x"},
        "rejected_hard",
    ),
    (
        "null granted scope is missing",
        "delegated_scope",
        {"granted": None, "used": ["read"]},
        "invalid",
    ),
    (
        "null used scope is missing",
        "delegated_scope",
        {"granted": ["read"], "used": None},
        "invalid",
    ),
    (
        "numeric semantic equality ignores host boxed type",
        "format_equivalence",
        {"a": {"shape": "json", "semantic": {"n": 1}}, "b": {"shape": "yaml", "semantic": {"n": 1.0}}},
        "equivalent",
    ),
    (
        "object key order is not semantic drift",
        "format_equivalence",
        {
            "a": {"shape": "json", "semantic": {"p": "1", "q": "2"}},
            "b": {"shape": "yaml", "semantic": {"q": "2", "p": "1"}},
        },
        "equivalent",
    ),
    # claim_support: the two ways a probe set can be "not useful" are not the same answer.
    (
        "an explicitly empty probe set is DECLARED and covers nothing",
        "claim_support",
        {
            "claim": {"kind": "absence", "surface": "network_connect"},
            "observer": {"class": "independently_observed", "declared_probe_set": []},
            "observation": {"saw_event": False, "observation_gap": False},
        },
        "inconclusive_no_coverage",
    ),
    (
        "a null probe set is UNDECLARED and makes the absence claim unjudgeable",
        "claim_support",
        {
            "claim": {"kind": "absence", "surface": "network_connect"},
            "observer": {"class": "independently_observed", "declared_probe_set": None},
            "observation": {"saw_event": False, "observation_gap": False},
        },
        "invalid",
    ),
    (
        "a missing observer object is untypeable, not permissive",
        "claim_support",
        {
            "claim": {"kind": "absence", "surface": "network_connect"},
            "observation": {"saw_event": False, "observation_gap": False},
        },
        "invalid",
    ),
    (
        "an absent saw_event flag is not a sighting",
        "claim_support",
        {
            "claim": {"kind": "occurrence", "surface": "network_connect"},
            "observer": {"class": "independently_observed", "declared_probe_set": ["network_connect"]},
            "observation": {},
        },
        "unsupported",
    ),
    (
        "an absent observation_gap flag does not manufacture a gap",
        "claim_support",
        {
            "claim": {"kind": "absence", "surface": "network_connect"},
            "observer": {"class": "independently_observed", "declared_probe_set": ["network_connect"]},
            "observation": {"saw_event": False},
        },
        "supported",
    ),
    # scc.v2-origin-allowlist: both removed v1 origin names stay invalid even at a
    # strength the old five-class ladder would accept.
    (
        "removed origin boundary_observed is invalid at its old within-ceiling strength",
        "source_class_ceiling",
        {"source_class": "boundary_observed", "claim": "observed_in_path"},
        "invalid",
    ),
    (
        "removed origin third_party_observed is invalid at its old within-ceiling strength",
        "source_class_ceiling",
        {"source_class": "third_party_observed", "claim": "independently_confirmed"},
        "invalid",
    ),
    (
        "current origin control producer_reported/asserted stays within_ceiling",
        "source_class_ceiling",
        {"source_class": "producer_reported", "claim": "asserted"},
        "within_ceiling",
    ),
    # claim.empty-set-declared: empty / missing / null are three answers.
    (
        "a missing probe-set key is undeclared on an absence claim",
        "claim_support",
        {
            "claim": {"kind": "absence", "surface": "network_connect"},
            "observer": {"class": "independently_observed"},
            "observation": {"saw_event": False, "observation_gap": False},
        },
        "invalid",
    ),
    # claim.surface-membership-occurrence: membership is decided before the occurrence branch.
    (
        "an uncovered occurrence surface is inconclusive even when an event was seen",
        "claim_support",
        {
            "claim": {"kind": "occurrence", "surface": "io_uring_submit"},
            "observer": {
                "class": "independently_observed",
                "declared_probe_set": ["network_connect", "file_open"],
            },
            "observation": {"saw_event": True, "observation_gap": False},
        },
        "inconclusive_no_coverage",
    ),
    (
        "a covered occurrence stays supported",
        "claim_support",
        {
            "claim": {"kind": "occurrence", "surface": "settlement"},
            "observer": {"class": "receiver_receipt", "declared_probe_set": ["settlement"]},
            "observation": {"saw_event": True, "observation_gap": False},
        },
        "supported",
    ),
    # claim.receiver-receipt-blindable: receiver_receipt is subject-controllable.
    (
        "covered gap-free unseen receiver-receipt absence is inconclusive",
        "claim_support",
        {
            "claim": {"kind": "absence", "surface": "network_connect"},
            "observer": {
                "class": "receiver_receipt",
                "declared_probe_set": ["network_connect", "file_open"],
            },
            "observation": {"saw_event": False, "observation_gap": False},
        },
        "inconclusive_no_coverage",
    ),
    (
        "independent-observer absence control stays supported",
        "claim_support",
        {
            "claim": {"kind": "absence", "surface": "network_connect"},
            "observer": {
                "class": "independently_observed",
                "declared_probe_set": ["network_connect", "file_open"],
            },
            "observation": {"saw_event": False, "observation_gap": False},
        },
        "supported",
    ),
    # claim.empty-routing-absent: _present_string, consulted only at step 6.
    (
        "absent routing is not present for a controllable observer",
        "claim_support",
        _controllable_absence(),
        "inconclusive_no_coverage",
    ),
    (
        "null routing is not present for a controllable observer",
        "claim_support",
        _controllable_absence(None),
        "inconclusive_no_coverage",
    ),
    (
        "empty routing string is not present for a controllable observer",
        "claim_support",
        _controllable_absence(""),
        "inconclusive_no_coverage",
    ),
    (
        "a non-empty routing string is present for a controllable observer",
        "claim_support",
        _controllable_absence("cluster_network_policy_denies_direct_egress"),
        "supported",
    ),
    (
        "whitespace-only routing is a non-empty string and is not trimmed",
        "claim_support",
        _controllable_absence(" "),
        "supported",
    ),
    (
        "a list routing value is invalid only where step 6 consults routing",
        "claim_support",
        _controllable_absence([]),
        "invalid",
    ),
    (
        "a number routing value is invalid only where step 6 consults routing",
        "claim_support",
        _controllable_absence(1),
        "invalid",
    ),
    (
        "malformed routing does not sink a covered occurrence",
        "claim_support",
        {
            "claim": {"kind": "occurrence", "surface": "network_connect"},
            "observer": {
                "class": "boundary_observed",
                "declared_probe_set": ["network_connect"],
                "routing_enforced_by": [],
            },
            "observation": {"saw_event": True, "observation_gap": False},
        },
        "supported",
    ),
    (
        "malformed routing does not sink an already-contradicted absence",
        "claim_support",
        {
            "claim": {"kind": "absence", "surface": "network_connect"},
            "observer": {
                "class": "boundary_observed",
                "declared_probe_set": ["network_connect"],
                "routing_enforced_by": 1,
            },
            "observation": {"saw_event": True, "observation_gap": False},
        },
        "contradicted",
    ),
    (
        "malformed routing does not sink an uncovered surface",
        "claim_support",
        {
            "claim": {"kind": "absence", "surface": "io_uring_submit"},
            "observer": {
                "class": "boundary_observed",
                "declared_probe_set": ["network_connect"],
                "routing_enforced_by": {},
            },
            "observation": {"saw_event": False, "observation_gap": False},
        },
        "inconclusive_no_coverage",
    ),
    (
        "malformed routing does not sink an independent observer",
        "claim_support",
        {
            "claim": {"kind": "absence", "surface": "network_connect"},
            "observer": {
                "class": "independently_observed",
                "declared_probe_set": ["network_connect"],
                "routing_enforced_by": [],
            },
            "observation": {"saw_event": False, "observation_gap": False},
        },
        "supported",
    ),
    # coverage_honesty shape edges no vector forces. Each input is chosen so a vacuous
    # confirmation or a non-object read as an empty map would land on a different outcome.
    (
        "an empty declared case set is invalid, never a vacuous confirmation",
        "coverage_honesty",
        {"declared_cases": [], "case_results": {"c1": "passed"}},
        "invalid",
    ),
    (
        "a missing case_results key is invalid",
        "coverage_honesty",
        {"declared_cases": ["c1"]},
        "invalid",
    ),
    (
        "a null case_results is invalid",
        "coverage_honesty",
        {"declared_cases": ["c1"], "case_results": None},
        "invalid",
    ),
    (
        "an empty case_results array is not an object and is invalid",
        "coverage_honesty",
        {"declared_cases": ["c1"], "case_results": []},
        "invalid",
    ),
    (
        "a case_results array of per-case objects is not an object and is invalid",
        "coverage_honesty",
        {"declared_cases": ["c1"], "case_results": [{"c1": "passed"}]},
        "invalid",
    ),
    (
        "a string case_results is not an object and is invalid",
        "coverage_honesty",
        {"declared_cases": ["c1"], "case_results": "passed"},
        "invalid",
    ),
    (
        "an empty case_results object is present and every declared case reads not run",
        "coverage_honesty",
        {"declared_cases": ["c1", "c2"], "case_results": {}},
        "incomplete",
    ),
    (
        "coverage_honesty control: every declared case passed stays confirmed",
        "coverage_honesty",
        {"declared_cases": ["c1"], "case_results": {"c1": "passed"}},
        "confirmed",
    ),
    # retained_replay: a missing carrier flag is not a valid carrier.
    (
        "an absent carrier_valid flag is missing and rejects the carrier",
        "retained_replay",
        _retained_replay(),
        "rejected_carrier",
    ),
    (
        "a null carrier_valid flag is missing and rejects the carrier",
        "retained_replay",
        _retained_replay(None),
        "rejected_carrier",
    ),
    (
        "a false carrier_valid flag rejects the carrier",
        "retained_replay",
        _retained_replay(False),
        "rejected_carrier",
    ),
    (
        "a rejected carrier is decided before records_retained is consulted",
        "retained_replay",
        {"carrier_valid": False, "records_retained": False, "replayed": [], "recorded": []},
        "rejected_carrier",
    ),
    (
        "retained_replay control: a true carrier_valid flag reaches the replay comparison",
        "retained_replay",
        _retained_replay(True),
        "replayed_match",
    ),
]


def main():
    failures = []
    for name, axis, inputs, expected in CASES:
        actual = evaluate(axis, inputs)
        if actual != expected:
            failures.append(f"{name}: expected {expected}, got {actual}")
    if failures:
        for failure in failures:
            print(f"contract-edge check failed: {failure}", file=sys.stderr)
        raise SystemExit(1)
    print(f"contract-edge check passed: {len(CASES)} probes")


if __name__ == "__main__":
    main()
