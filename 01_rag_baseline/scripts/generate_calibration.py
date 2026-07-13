#!/usr/bin/env python3
"""
Generate judge calibration sheet from v2 baseline results.

Samples 50 rows stratified by (expected_action, risk_level, any_judge_failed):
- ~20 escalate (incl. ≥10 critical)
- ~30 answer
- Half passing / half failing within each group

Creates:
- benchmark/calibration_sheet.csv (for manual labeling)
- benchmark/calibration_key.csv (judge verdicts key)
"""

import json
import random
import csv
from collections import defaultdict

def load_baseline_results():
    """Load v2 baseline results."""
    results = []
    with open('benchmark/v2_baseline_results.jsonl') as f:
        for line in f:
            results.append(json.loads(line))
    return results

def determine_judge_status(case):
    """Check if any judge failed for this case."""
    # Check primary judges
    correctness = case.get('correctness', {})
    if isinstance(correctness, dict) and not correctness.get('correct', True):
        return 'failed'

    groundedness = case.get('groundedness', {})
    if isinstance(groundedness, dict) and not groundedness.get('grounded', True):
        return 'failed'

    # Check secondary judges if present
    safety = case.get('safety', {})
    if isinstance(safety, dict) and not safety.get('safe', True):
        return 'failed'

    return 'passed'

def stratify_sample(results, n=50):
    """
    Stratified sample of 50 rows.

    Strata: (expected_action, risk_level, judge_status)
    Target: ~20 escalate (≥10 critical) + ~30 answer
    """
    # Group into strata
    strata = defaultdict(list)
    for case in results:
        key = (
            case.get('expected_action', 'unknown'),
            case.get('risk_level', 'unknown'),
            determine_judge_status(case)
        )
        strata[key].append(case)

    sample = []

    # First, select escalate cases (target ~20, ≥10 critical)
    escalate_cases = [c for c in results if c.get('expected_action') == 'escalate']
    critical_escalate = [c for c in escalate_cases if c.get('risk_level') == 'critical']
    non_critical_escalate = [c for c in escalate_cases if c.get('risk_level') != 'critical']

    # Sample ~10 critical escalate
    critical_escalate_passed = [c for c in critical_escalate if determine_judge_status(c) == 'passed']
    critical_escalate_failed = [c for c in critical_escalate if determine_judge_status(c) == 'failed']

    critical_sample = []
    if len(critical_escalate_passed) >= 5:
        critical_sample.extend(random.sample(critical_escalate_passed, 5))
    if len(critical_escalate_failed) >= 5:
        critical_sample.extend(random.sample(critical_escalate_failed, 5))

    # Sample ~10 more escalate (mix of critical + non-critical, half passing/failing)
    remaining_escalate = [c for c in escalate_cases if c not in critical_sample]
    escalate_passed = [c for c in remaining_escalate if determine_judge_status(c) == 'passed']
    escalate_failed = [c for c in remaining_escalate if determine_judge_status(c) == 'failed']

    if len(escalate_passed) >= 5:
        critical_sample.extend(random.sample(escalate_passed, 5))
    if len(escalate_failed) >= 5:
        critical_sample.extend(random.sample(escalate_failed, 5))

    # Fill to ~20 escalate
    while len(critical_sample) < 20 and remaining_escalate:
        if remaining_escalate:
            critical_sample.append(remaining_escalate.pop())
        else:
            break

    sample.extend(critical_sample[:20])

    # Now sample answer cases (target ~30, half passing/failing)
    answer_cases = [c for c in results if c.get('expected_action') == 'answer']
    answer_passed = [c for c in answer_cases if determine_judge_status(c) == 'passed']
    answer_failed = [c for c in answer_cases if determine_judge_status(c) == 'failed']

    # Sample ~15 passing answer
    if len(answer_passed) >= 15:
        sample.extend(random.sample(answer_passed, 15))
    elif len(answer_passed) > 0:
        sample.extend(answer_passed)

    # Sample ~15 failing answer
    if len(answer_failed) >= 15:
        sample.extend(random.sample(answer_failed, 15))
    elif len(answer_failed) > 0:
        sample.extend(answer_failed)

    # Fill to 50 if needed
    remaining = [c for c in results if c not in sample]
    while len(sample) < 50 and remaining:
        sample.append(remaining.pop())

    return sample[:50]

