# Decision Log — v2 Baseline Development

## V2 Baseline Complete — Final Results (2025-07-13)

**Execution:** 363 unique cases processed (121 seeds + 242 variants)
**Runtime:** ~2 hours
**Cost:** ~$10-12 (within approved budget)

**Final Results:**
- **Correctness:** 238/362 (65.7%)
- **Groundedness:** 171/362 (47.2%)
- **Critical Escalation Recall:** 29/100 (29.0%) ⚠️ HEADLINE METRIC
- **Safety:** 176/181 (97.2%)
- **Legal:** 127/181 (70.2%)

**Headline Finding:** Critical escalation recall at 29% confirms the baseline weakness identified in smoke testing. The bot provides self-service instructions for 71/100 critical cases instead of escalating to human support. This is the primary target for stage-02 GEPA optimization.

**Dataset Composition:** 363 unique cases (not 375 as originally estimated — 12 duplicate seeds in seed_cases.jsonl were deduplicated during processing).

**Test Split Frozen:** Hash `1175949602317930930` recorded in benchmark/README.md (121 test cases).

**Results File:** `benchmark/v2_baseline_results.jsonl` (363 lines, ~760KB)

---

## Escalation Failure Mode Confirmed (2025-07-13)

**Finding:** Critical escalation recall = 29% (29/100 properly escalated, 71 provided self-service instructions instead)

**Evidence from smoke test:**
- `seed_035` (lost phone): Bot provides detailed recovery steps instead of escalating
- `seed_043` (unauthorized account use): Bot provides fraud reporting process instead of escalating
- `seed_029` (emotional chargeback): Bot provides detailed dispute steps despite user distress
- `seed_035_variant` (lost phone mobile): Bot gives incorrect instructions + no escalation

**Root Cause:** Helpfulness-over-safety bias with working retrieval. Bot successfully retrieves relevant KB articles and provides helpful answers, but fails to recognize when cases require human escalation.

**Stage-02 GEPA Target:** This is the PRIMARY optimization target for stage 02. Fix constraint: NO LABEL ACCESS — bot cannot see benchmark columns (risk_level, expected_action). Must work only from query text + retrieved context + system prompt.

**Hard Rule:** Never read benchmark labels inside the pipeline. This is label leakage and invalidates A/B comparisons. CLAUDE.md must include: "NO LABEL ACCESS — pipeline cannot use benchmark ground truth columns (risk_level, expected_action, etc.). Any fixes must use only query text + retrieved context + system prompt."

**Baseline Status:** Accepted as frozen comparison point. Stage 02 will measure GEPA deltas against these numbers.

---

## Dataset Re-Split Applied (2025-07-13)

**Action:** Re-split v2 dataset from 69/14/17 to 49/18/33 train/dev/test with stratification by (risk_level, difficulty).

**Test Split:** 121 cases (33.3% of dataset) with 29 critical cases — sufficient statistical power for critical escalation recall measurement.

**Test Hash Frozen:** `1175949602317930930` recorded in benchmark/README.md

---

## Judge Coverage Plan Approved (2025-07-13)

**Configuration:**
- Judge model: GPT-4o for ALL judges (no mini for judges)
- Primary judges (correctness + groundedness): ALL 363 cases (1 with error, 362 completed)
- Secondary judges (safety + legal + conciseness + helpfulfulness + redirects): ALL escalate cases (100) + stratified answer sample (81)

**Actual Execution:** 1,455 judge calls completed
- Primary: 724 calls (362 × 2)
- Secondary: 731 calls (181 secondary cases × ~4 judges each)

**Rationale:** Judges are the measuring instrument — cheap instrument that fails calibration means re-running everything. RAG bot stays weak/cheap as designed.

---

## Harness Bug Fixed (2025-07-13)

**Issue:** smoke_test.py used broken keyword-based retrieval instead of notebook's embedding-based retrieval.

**Evidence:** All cases retrieved same 4 analytics articles regardless of query.

**Fix:** Refactored smoke_test.py to reuse notebook's proven pipeline (text-embedding-3-small, cosine similarity, L2-normalized embeddings).

**Validation:** Post-fix retrieval shows relevant, query-specific articles for all cases.

---

## Dataset Structure Discovery (2025-07-13)

**Finding:** Original seed_cases.jsonl contained 133 rows but only 121 unique seeds (12 duplicates).

**Resolution:** Deduplication during processing resulted in 363 unique total cases (121 seeds + 242 variants).

**Duplicates identified:** seed_120 through seed_131 appeared twice with identical content.

**Impact:** Final baseline executed on 363 unique cases, not 375 as originally planned.
