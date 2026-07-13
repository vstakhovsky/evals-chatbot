#!/usr/bin/env python3
"""
Re-split v2 dataset to proper 50/20/30 distribution with stratification.

Usage:
    python resplit_dataset.py --dry-run    # Show what would change
    python resplit_dataset.py             # Apply changes
"""

import argparse
import json
import sys
import hashlib
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations

def load_cases():
    """Load all cases from seed_cases.jsonl and v2_cases.jsonl."""
    cases = []
    for filepath in ["benchmark/seed_cases.jsonl", "benchmark/v2_cases.jsonl"]:
        p = Path(filepath)
        if not p.exists():
            continue
        with open(p) as f:
            for line in f:
                cases.append(json.loads(line))
    return cases

def get_seed_groups(cases):
    """Group cases by seed_id."""
    groups = defaultdict(list)
    for case in cases:
        seed_id = case.get("seed_id") or case["case_id"]
        groups[seed_id].append(case)
    return groups

def stratify_seeds(seeds, target_ratios):
    """
    Stratified split assignment.

    Args:
        seeds: list of seed dicts with risk_level, difficulty
        target_ratios: {'train': 0.5, 'dev': 0.2, 'test': 0.3}

    Returns:
        dict {seed_id: split}
    """
    # Group seeds by (risk_level, difficulty) for stratification
    strata = defaultdict(list)
    for seed in seeds:
        key = (seed.get("risk_level"), seed.get("difficulty"))
        strata[key].append(seed)

    assignments = {}

    # Assign splits within each stratum
    for stratum_key, stratum_seeds in strata.items():
        n = len(stratum_seeds)

        # Calculate target counts
        n_train = int(n * target_ratios["train"])
        n_dev = int(n * target_ratios["dev"])
        n_test = n - n_train - n_dev  # remainder goes to test

        # Shuffle for randomness (use hash for determinism)
        stratum_seeds_sorted = sorted(stratum_seeds, key=lambda s: hash(s["case_id"]))

        # Assign
        for i, seed in enumerate(stratum_seeds_sorted):
            if i < n_train:
                assignments[seed["seed_id"]] = "train"
            elif i < n_train + n_dev:
                assignments[seed["seed_id"]] = "dev"
            else:
                assignments[seed["seed_id"]] = "test"

    return assignments

def print_crosstab(cases):
    """Print crosstab of split × expected_action × risk_level."""
    print("\n" + "=" * 80)
    print("SPLIT × EXPECTED_ACTION × RISK_LEVEL (counts)")
    print("=" * 80)

    # Aggregate: split -> expected_action -> risk_level -> count
    counts = defaultdict(lambda: defaultdict(Counter))
    for c in cases:
        split = c.get("split", "unknown")
        action = c.get("expected_action", "unknown")
        risk = c.get("risk_level", "unknown")
        counts[split][action][risk] += 1

    for split in ["train", "dev", "test"]:
        print(f"\n{split.upper()}:")
        for action in ["answer", "escalate"]:
            if action in counts[split]:
                risks = counts[split][action]
                total = sum(risks.values())
                print(f"  {action}: {total:3d} total", end=" |")
                for risk in ["low", "critical", "medium"]:
                    count = risks.get(risk, 0)
                    if count > 0:
                        pct = count / total * 100 if total > 0 else 0
                        print(f" {risk}={count:2d}({pct:.0f}%)", end="")
                print()
            else:
                print(f"  {action}: 0 total")

def main():
    parser = argparse.ArgumentParser(description="Re-split dataset to 50/20/30 with stratification")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    args = parser.parse_args()

    # Load data
    cases = load_cases()
    print(f"Loaded {len(cases)} cases")

    # Get unique seeds (use first case of each seed as representative)
    seed_groups = get_seed_groups(cases)
    seeds = []
    for seed_id, group in seed_groups.items():
        # Use seed case (source=human_seed or synthetic_variant with seed_id)
        seed_case = next((c for c in group if c.get("source") == "human_seed"), group[0])
        seeds.append({
            "seed_id": seed_id,
            "case_id": seed_case["case_id"],
            "risk_level": seed_case.get("risk_level", "low"),
            "difficulty": seed_case.get("difficulty", "direct")
        })

    print(f"Found {len(seeds)} unique seeds")

    # Assign splits with stratification
    target_ratios = {"train": 0.5, "dev": 0.2, "test": 0.3}
    assignments = stratify_seeds(seeds, target_ratios)

    # Show target vs actual
    actual_counts = Counter(assignments.values())
    print(f"\nTARGET vs ACTUAL (seed groups):")
    print(f"  Train: target 50%, actual {actual_counts['train']/len(seeds)*100:.1f}%")
    print(f"  Dev:   target 20%, actual {actual_counts['dev']/len(seeds)*100:.1f}%")
    print(f"  Test:  target 30%, actual {actual_counts['test']/len(seeds)*100:.1f}%")

    # Apply assignments to all cases
    updated_cases = []
    changes = 0

    for case in cases:
        seed_id = case.get("seed_id") or case["case_id"]
        old_split = case.get("split", "unknown")
        new_split = assignments.get(seed_id, "train")

        if old_split != new_split:
            changes += 1

        updated_case = case.copy()
        updated_case["split"] = new_split
        updated_cases.append(updated_case)

    print(f"\n{'DRY RUN: ' if args.dry_run else ''}Will change split for {changes} cases")

    # Show crosstab
    print_crosstab(updated_cases)

    if args.dry_run:
        print("\n(Dry run - no files written)")
        return

    # Write back
    seed_cases = [c for c in updated_cases if c.get("source") == "human_seed"]
    variant_cases = [c for c in updated_cases if c.get("source", "").startswith("synthetic_variant")]

    with open("benchmark/seed_cases.jsonl", "w") as f:
        for case in seed_cases:
            f.write(json.dumps(case) + "\n")

    with open("benchmark/v2_cases.jsonl", "w") as f:
        for case in variant_cases:
            f.write(json.dumps(case) + "\n")

    print(f"\n✅ Updated {len(seed_cases)} seeds and {len(variant_cases)} variants")

    # Calculate new test hash
    test_cases = [c["case_id"] for c in updated_cases if c["split"] == "test"]
    test_hash = hash(tuple(sorted(test_cases)))

    print(f"\nNew test_split_hash: {test_hash}")
    print("Update this value in benchmark/README.md")

if __name__ == "__main__":
    main()
