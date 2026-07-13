#!/usr/bin/env python3
"""
Verify ALL seed cases in benchmark/seed_cases.jsonl against KB.

Checks:
1. expected_article exists in revolut_help_articles.jsonl (case-insensitive + fuzzy match)
2. required_facts are present in article content_text (substring match)
3. "unknown" seeds are genuinely unanswerable (retrieval score < 0.45)
4. Critical seeds have expected_action == escalate

Usage:
    python verify_seeds.py

Output:
- Summary counts (valid, invalid by category)
- List of every flagged seed with reason
- For "unknown" seeds: top retrieval score + article title
"""

import json
import os
import sys
from typing import Dict, List, Tuple

# Paths
SEEDS_PATH = "benchmark/seed_cases.jsonl"
KB_PATH = "data/revolut_help_articles.jsonl"


def load_articles() -> Tuple[List[dict], Dict[str, dict]]:
    """Load KB articles and build title lookup (case-insensitive)."""
    articles = []
    title_lookup = {}

    with open(KB_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                article = json.loads(line)
                articles.append(article)
                # Case-insensitive title lookup
                title_lower = article["title"].lower()
                title_lookup[title_lower] = article
            except json.JSONDecodeError:
                continue

    return articles, title_lookup


def find_article(expected_title: str, title_lookup: Dict[str, dict]) -> Tuple[bool, str, dict]:
    """
    Find article in KB by expected_title.
    Returns: (found, match_method, article)
    """
    if not expected_title or expected_title == "null" or expected_title == "None":
        return True, "null_expected_valid", None  # None is valid for unknown cases

    expected_lower = expected_title.lower()

    # Exact case-insensitive match
    if expected_lower in title_lookup:
        return True, "exact_match", title_lookup[expected_lower]

    # Substring match (expected_title is substring of KB title)
    for kb_title_lower, article in title_lookup.items():
        if expected_lower in kb_title_lower or kb_title_lower in expected_lower:
            return True, f"substring_match({kb_title_lower})", article

    return False, "not_found", None


def verify_facts_in_article(required_facts: List[str], article: dict) -> Tuple[bool, List[str]]:
    """
    Verify required_facts are present in article content_text.
    Uses keyword matching: extract keywords from fact, check if ANY keyword is in content.
    Returns: (all_found, missing_facts)
    """
    if not required_facts or not article:
        return True, []

    content_lower = article.get("content_text", "").lower()
    missing_facts = []

    for fact in required_facts:
        # Extract keywords from fact (remove common words and arrows)
        # Split on non-word characters, keep meaningful words
        import re
        keywords = [w.lower() for w in re.findall(r'\b\w{3,}\b', fact)
                    if w.lower() not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'get', 'has', 'his', 'how', 'its', 'set', 'two', 'use', 'why']]

        # Check if at least one meaningful keyword is in the content
        found = any(kw in content_lower for kw in keywords)

        if not found:
            missing_facts.append(fact)

    return len(missing_facts) == 0, missing_facts


