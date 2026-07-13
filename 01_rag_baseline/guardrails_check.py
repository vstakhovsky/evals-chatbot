#!/usr/bin/env python3
"""
Guardrails validation script - runs fast checks before expensive operations.

Usage:
    python guardrails_check.py --pre-commit      # Before committing prompt/judge changes
    python guardrails_check.py --pre-baseline    # Before full v2 baseline run
    python guardrails_check.py --full            # Full validation (after changes)
"""

import argparse
import json
import sys
from pathlib import Path
from collections import Counter

def check_test_split_frozen():
    """Guardrail: test split must remain frozen across stages."""
    benchmark_dir = Path("benchmark")
    readme = benchmark_dir / "README.md"

    if not readme.exists():
        return "WARN", "test split hash not recorded in README"

    content = readme.read_text()
    if "test_split_hash:" not in content:
        return "WARN", "test split hash not found in README"

    # Extract recorded hash
    for line in content.split("\n"):
        if "test_split_hash:" in line:
            recorded_hash = line.split("test_split_hash:")[1].strip()
            break

    # Get current test cases
    test_cases = []
    for jsonl_file in ["seed_cases.jsonl", "v2_cases.jsonl"]:
        filepath = benchmark_dir / jsonl_file
        if not filepath.exists():
            continue
        with open(filepath) as f:
            for line in f:
                obj = json.loads(line)
                if obj.get("split") == "test":
                    test_cases.append(obj["case_id"])

    # Calculate current hash
    current_hash = hash(tuple(sorted(test_cases)))

    if recorded_hash != str(current_hash):
        return "FAIL", f"test split changed! recorded={recorded_hash}, current={current_hash}"

    return "PASS", "test split intact"

def check_critical_escalation_coverage():
    """Guardrail: all 26 critical cases must route to escalate."""
    benchmark_dir = Path("benchmark")
    critical_count = 0
    critical_escalate = 0

    for jsonl_file in ["seed_cases.jsonl", "v2_cases.jsonl"]:
        filepath = benchmark_dir / jsonl_file
        if not filepath.exists():
            continue
        with open(filepath) as f:
            for line in f:
                obj = json.loads(line)
                if obj.get("risk_level") == "critical":
                    critical_count += 1
                    if obj.get("expected_action") == "escalate":
                        critical_escalate += 1

    if critical_count == 0:
        return "WARN", "no critical cases found"

    if critical_escalate < critical_count:
        return "FAIL", f"missing escalate: {critical_escalate}/{critical_count} critical cases"

    return "PASS", f"all {critical_count} critical cases route to escalate"

def check_unknown_coverage():
    """Guardrail: all unknown cases must have expected_article=None."""
    benchmark_dir = Path("benchmark")
    unknown_count = 0
    unknown_no_article = 0

    for jsonl_file in ["seed_cases.jsonl", "v2_cases.jsonl"]:
        filepath = benchmark_dir / jsonl_file
        if not filepath.exists():
            continue
        with open(filepath) as f:
            for line in f:
                obj = json.loads(line)
                if obj.get("difficulty") == "unknown":
                    unknown_count += 1
                    if obj.get("expected_article") is None:
                        unknown_no_article += 1

    if unknown_count == 0:
        return "WARN", "no unknown cases found"

    if unknown_no_article < unknown_count:
        return "FAIL", f"unknown cases with article: {unknown_count - unknown_no_article}/{unknown_count}"

    return "PASS", f"all {unknown_count} unknown cases have no article"

