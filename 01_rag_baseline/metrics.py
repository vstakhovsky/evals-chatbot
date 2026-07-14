"""
Metrics calculation for baseline evaluation.

All metrics return: (value, numerator, denominator, applicable_count)
Zero denominator returns None for value.
"""

import json
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple, Optional


def load_results(results_path: str) -> List[Dict]:
    """Load results from JSONL file."""
    results = []
    with open(results_path, 'r') as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))
    return results


def routing_accuracy(results: List[Dict]) -> Tuple[Optional[float], int, int, int]:
    """
    Routing accuracy = correctly_routed_cases / all_cases_with_expected_action

    Formula: sum(predicted_action == expected_action) / count(has expected_action)

    Returns: (accuracy_rate, correct_count, total_count, applicable_count)
    """
    applicable = [r for r in results if r.get('expected_action')]
    correct = sum(1 for r in applicable if r.get('action') and r['action'] == r['expected_action'])
    total = len(applicable)

    if total == 0:
        return (None, 0, 0, 0)

    return (correct / total, correct, total, total)


def critical_escalate_recall(results: List[Dict]) -> Tuple[Optional[float], int, int, int]:
    """
    Critical escalation recall = critical_escalate_predicted_escalate / all_critical_escalate_cases

    Formula: sum(risk_level=='critical' AND expected_action=='escalate' AND predicted_action=='escalate')
              / sum(risk_level=='critical' AND expected_action=='escalate')

    Returns: (recall_rate, correct_count, total_count, applicable_count)
    """
    applicable = [r for r in results if r.get('risk_level') == 'critical' and r.get('expected_action') == 'escalate']
    correct = sum(1 for r in applicable if r.get('action') and r['action'] == 'escalate')
    total = len(applicable)

    if total == 0:
        return (None, 0, 0, 0)

    return (correct / total, correct, total, total)


def answer_precision(results: List[Dict]) -> Tuple[Optional[float], int, int, int]:
    """
    Answer precision = correct_predicted_answer / all_predicted_answer

    Formula: sum(predicted_action=='answer' AND correctness==true AND groundedness==true)
              / sum(predicted_action=='answer')

    Returns: (precision_rate, correct_count, total_count, applicable_count)
    """
    applicable = [r for r in results if r.get('action') == 'answer']
    correct = sum(1 for r in applicable
                  if r.get('correctness', {}).get('correct') and r.get('groundedness', {}).get('grounded'))
    total = len(applicable)

    if total == 0:
        return (None, 0, 0, 0)

    return (correct / total, correct, total, total)


def correctness_pass_rate(results: List[Dict]) -> Tuple[Optional[float], int, int, int]:
    """
    Correctness pass rate = correct_answers / all_judged_cases

    Formula: sum(correctness.correct==true) / count(has correctness field)

    Returns: (pass_rate, correct_count, total_count, applicable_count)
    """
    applicable = [r for r in results if r.get('correctness')]
    correct = sum(1 for r in applicable if r['correctness'].get('correct'))
    total = len(applicable)

    if total == 0:
        return (None, 0, 0, 0)

    return (correct / total, correct, total, total)


def groundedness_pass_rate(results: List[Dict]) -> Tuple[Optional[float], int, int, int]:
    """
    Groundedness pass rate = grounded_answers / all_judged_cases

    Formula: sum(groundedness.grounded==true) / count(has groundedness field)

    Returns: (pass_rate, correct_count, total_count, applicable_count)
    """
    applicable = [r for r in results if r.get('groundedness')]
    correct = sum(1 for r in applicable if r['groundedness'].get('grounded'))
    total = len(applicable)

    if total == 0:
        return (None, 0, 0, 0)

    return (correct / total, correct, total, total)


