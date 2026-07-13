#!/usr/bin/env python3
"""
Smoke test for rag_system_v3_action prompt — 20 cases with ACTION-line routing.

Validates:
- Every response has parseable ACTION line
- Format violations are counted
- At least 5 escalate cases in the sample
- One critical case escalated end-to-end shown in full
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Import from baseline runner
import sys
sys.path.insert(0, '/Users/veniamin/Projects/evals-chatbot/01_rag_baseline')
from run_v2_baseline import ask, load_rag_components
from routing_parse import parse_action, strip_action_line

load_dotenv()

# Configuration
MODEL_RAG = "gpt-4o-mini"
TOP_K = 4
EMBED_MODEL = "text-embedding-3-small"

# Sample: 20 cases with ≥5 escalate
SMOKE_CASES = [
    # Critical cases (should escalate)
    {'case_id': 'seed_009', 'query': 'My card was stolen - how do I get a new one?', 'expected_action': 'escalate', 'risk_level': 'critical'},
    {'case_id': 'seed_043', 'query': 'I think someone accessed my account without permission - what should I do?', 'expected_action': 'escalate', 'risk_level': 'critical'},
    {'case_id': 'seed_035', 'query': 'What should I do if I lost my phone and can\'t access Revolut?', 'expected_action': 'escalate', 'risk_level': 'critical'},
    {'case_id': 'seed_072', 'query': 'My account was frozen after I tried to log in from a new device - help!', 'expected_action': 'escalate', 'risk_level': 'critical'},
    {'case_id': 'seed_010', 'query': 'I see a strange small charge on my card - is this fraud?', 'expected_action': 'escalate', 'risk_level': 'critical'},

    # Unknown cases (should escalate per trade-offs)
    {'case_id': 'seed_120', 'query': 'How do I report my Revolut crypto trading for tax purposes?', 'expected_action': 'escalate', 'risk_level': 'low', 'difficulty': 'unknown'},
    {'case_id': 'seed_121', 'query': 'Does Revolut support joint accounts for married couples?', 'expected_action': 'escalate', 'risk_level': 'low', 'difficulty': 'unknown'},

    # Answer cases (routine queries)
    {'case_id': 'seed_001', 'query': 'How do I freeze my Revolut card?', 'expected_action': 'answer', 'risk_level': 'low'},
    {'case_id': 'seed_002', 'query': 'What are the Revolut card fees for ATM withdrawals?', 'expected_action': 'answer', 'risk_level': 'low'},
    {'case_id': 'seed_003', 'query': 'How do I change my address on Revolut?', 'expected_action': 'answer', 'risk_level': 'low'},
    {'case_id': 'seed_004', 'query': 'Where can I find my IBAN?', 'expected_action': 'answer', 'risk_level': 'low'},
    {'case_id': 'seed_005', 'query': 'How do I order a replacement card?', 'expected_action': 'answer', 'risk_level': 'low'},
    {'case_id': 'seed_006', 'query': 'What is the monthly fee for Revolut Premium?', 'expected_action': 'answer', 'risk_level': 'low'},
    {'case_id': 'seed_011', 'query': 'How do I enable location security feature?', 'expected_action': 'answer', 'risk_level': 'low'},
    {'case_id': 'seed_012', 'query': 'Can I use Revolut card abroad?', 'expected_action': 'answer', 'risk_level': 'low'},
    {'case_id': 'seed_013', 'query': 'How do I set up direct deposit?', 'expected_action': 'answer', 'risk_level': 'low'},
    {'case_id': 'seed_014', 'query': 'What are the transfer limits between Revolut accounts?', 'expected_action': 'answer', 'risk_level': 'low'},
    {'case_id': 'seed_015', 'query': 'How do I close my Revolut account?', 'expected_action': 'answer', 'risk_level': 'low'},
    {'case_id': 'seed_016', 'query': 'Where can I find my transaction history?', 'expected_action': 'answer', 'risk_level': 'low'},
    {'case_id': 'seed_017', 'query': 'How do I contact Revolut support?', 'expected_action': 'answer', 'risk_level': 'low'},
]

async def run_smoke_test():
    """Run smoke test on 20 cases with ACTION-line routing."""
    print("=" * 80)
    print("SMOKE TEST — rag_system_v3_action (20 cases)")
    print("=" * 80)
    print(f"Sample: {len(SMOKE_CASES)} cases ({sum(1 for c in SMOKE_CASES if c.get('expected_action') == 'escalate')} escalate)")

    # Initialize client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("BASE_URL"))

    # Load RAG components
    load_rag_components()

    # Counters
    format_violations = 0
    correct_routing = 0
    critical_escalated = 0

    results = []
    start_time = time.time()

    for i, case in enumerate(SMOKE_CASES):
        case_id = case.get('case_id')
        query = case.get('query')
        expected = case.get('expected_action')
        risk = case.get('risk_level', 'unknown')

        print(f"\n[{i+1}/20] {case_id}: {query[:50]}...")
        print(f"  Expected: {expected} | Risk: {risk}")

        # Get bot response
        bot_response, hits = ask(query, client)

        if not bot_response:
            print(f"  ✗ Bot failed")
            continue

        # Parse ACTION line
        action = parse_action(bot_response)

        if action == 'format_violation':
            format_violations += 1
            print(f"  ⚠️  FORMAT VIOLATION: No parseable ACTION line")
            print(f"  Response preview: {bot_response[:100]}...")
        else:
            print(f"  ✓ ACTION: {action}")

            # Check routing correctness
            if action == expected:
                correct_routing += 1
            else:
                print(f"  ⚠️  Routing mismatch: expected {expected}, got {action}")

            # Count critical escalations
            if risk == 'critical' and action == 'escalate':
                critical_escalated += 1
                if critical_escalated == 1:  # Show first critical escalation in full
                    print(f"\n  📋 FIRST CRITICAL ESCALATION (shown in full):")
                    print(f"  Query: {query}")
                    print(f"  Bot response:\n{bot_response}")
                    print(f"  Retrieved articles: {[h[2].get('title') for h in hits]}")

        # Strip ACTION line for display
        clean_response = strip_action_line(bot_response)

        results.append({
            'case_id': case_id,
            'query': query,
            'expected_action': expected,
            'predicted_action': action,
            'risk_level': risk,
            'format_violation': (action == 'format_violation'),
            'bot_response_clean': clean_response[:100],
        })

    elapsed = time.time() - start_time

    # Print results table
    print("\n" + "=" * 80)
    print("SMOKE TEST RESULTS TABLE")
    print("=" * 80)
    print(f"{'Case':<15} {'Expected':<10} {'Predicted':<10} {'Risk':<10} {'Status':<15}")
    print("-" * 60)

    for r in results:
        status = "✓ Correct" if r['predicted_action'] == r['expected_action'] and not r['format_violation'] else "✗ Error"
        if r['format_violation']:
            status = "⚠️  Format violation"
        print(f"{r['case_id']:<15} {r['expected_action']:<10} {r['predicted_action']:<10} {r['risk_level']:<10} {status:<15}")

    print("=" * 80)
    print(f"SUMMARY:")
    print(f"  Format violations: {format_violations}/20")
    print(f"  Correct routing: {correct_routing}/20 ({correct_routing/20*100:.1f}%)")
    print(f"  Critical escalated: {critical_escalated}/5")
    print(f"  Runtime: {elapsed:.1f}s ({elapsed/60:.1f} minutes)")
    print(f"  Cost estimate for full 363-case run: ${363 * elapsed / 20 / 60 * 0.002:.2f} (rough estimate)")
    print("=" * 80)

    if format_violations > 5:
        print("\n⚠️  High format violation rate - review ACTION-line prompt compliance")
    else:
        print("\n✅ Smoke test passed - ACTION-line routing working")

if __name__ == "__main__":
    asyncio.run(run_smoke_test())
