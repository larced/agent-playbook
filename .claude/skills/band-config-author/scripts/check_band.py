#!/usr/bin/env python3
"""Evaluate one metric value against a band config (bands/<metric>.yaml).

Usage: check_band.py <band-file> <value>

Prints JSON describing the highest band the value falls into.
Exit codes: 0 = within all bands, 1 = a band matched, 2 = bad input/config.

Deterministic on purpose: this decides *whether* the model gets invoked and
at which tier; the model never decides that itself. Sustain and cooldown are
the scheduler's responsibility.

Reads YAML if PyYAML is installed, otherwise JSON (YAML is a superset of JSON,
so a band file written as JSON works either way).
"""
import json
import sys

TIER_ORDER = ["log", "diagnose", "propose"]


def load(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    try:
        import yaml  # type: ignore
    except ImportError:
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            fail("PyYAML not installed and file is not JSON; pip install pyyaml")
    return yaml.safe_load(text)


def fail(msg):
    print(json.dumps({"error": msg}))
    sys.exit(2)


def validate(cfg):
    for key in ("metric", "owner", "direction", "bands"):
        if key not in cfg:
            fail(f"missing required key: {key}")
    if cfg["direction"] not in ("higher_is_worse", "lower_is_worse"):
        fail("direction must be higher_is_worse or lower_is_worse")
    bands = cfg["bands"]
    if not isinstance(bands, list) or not bands:
        fail("bands must be a non-empty list")
    for b in bands:
        for key in ("name", "threshold", "tier"):
            if key not in b:
                fail(f"band missing {key}: {b}")
        if b["tier"] not in TIER_ORDER:
            fail(f"band {b['name']}: tier must be one of {TIER_ORDER}")
    # Sort from least to most severe; tiers must not decrease with severity.
    worse_is_higher = cfg["direction"] == "higher_is_worse"
    ordered = sorted(bands, key=lambda b: b["threshold"], reverse=not worse_is_higher)
    ranks = [TIER_ORDER.index(b["tier"]) for b in ordered]
    if ranks != sorted(ranks):
        fail("a more severe band has a lower tier than a less severe one")
    return ordered, worse_is_higher


def main():
    if len(sys.argv) != 3:
        fail("usage: check_band.py <band-file> <value>")
    cfg = load(sys.argv[1])
    try:
        value = float(sys.argv[2])
    except ValueError:
        fail(f"value is not a number: {sys.argv[2]}")
    ordered, worse_is_higher = validate(cfg)

    matched = None
    for b in ordered:
        hit = value >= b["threshold"] if worse_is_higher else value <= b["threshold"]
        if hit:
            matched = b  # keep going: later bands are more severe

    result = {"metric": cfg["metric"], "value": value, "owner": cfg["owner"]}
    if matched is None:
        result.update({"band": None, "tier": None})
        print(json.dumps(result))
        sys.exit(0)
    result.update({
        "band": matched["name"],
        "tier": matched["tier"],
        "sustain": matched.get("sustain"),
        "runbooks": matched.get("runbooks", []),
    })
    print(json.dumps(result))
    sys.exit(1)


if __name__ == "__main__":
    main()