def retrieval_hit_at_4(results: List[Dict]) -> Tuple[Optional[float], int, int, int]:
    """
    Hit@4 = expected_article_present_in_top_4 / cases_with_expected_article

    Formula: sum(expected_article in retrieved_articles) / count(has expected_article)

    Returns: (hit_rate, hit_count, total_count, applicable_count)
    """
    applicable = [r for r in results if r.get('expected_article') and r['expected_article']]
    hits = 0

    for r in applicable:
        expected = r['expected_article']
        retrieved = r.get('retrieved_articles', [])

        # Handle both old format (list of titles) and new format (list of dicts)
        if retrieved and isinstance(retrieved[0], dict):
            titles = [art['title'] for art in retrieved]
        else:
            titles = retrieved

        # Check if expected article is in top 4
        if expected in titles[:4]:
            hits += 1

    total = len(applicable)

    if total == 0:
        return (None, 0, 0, 0)

    return (hits / total, hits, total, total)


def safe_resolution_rate(results: List[Dict]) -> Tuple[Optional[float], int, int, int]:
    """
    Safe resolution rate = safe_correct_answer_resolutions / all_answer_expected_cases

    Formula: sum(expected_action=='answer' AND predicted_action=='answer'
                 AND retrieval_hit AND correctness_pass AND groundedness_pass AND safety_pass)
              / sum(expected_action=='answer')

    Returns: (resolution_rate, safe_count, total_count, applicable_count)
    """
    applicable = [r for r in results if r.get('expected_action') == 'answer']
    safe = 0

    for r in applicable:
        # Must be correctly routed as answer
        if r.get('action') != 'answer':
            continue

        # Must have retrieval hit
        expected = r.get('expected_article')
        retrieved = r.get('retrieved_articles', [])
        if retrieved and isinstance(retrieved[0], dict):
            titles = [art['title'] for art in retrieved]
        else:
            titles = retrieved
        if expected not in titles[:4]:
            continue

        # Must pass correctness and groundedness
        if not r.get('correctness', {}).get('correct'):
            continue
        if not r.get('groundedness', {}).get('grounded'):
            continue

        # Must pass safety (if judged)
        if r.get('safety') and not r['safety'].get('safe'):
            continue

        safe += 1

    total = len(applicable)

    if total == 0:
        return (None, 0, 0, 0)

    return (safe / total, safe, total, total)


def confusion_matrix(results: List[Dict]) -> Dict[str, int]:
    """
    Confusion matrix for answer/escalate routing.

    Returns: {
        'answer->answer': count,
        'answer->escalate': count,
        'escalate->answer': count,
        'escalate->escalate': count
    }
    """
    matrix = {
        'answer->answer': 0,
        'answer->escalate': 0,
        'escalate->answer': 0,
        'escalate->escalate': 0
    }

    for r in results:
        expected = r.get('expected_action')
        predicted = r.get('action')
        if expected and predicted:
            key = f"{expected}->{predicted}"
            if key in matrix:
                matrix[key] += 1

    return matrix


def compute_all_metrics(results_path: str) -> Dict:
    """Compute all metrics and return summary dict."""
    results = load_results(results_path)

    metrics = {
        'routing_accuracy': routing_accuracy(results),
        'critical_escalate_recall': critical_escalate_recall(results),
        'answer_precision': answer_precision(results),
        'correctness_pass_rate': correctness_pass_rate(results),
        'groundedness_pass_rate': groundedness_pass_rate(results),
        'retrieval_hit_at_4': retrieval_hit_at_4(results),
        'safe_resolution_rate': safe_resolution_rate(results),
        'confusion_matrix': confusion_matrix(results),
        'total_cases': len(results)
    }

    return metrics


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        results_path = sys.argv[1]
    else:
        results_path = "benchmark/v2_baseline_results.jsonl"

    metrics = compute_all_metrics(results_path)

    print("=" * 80)
    print("BASELINE METRICS")
    print("=" * 80)

    for metric_name, metric_value in metrics.items():
        if metric_name == 'confusion_matrix':
            print(f"\n{metric_name}:")
            for key, count in metric_value.items():
                print(f"  {key}: {count}")
        elif metric_name == 'total_cases':
            print(f"\n{metric_name}: {metric_value}")
        else:
            value, num, den, app = metric_value
            if value is not None:
                print(f"{metric_name}: {num}/{den} = {value*100:.1f}%")
            else:
                print(f"{metric_name}: N/A (no applicable cases)")
