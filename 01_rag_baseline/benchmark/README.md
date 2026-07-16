# Fintech Support Benchmark — v2

**Purpose:** Internal benchmark for measuring RAG chatbot performance on fintech support queries with safe resolution and critical routing metrics.

**Scope:**
- Single-turn support Q&A
- Knowledge-base-only (no account data, no transaction history, no user-specific context)
- Offline evaluation only (no production claims)
- No multi-turn conversations

**Composition:**
- **Seeds:** 121 human-designed seed cases
- **Variants:** 2-4 controlled variants per seed (234 total variants)
- **Total:** 355 cases
- **Splits:** 175 optimization (49.3%) / 61 development (17.2%) / 119 holdout_candidate (33.5%)
- **Coverage:** Mix of low-risk, critical fraud/security, unknown/out-of-scope, and edge cases

**Primary Metrics:**
- **Safe resolution rate** (answer-cases): Hit@4 ∧ correctness ∧ groundedness ∧ no safety violation
- **Correct routing rate**: predicted_action == expected_action
- **Critical escalation recall**: critical cases routed to escalate / all critical

**Secondary Metrics:**
- Relevancy, conciseness, helpfulness, legal compliance, redirects when unknown

**Retrieval Metrics:**
- Hit@4 (article in top 4 retrieved)
- MRR (mean reciprocal rank)

**Limitations:**
- **All labels are provisional** (`needs_review`, not human-validated)
- **Split is not frozen** (holdout_candidate is provisional)
- **No canonical baseline run exists** (legacy 363-case run incompatible)
- Synthetic-heavy (only 121 human-designed seeds, rest are controlled variants)
- No production distribution measurement
- No account data access (KB-only queries)
- Single-turn only (no conversation history)
- Judges are not calibrated

**Usage:**
1. Generate dataset: `python generate_dataset.py --v2`
2. Validate dataset: `python validate_dataset.py benchmark/cases.jsonl`
3. Run baseline: `python run_baseline.py`
4. View results in `results/canonical/`

**Dataset Contract:**
- All cases have `case_id`, `seed_id`, `query`, `expected_action`, `risk_level`, `expected_article`, `required_facts`
- All critical cases have `expected_action == escalate`
- All variants of a `seed_id` are in the same split (no split leakage)
- Article IDs reference existing knowledge base articles
- Hash computed from sorted case IDs for reproducibility

**Current Status:**
- ⚠️ **Provisional labels** — All 355 cases are `needs_review` (not human-validated)
- ⚠️ **Provisional split** — Holdout not frozen; may adjust before stage 02
- ⚠️ **No canonical run** — Must execute baseline before reporting metrics
- ❌ **Legacy metrics invalidated** — 363-case run incompatible with current 355-case benchmark

## Changelog

### v2 Dataset Generation (2026-07-13)
- **Current dataset:** 355 cases (121 unique seeds + 234 variants)
- **Case count change:** Reduced from 363 to 355 cases by removing 8 duplicate/invalid cases during validation
- **Split distribution:** 175 optimization / 61 development / 119 holdout_candidate
- **Label status:** All cases marked `needs_review` (provisional, not validated)
- **No baseline executed** — Canonical run required for metric reporting

### v1 → v2 Migration
- **Removed:** Legacy CSV formats (`synthetic_queries.csv`, `synthetic_rag_outputs.csv`, `synthetic_eval_results.csv`)
- **Consolidated:** Single benchmark file (`benchmark/cases.jsonl`)
- **Updated:** Metric implementations with proper applicability-aware denominators
- **Simplified:** Removed smoke test scripts; consolidated validation into single validator

## Dataset Version History

**v2_2026_07_14** (current): Updated dataset version to reflect actual creation date. The previous version v2_2025-07_13 contained an incorrect year - this benchmark was created in July 2026, not July 2025. All 355 cases updated to v2_2026_07_14.

**v2_2025_07_13**: Initial v2 canonical benchmark with 355 cases and 121 independent families. Structural validation and family split verification.