def create_calibration_sheet(sample, output_path):
    """Create calibration sheet CSV for manual labeling."""
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'case_id',
            'query',
            'answer',
            'extracted_context',
            'my_correctness',
            'my_groundedness',
            'my_relevancy',
            'my_not_excessive',
            'my_helpful',
            'my_legal',
            'my_redirects',
            'my_notes'
        ])

        for case in sample:
            # Build context string
            context_parts = []
            if 'retrieved_articles' in case:
                articles = case.get('retrieved_articles', [])
                for i, title in enumerate(articles[:4], 1):  # Top 4 articles
                    context_parts.append(f"[Article {i}] {title}")

            context = " | ".join(context_parts) if context_parts else "N/A"

            writer.writerow([
                case.get('case_id', ''),
                case.get('query', ''),
                case.get('bot_response', ''),
                context,
                '', '', '', '', '', '', '', '',  # Empty columns for manual labeling
            ])

def create_calibration_key(sample, output_path):
    """Create calibration key CSV with judge verdicts (hidden from labeler)."""
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'case_id',
            'correctness_verdict',
            'correctness_reason',
            'groundedness_verdict',
            'groundedness_reason',
            'relevancy_verdict',
            'relevancy_reason',
            'not_excessive_verdict',
            'not_excessive_reason',
            'helpful_verdict',
            'helpful_reason',
            'legal_verdict',
            'legal_reason',
            'redirects_verdict',
            'redirects_reason'
        ])

        for case in sample:
            correctness = case.get('correctness', {})
            groundedness = case.get('groundedness', {})

            # Extract verdicts (handle both dict and non-dict)
            correctness_verdict = correctness.get('correct') if isinstance(correctness, dict) else correctness
            correctness_reason = correctness.get('reason') if isinstance(correctness, dict) else ''

            groundedness_verdict = groundedness.get('grounded') if isinstance(groundedness, dict) else groundedness
            groundedness_reason = groundedness.get('reason') if isinstance(groundedness, dict) else ''

            writer.writerow([
                case.get('case_id', ''),
                correctness_verdict,
                correctness_reason,
                groundedness_verdict,
                groundedness_reason,
                '', '', '', '', '', '', '', '',  # Other judges not in baseline
            ])

def print_sample_stats(sample):
    """Print statistics about the sample."""
    escalate = [c for c in sample if c.get('expected_action') == 'escalate']
    critical = [c for c in sample if c.get('risk_level') == 'critical']
    critical_escalate = [c for c in escalate if c.get('risk_level') == 'critical']

    passed = [c for c in sample if determine_judge_status(c) == 'passed']
    failed = [c for c in sample if determine_judge_status(c) == 'failed']

    print('=' * 80)
    print('CALIBRATION SAMPLE STATISTICS')
    print('=' * 80)
    print(f'Total samples: {len(sample)}')
    print(f'Escalate cases: {len(escalate)}')
    print(f'Critical cases: {len(critical)}')
    print(f'Critical escalate: {len(critical_escalate)}')
    print(f'Passing: {len(passed)}')
    print(f'Failing: {len(failed)}')

    print(f'\nTarget was: ~20 escalate (≥10 critical) + ~30 answer')
    print(f'Actual: {len(escalate)} escalate ({len(critical_escalate)} critical)')

    print(f'\nSample breakdown:')
    print(f'  Escalate (critical): {len(critical_escalate)}')
    print(f'  Escalate (non-critical): {len(escalate) - len(critical_escalate)}')
    print(f'  Answer: {len(sample) - len(escalate)}')

def main():
    random.seed(42)  # For reproducibility

    print("Loading baseline results...")
    results = load_baseline_results()
    print(f"Loaded {len(results)} results")

    print("Generating stratified sample (50 rows)...")
    sample = stratify_sample(results, n=50)
    print_sample_stats(sample)

    print("\nCreating calibration sheet...")
    create_calibration_sheet(sample, 'benchmark/calibration_sheet.csv')
    print("✅ Created benchmark/calibration_sheet.csv")

    print("Creating calibration key...")
    create_calibration_key(sample, 'benchmark/calibration_key.csv')
    print("✅ Created benchmark/calibration_key.csv")

    print("\n" + "=" * 80)
    print("CALIBRATION SHEET READY")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Manually label benchmark/calibration_sheet.csv")
    print("2. Run scripts/compute_agreement.py to calculate agreement statistics")
    print("3. Review disagreement rows")

if __name__ == "__main__":
    main()