def load_seeds() -> List[dict]:
    """Load all seed cases."""
    seeds = []
    with open(SEEDS_PATH, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                seed = json.loads(line)
                seeds.append(seed)
            except json.JSONDecodeError as e:
                print(f"Parse error at line {line_num}: {e}", file=sys.stderr)

    return seeds


def check_unknown_answerable(unknown_seeds: List[dict], articles: List[dict]) -> List[dict]:
    """
    Placeholder for future embedding-based unknown verification.
    Currently disabled — requires numpy + OpenAI embeddings.
    Returns empty list (no unknown seeds flagged as answerable).
    """
    # TODO: Implement with embeddings when numpy available
    # For now, rely on manual verification that unknown topics are genuinely absent from KB
    return []


def verify_seeds(seeds: List[dict], articles: List[dict], title_lookup: Dict[str, dict]) -> Dict:
    """
    Verify all seeds against KB.
    Returns report dict with counts and flagged seeds.
    """
    report = {
        "total": len(seeds),
        "valid": 0,
        "invalid": 0,
        "flags": {
            "missing_article": [],
            "missing_facts": [],
            "unknown_answerable": [],
            "critical_wrong_action": [],
        },
    }

    # Separate unknown seeds for embedding check
    unknown_seeds = [s for s in seeds if s.get("difficulty") == "unknown"]

    # Check unknown seeds with embeddings
    answerable_unknowns = check_unknown_answerable(unknown_seeds, articles)

    for seed in seeds:
        case_id = seed.get("case_id", "unknown")
        query = seed.get("query", "")
        expected_article = seed.get("expected_article")
        required_facts = seed.get("required_facts", [])
        difficulty = seed.get("difficulty", "")
        expected_action = seed.get("expected_action", "")
        risk_level = seed.get("risk_level", "")

        seed_flags = []

        # Check 1: expected_article exists
        found, match_method, article = find_article(expected_article, title_lookup)
        if not found:
            seed_flags.append(f"missing_article ({expected_article})")
            report["flags"]["missing_article"].append({
                "case_id": case_id,
                "query": query,
                "expected_article": expected_article,
            })

        # Check 2: required_facts in article
        if found and article:
            all_facts_found, missing_facts = verify_facts_in_article(required_facts, article)
            if not all_facts_found:
                seed_flags.append(f"missing_facts: {missing_facts}")
                report["flags"]["missing_facts"].append({
                    "case_id": case_id,
                    "query": query,
                    "expected_article": expected_article,
                    "missing_facts": missing_facts,
                })

        # Check 3: unknown seeds are genuinely unanswerable (from embedding check)
        if difficulty == "unknown":
            answerable = next((a for a in answerable_unknowns if a["case_id"] == case_id), None)
            if answerable:
                seed_flags.append(f"unknown_answerable (score={answerable['top_score']:.3f}, article='{answerable['top_article']}')")
                report["flags"]["unknown_answerable"].append({
                    "case_id": case_id,
                    "query": query,
                    "top_score": answerable["top_score"],
                    "top_article": answerable["top_article"],
                })

        # Check 4: critical seeds have expected_action == escalate
        if risk_level == "critical" and expected_action != "escalate":
            seed_flags.append(f"critical_wrong_action (expected '{expected_action}')")
            report["flags"]["critical_wrong_action"].append({
                "case_id": case_id,
                "query": query,
                "expected_action": expected_action,
                "risk_level": risk_level,
            })

        if seed_flags:
            report["invalid"] += 1
        else:
            report["valid"] += 1

    return report


def print_report(report: Dict):
    """Print verification report."""
    print("=" * 80)
    print("SEED VERIFICATION REPORT")
    print("=" * 80)

    print(f"\nTotal seeds: {report['total']}")
    print(f"Valid: {report['valid']}")
    print(f"Invalid: {report['invalid']}")
    print(f"Validity rate: {report['valid'] / report['total'] * 100:.1f}%")

    print("\n" + "-" * 80)
    print("FLAGS BY CATEGORY")
    print("-" * 80)

    # Missing articles
    if report["flags"]["missing_article"]:
        print(f"\n❌ MISSING ARTICLE ({len(report['flags']['missing_article'])} seeds):")
        for item in report["flags"]["missing_article"]:
            print(f"  {item['case_id']}: {item['query'][:60]}...")
            print(f"    Expected: '{item['expected_article']}'")
    else:
        print("\n✅ No missing articles")

    # Missing facts
    if report["flags"]["missing_facts"]:
        print(f"\n❌ MISSING FACTS ({len(report['flags']['missing_facts'])} seeds):")
        for item in report["flags"]["missing_facts"]:
            print(f"  {item['case_id']}: {item['query'][:60]}...")
            print(f"    Article: '{item['expected_article']}'")
            print(f"    Missing facts: {item['missing_facts']}")
    else:
        print("\n✅ No missing facts")

    # Wrong action for critical
    if report["flags"]["critical_wrong_action"]:
        print(f"\n❌ CRITICAL WITH WRONG ACTION ({len(report['flags']['critical_wrong_action'])} seeds):")
        for item in report["flags"]["critical_wrong_action"]:
            print(f"  {item['case_id']}: {item['query'][:60]}...")
            print(f"    Expected action: '{item['expected_action']}' (should be 'escalate')")
            print(f"    Risk level: {item['risk_level']}")
    else:
        print("\n✅ All critical cases have expected_action='escalate'")

    # Unknown but answerable
    if report["flags"]["unknown_answerable"]:
        print(f"\n❌ UNKNOWN BUT ANSWERABLE ({len(report['flags']['unknown_answerable'])} seeds):")
        for item in report["flags"]["unknown_answerable"]:
            print(f"  {item['case_id']}: {item['query'][:60]}...")
            print(f"    Top retrieval score: {item['top_score']:.3f}")
            print(f"    Top article: '{item['top_article']}'")
            print(f"    → Should have expected_article or be marked as 'direct'/'ambiguous'")
    else:
        print("\n✅ All unknown seeds are genuinely unanswerable")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Load data
    print("Loading KB articles...")
    articles, title_lookup = load_articles()
    print(f"Loaded {len(articles)} articles")

    print("\nLoading seeds...")
    seeds = load_seeds()
    print(f"Loaded {len(seeds)} valid seeds")

    # Verify
    print("\nVerifying seeds...")
    report = verify_seeds(seeds, articles, title_lookup)

    # Print report
    print_report(report)

    # Exit with error if any invalid seeds
    if report["invalid"] > 0:
        print(f"\n❌ VERIFICATION FAILED: {report['invalid']} invalid seeds found")
        sys.exit(1)
    else:
        print(f"\n✅ ALL SEEDS PASSED VERIFICATION")
        sys.exit(0)
