# Pre-registration: Stage 02 — GEPA optimization

Commit this file COMPLETED before the first optimization run. Results contradicting this document
are still results; moving the goalposts after seeing them is not.

## 1. Optimization target (exactly one)
- Artifact being optimized: `<e.g. RAG system prompt, version rag_system_v2_routing>`
- Failure mode addressed: `<e.g. bot answers instead of escalating when KB lacks the answer>`
- Baseline evidence: `<metric = X.XX (n=N/D) on frozen test split, run_id=...>`

## 2. Success criterion
- Primary metric: `<e.g. correct_routing_rate on unknown+critical cases>`
- Minimal meaningful delta: `<e.g. +10 p.p. on test split>` — smaller improvements are reported as "no confirmed effect".
- Split usage: train `<n>` for GEPA, dev `<n>` for selection, test `<n>` LOCKED — touched exactly once, for the final before/after.

## 3. Guardrails (must not regress)
| Metric | Baseline | Floor/Ceiling |
|---|---|---|
| critical_escalation_recall | `X.XX` | floor: no decrease |
| false escalation rate (low-risk answered as escalate) | `X.XX` | ceiling: `<baseline + 5 p.p.>` |
| safe_resolution_rate | `X.XX` | floor: `<baseline − 2 p.p.>` |
| missed_critical_escalations (absolute) | `N` | must remain 0 / not increase |

## 4. Comparison protocol
- Paired, case-level, same frozen test split, same judge versions (`judge_prompt_version=...`).
- Report: before/after per metric with n, fixed vs regressed case counts (2×2), per-topic deltas.
- Judges are calibrated (human agreement ≥ `<85>`% on `<50>` labeled rows) BEFORE this run; if not — stop.

## 5. Stopping rule & budget
- Max GEPA iterations / API budget: `<...>`. If target not reached within budget → report honestly, analyze, do not extend silently.

## 6. Declared beforehand
- Date, run_id prefix, random seed, model versions: `<...>`
- Anything not listed above that looks interesting in results = exploratory, labeled as such.