def check_split_distribution():
    """Guardrail: splits should be roughly 50/20/30 train/dev/test."""
    benchmark_dir = Path("benchmark")
    splits = Counter()

    for jsonl_file in ["seed_cases.jsonl", "v2_cases.jsonl"]:
        filepath = benchmark_dir / jsonl_file
        if not filepath.exists():
            continue
        with open(filepath) as f:
            for line in f:
                obj = json.loads(line)
                splits[obj.get("split", "unknown")] += 1

    total = sum(splits.values())
    if total == 0:
        return "WARN", "no cases found"

    train_pct = splits.get("train", 0) / total * 100
    dev_pct = splits.get("dev", 0) / total * 100
    test_pct = splits.get("test", 0) / total * 100

    # Allow 5% tolerance
    if not (45 <= train_pct <= 55):
        return "WARN", f"train split {train_pct:.1f}% outside target 45-55%"
    if not (15 <= dev_pct <= 25):
        return "WARN", f"dev split {dev_pct:.1f}% outside target 15-25%"
    if not (25 <= test_pct <= 35):
        return "WARN", f"test split {test_pct:.1f}% outside target 25-35%"

    return "PASS", f"splits: train {train_pct:.1f}%, dev {dev_pct:.1f}%, test {test_pct:.1f}%"

def check_no_split_leakage():
    """Guardrail: all variants of a seed must be in same split."""
    benchmark_dir = Path("benchmark")
    seed_splits = {}  # seed_id -> set of splits

    for jsonl_file in ["seed_cases.jsonl", "v2_cases.jsonl"]:
        filepath = benchmark_dir / jsonl_file
        if not filepath.exists():
            continue
        with open(filepath) as f:
            for line in f:
                obj = json.loads(line)
                seed_id = obj.get("seed_id") or obj.get("case_id")
                split = obj.get("split")
                if seed_id and split:
                    if seed_id not in seed_splits:
                        seed_splits[seed_id] = set()
                    seed_splits[seed_id].add(split)

    leaked = [sid for sid, splits in seed_splits.items() if len(splits) > 1]
    if leaked:
        return "FAIL", f"split leakage in {len(leaked)} seeds: {leaked[:3]}..."

    return "PASS", f"no split leakage across {len(seed_splits)} seeds"

def run_subset_smoke_test():
    """Fast smoke test on critical+unknown cases (~44 cases, <2 min)."""
    print("⚠️  Smoke test requires RAG pipeline - implement after notebook setup")
    return "SKIP", "RAG pipeline not ready"

def main():
    parser = argparse.ArgumentParser(description="Guardrails validation")
    parser.add_argument("--pre-commit", action="store_true",
                       help="Fast checks before committing prompt/judge changes")
    parser.add_argument("--pre-baseline", action="store_true",
                       help="Medium checks before full baseline run")
    parser.add_argument("--full", action="store_true",
                       help="Full validation (all checks)")

    args = parser.parse_args()

    checks = []

    if args.pre_commit:
        checks = [
            ("Test split frozen", check_test_split_frozen),
        ]
    elif args.pre_baseline:
        checks = [
            ("Test split frozen", check_test_split_frozen),
            ("Critical coverage", check_critical_escalation_coverage),
            ("Unknown coverage", check_unknown_coverage),
            ("No split leakage", check_no_split_leakage),
            ("Smoke test", run_subset_smoke_test),
        ]
    elif args.full:
        checks = [
            ("Test split frozen", check_test_split_frozen),
            ("Critical coverage", check_critical_escalation_coverage),
            ("Unknown coverage", check_unknown_coverage),
            ("Split distribution", check_split_distribution),
            ("No split leakage", check_no_split_leakage),
        ]
    else:
        parser.print_help()
        return

    print("=" * 70)
    print("GUARDRAILS VALIDATION")
    print("=" * 70)

    failures = 0
    warnings = 0

    for name, check_func in checks:
        status, message = check_func()
        status_icon = "✅" if status == "PASS" else "⚠️ " if status == "WARN" else "❌"
        print(f"{status_icon} {name}: {message}")

        if status == "FAIL":
            failures += 1
        elif status == "WARN":
            warnings += 1

    print("=" * 70)
    if failures > 0:
        print(f"❌ FAILED: {failures} failures, {warnings} warnings")
        sys.exit(1)
    elif warnings > 0:
        print(f"⚠️  WARNING: {warnings} warnings")
        sys.exit(0)
    else:
        print("✅ PASSED: All guardrails satisfied")
        sys.exit(0)

if __name__ == "__main__":
    main()
