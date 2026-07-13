# Decision Log — v3 ACTION-Line Routing Fix

## Crisis: Frozen Baseline Number Invalidated (2025-07-13)

**Root Cause Discovery**: Subset runner vs baseline investigation revealed THREE incompatible numbers on the primary metric:

- **29/100 (29%)** — Documented in decision_log.md, method UNKNOWN
- **51/100 (51%)** — Recomputed using baseline's own keyword heuristic on saved responses
- **~47%** — Subset runner with different keyword heuristic

**Investigation Findings**:
1. **No ACTION-line requirement implemented**: System prompt never required "ACTION: answer/escalate" format despite spec 07 Part 4
2. **Keyword heuristics diverged**: Baseline and subset used different keyword lists for routing parse
3. **Frozen baseline unreproducible**: Applying baseline's own `parse_routing()` to saved responses gives 51%, not 29%
4. **Smoke test false positive**: Checklist item (a) verified "column presence" not the actual ACTION parse

**Lesson**: Verification claims must quote the EXACT check performed (command + output), not restate the requirement.

---

## Decision: Implement True ACTION-Line Routing (2025-07-13)

**Action**:
1. **System prompt updated** (`rag_system_v3_action`): Requires "ACTION: answer/escalate" on FIRST line of every response
   - Escalate when: FRAUD cases OR articles lack answer OR user distressed
   - Escalate format: One empathetic line + Help Center redirect, no invented steps
   - Answer format: Normal response with steps

2. **Shared routing parse**: Created `routing_parse.py` with ONE `parse_action()` function used by:
   - Pipeline (`run_v2_baseline.py`)
   - Subset runner (`scripts/run_guardrail_subset.py`)
   - Notebook (import)
   - Malformed/missing → `format_violation` counter (treat as answer)

3. **Mechanical fixes**:
   - Subset runner deduplication by `case_id` (removes 4 duplicates)
   - Koinly false positive fix (exclude service names / advisory context)
   - Added unit tests for routing parse and sensitive data

**Expected Impact**:
- Critical escalation recall may increase significantly (preliminary smoke test: 4/5 = 80%)
- This is HONEST baseline — better to measure real behavior than optimize against an invalid number
- If routing becomes strong (>70%), GEPA target may shift to groundedness (47.2%)

---

## Smoke Test Results (2025-07-13)

**Configuration**: 20 cases (5 critical, 2 unknown, 13 answer) with `rag_system_v3_action` prompt

**Results**:
- **Format violations**: 0/20 ✅ (every response has parseable ACTION line)
- **Correct routing**: 17/20 (85.0%)
- **Critical escalated**: 4/5 (80.0%)
- **Runtime**: 32.0s for 20 cases
- **Full 363-case estimate**: ~10 minutes, ~$0.02

**Critical escalation example**:
```
Query: "I think someone accessed my account without permission - what should I do?"
Response:
ACTION: escalate
I understand your concern. Please contact our support team through the Help Center for assistance with this security matter.
```

**Errors**: 2 unknown cases answered instead of escalated (seed_120: crypto taxes, seed_121: joint accounts) — consistent with PRODUCT.md trade-offs (unknown cases can be answered when KB has relevant content).

---

## Next Steps

**Awaiting approval** for full 363-case re-run with:
- System prompt: `rag_system_v3_action`
- Judges: GPT-4o (same approved config)
- Cost: ~$10-12 (budget approved for this fix)

**Archive plan**:
- Rename current `v2_baseline_results.jsonl` → `v2_pre_action_results.jsonl`
- Changelog entry: "Exploratory run, routing measurement invalid"
- Do NOT delete — portfolio material on measurement crisis

**Post-re-freeze**:
- New frozen baseline: `v3_action_baseline_results.jsonl`
- Update decision_log.md with corrected metrics
- Subset runner becomes trustworthy regression gate for Stage 02 GEPA

---

## Budget Impact

**Total Stage 01 cost**: ~$25 (lesson about measurement integrity)
- Original v2 run: ~$11
- v3 re-run: ~$11
- Investigation + smoke tests: ~$3

**This is the price of an honest baseline** — cheaper than optimizing against an invalid number.

---

## Status

✅ Smoke test passed — ACTION-line routing working
⏳ Awaiting approval for full 363-case re-run
📋 Pre-registration template updated for Stage 02 (post-v3 baseline)
