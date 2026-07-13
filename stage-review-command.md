# /stage-review — end-of-stage audit ritual

Run this at the end of every stage (or before approving a major expansion). You orchestrate existing
tools — do not invent new checks here. Execute in order, collect outputs, then synthesize.

## Steps

1. **Deterministic gates** (run, paste summaries):
   - `python 01_rag_baseline/validate_dataset.py` — ground truth, leakage, realism metrics
   - guardrail subset run (escalate cases) — the 3-line report
   - `scripts/check_secrets.sh` + confirm gitleaks CI green
   - tests (`python -m pytest 01_rag_baseline/`)

2. **Product validation**: apply the `product-validation` skill to the stage's results
   (notebook outputs, metric tables, claims in README). Produce its verdict table.

3. **Repo hygiene**: apply `/ponytail-review` — one-offs to delete, duplicates to consolidate.

4. **Cross-stage consistency**: check that numbers cited in README / PRODUCT.md / decision_log
   match the current notebook outputs; every spec in docs/specs/ for this stage is either
   satisfied or has a written deviation note; frozen test split untouched (compare case_id hash
   against the recorded one).

5. **Error analysis**: invoke the `error-analyst` subagent on the stage's eval results.
   Attach its themes table.

6. **Synthesize a one-page decision memo** (commit to docs/memos/NN_stage_memo.md):
   - 3 lines: what this stage proved, with the key numbers (each with n)
   - weakest link in the validity chain right now
   - top-3 next actions ranked by expected impact, each tied to a metric
   - open questions moved to docs/decision_log.md
   - go / no-go recommendation for the next stage

## Output contract
Verdict table per step (pass/fail/n-a + evidence), then the memo. A stage is DONE only when
steps 1-4 are green and the memo is committed. Never mark done with an open blocking issue.
