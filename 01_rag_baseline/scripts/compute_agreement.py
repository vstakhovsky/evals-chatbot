#!/usr/bin/env python3
"""
Compute agreement between manual labels and judge verdicts.

Reads:
- benchmark/calibration_sheet.csv (your manual labels)
- benchmark/calibration_key.csv (judge verdicts)

Calculates per-judge:
- Agreement % (exact match)
- Cohen's kappa (inter-rater reliability)
- Disagreement rows (for review)

Usage:
    python scripts/compute_agreement.py
"""

import csv
import sys
from collections import defaultdict

def load_calibration_sheet():
    """Load manual labels."""
    sheet = {}
    with open('benchmark/calibration_sheet.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            case_id = row['case_id']
            sheet[case_id] = row
    return sheet

def load_calibration_key():
    """Load judge verdicts."""
    key = {}
    with open('benchmark/calibration_key.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            case_id = row['case_id']
            key[case_id] = row
    return key

def compute_agreement(manual, judge, judge_col):
    """Compute agreement statistics for one judge."""
    total = 0
    agree = 0
    disagreements = []

    for case_id in manual.keys():
        if case_id not in judge:
            continue

        manual_label = manual[case_id].get(judge_col, '').strip()
        judge_verdict = str(judge[case_id].get(f'{judge_col}_verdict', '')).strip()

        # Skip if manual label is empty
        if not manual_label or manual_label == 'N/A':
            continue

        # Skip if judge verdict is empty
        if not judge_verdict or judge_verdict in ['N/A', '', 'None']:
            continue

        total += 1

        # Normalize boolean strings
        manual_bool = manual_label.lower() in ['true', 'yes', '1', 'correct', 'compliant', 'safe']
        judge_bool = judge_verdict.lower() in ['true', 'yes', '1', 'correct', 'compliant', 'safe']

        if manual_bool == judge_bool:
            agree += 1
        else:
            disagreements.append({
                'case_id': case_id,
                'manual': manual_label,
                'judge': judge_verdict
            })

    if total == 0:
        return None, None, [], 0

    agreement_pct = (agree / total) * 100

    # Calculate Cohen's kappa (simplified - assumes binary classification)
    # Observed agreement
    po = agree / total

    # Expected agreement (by chance)
    manual_positive = sum(1 for v in manual.values() if v.get(judge_col, '').strip().lower() in ['true', 'yes', '1'])
    manual_negative = total - manual_positive

    if manual_positive == 0 or manual_positive == total:
        kappa = "N/A (all same verdict)"
    else:
        judge_positive = sum(1 for v in judge.values() if str(v.get(f'{judge_col}_verdict', '')).strip().lower() in ['true', 'yes', '1'])

        # Expected agreement
        pe = ((manual_positive * judge_positive) + (manual_negative * (total - judge_positive))) / (total * total)

        if pe == 1:
            kappa = "N/A (perfect chance agreement)"
        else:
            kappa = (po - pe) / (1 - pe)
            kappa = round(kappa, 3)

    return agreement_pct, kappa, disagreements, total

def main():
    print("Loading calibration data...")
    manual = load_calibration_sheet()
    judge = load_calibration_key()

    print(f"Manual labels: {len(manual)}")
    print(f"Judge verdicts: {len(judge)}")

    print("\n" + "=" * 80)
    print("JUDGE AGREEMENT ANALYSIS")
    print("=" * 80)

    judges = ['correctness', 'groundedness', 'relevancy', 'not_excessive', 'helpful', 'legal', 'redirects']

    for judge_col in judges:
        agreement_pct, kappa, disagreements, total = compute_agreement(manual, judge, judge_col)

        if agreement_pct is None:
            print(f"\n{judge_col.upper()}:")
            print(f"  No comparable data (manual labels missing or judge verdicts missing)")
            continue

        print(f"\n{judge_col.upper()}:")
        print(f"  Total comparable: {total}")
        print(f"  Agreement: {agreement_pct:.1f}%")
        print(f"  Cohen's kappa: {kappa}")

        if disagreements:
            print(f"  Disagreements: {len(disagreements)}")
            print(f"  Sample disagreements:")
            for d in disagreements[:3]:
                print(f"    {d['case_id']}: manual={d['manual']}, judge={d['judge']}")
        else:
            print(f"  ✅ Perfect agreement!")

    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nRecommendations:")
    print("1. Review disagreement rows to understand judge weaknesses")
    print("2. If agreement < 80%, consider judge prompt refinement")
    print("3. Use Cohen's kappa interpretation:")
    print("   < 0: Poor agreement")
    print("   0-0.20: Slight agreement")
    print("   0.21-0.40: Fair agreement")
    print("   0.41-0.60: Moderate agreement")
    print("   0.61-0.80: Substantial agreement")
    print("   0.81-1.00: Almost perfect agreement")

if __name__ == "__main__":
    main()
