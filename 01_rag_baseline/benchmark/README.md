# Fintech Support Benchmark — v2

**Purpose:** Validated internal benchmark for measuring RAG chatbot performance on fintech support queries with safe resolution and critical routing metrics.

**Scope:**
- Single-turn support Q&A
- Knowledge-base-only (no account data, no transaction history, no user-specific context)
- No production claims (offline evaluation only)
- No multi-turn conversations

**Composition:**
- **Seeds**: 100-120 human-designed seed cases
- **Variants**: 2-4 controlled variants per seed (350-450 total cases)
- **Splits**: ~50% train / 20% dev / 30% test (grouped by seed_id)
- **Coverage**: Mix of frequent low-risk (~55%), critical fraud/security (~25%), unknown/out-of-scope (~15%), and edge cases (~5%)

**Primary Metrics:**
- **Safe resolution rate** (answer-cases): Hit@4 ∧ correctness ∧ groundedness ∧ no safety violation
- **Correct routing rate**: predicted_action == expected_action
- **Critical escalation recall**: critical cases routed to escalate / all critical

**Secondary Metrics (from v1 baseline):**
- Relevancy, conciseness, helpfulness, legal compliance, redirects when unknown

**Retrieval Metrics:**
- Hit@4 (article in top 4 retrieved)
- MRR (mean reciprocal rank)

**Limitations:**
- Synthetic-heavy (only ~100 human-designed seeds, rest are controlled variants)
- No production distribution measurement
- No account data access (KB-only queries)
- Single-turn only (no conversation history)
- Judges are LLM-based (~80% accuracy on manual spot-check)

**Usage:**
1. Verify seeds: `python verify_seeds.py` (checks articles, facts, labels)
2. Generate variants: `python generate_dataset.py --v2`
3. Validate dataset: `python validate_dataset.py v2_cases.jsonl`
4. Check guardrails: `python guardrails_check.py --pre-baseline`
5. Run benchmark through notebook
6. Regression testing via regression_cases.jsonl
7. Internal model selection; Arena/MTEB shortlist external leaderboards

**Guardrails:**
- test_split_hash: 1175949602317930930 (frozen for stage 02+)
- All critical → escalate ✅
- All unknown → escalate ✅
- No split leakage ✅
- Splits stratified by (risk_level, difficulty) ✅

## Changelog

### v1 → v2 Seed Verification (Current)
- **Initial state:** 109 seeds with issues:
  - Only 2 unknown cases (needed ~15 for measuring redirects_when_unknown failure mode)
  - 2 unknown cases incorrectly labeled with action=answer instead of escalate
  - 6 seeds with oversimplified required_facts that passed verification but lost substantive content

- **Fixes applied:**
  - Added 12 new genuinely unknown seeds (crypto tax, joint accounts, inheritance, business features, PoA, region-specific)
  - Fixed label math: all 26 unknown cases now have expected_action=escalate
  - Restored substantive required_facts for 6 seeds matching actual article content

- **Final state:** 133 seeds (100% verified)
  - 89 low-risk answer | 44 escalate (26 critical + 18 unknown)
  - 77 direct | 17 ambiguous | 13 noisy | 26 unknown
  - All critical → escalate ✅
  - All unknown → escalate ✅
  - No missing articles ✅
  - No missing facts ✅
