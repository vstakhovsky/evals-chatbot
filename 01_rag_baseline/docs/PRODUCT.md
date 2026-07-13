# PRODUCT.md — how this project makes decisions

One page. If a section outgrows this file, it's a symptom, not progress.

## Two problems, two success criteria
- **Modeled problem**: first-line fintech support RAG — safely resolve frequent low-risk requests, escalate critical/unknown ones. Success = trustworthy metrics on the metric tree.
- **Real problem**: a portfolio artifact demonstrating eval-quality reasoning. Success = visible trade-offs, honest limitations, decisions traceable to data.
Every addition must serve at least one. Serving neither → cut.

## Validity chain (check before trusting any number)
business problem → metric tree → benchmark → judges → numbers → decisions.
A number is only as trustworthy as the weakest link. Current weakest link: **judge calibration**
(no human-agreement measurement yet) — until fixed, all judge-derived claims carry an "uncalibrated" caveat,
and no optimization (GEPA) may target an uncalibrated judge.

## Benchmark quality = four properties (not case count)
1. **Validity** — ground truth verified programmatically (validate_dataset.py), earned via 3 fix iterations.
2. **Coverage** — topics × risk × difficulty; conscious gaps: no multi-turn, no account state, no production distribution.
3. **Discriminative power** — different systems must score differently; our 59–94% spread confirms it. All-0.95+ would mean a useless benchmark.
4. **Stability** — frozen test split (group-aware by seed_id); all stage comparisons run against it.
Predictiveness of production outcomes is unmeasurable offline → recorded as limitation; shadow-mode pilot is the measurement plan.

## Decision rules
- **Decision-changing test**: a metric/entity lives only if a different value would change someone's recommendation. Owner + action required.
- **n-gating**: every number ships with n; slice conclusions with n<20 are hypotheses, not findings.
- **Error-analysis outcomes**: every failure conclusion ends in one of five: fix prompt | fix KB | fix retrieval | fix benchmark label | accept as limitation. Nothing else counts as analysis.
- **Expansion rule**: add cases/personas/judges only when a specific pending decision is blocked by lack of data.
- **Pre-registration**: optimization stages declare target, minimal meaningful delta, guardrails, and split BEFORE running (see docs/specs/02_gepa_preregistration.md).

## Trade-off ledger (chosen positions)
| Trade-off | Our position | Why |
|---|---|---|
| Safety vs deflection | Critical escalation recall → ~1.00, accept higher false-escalation | Missed fraud costs trust/regulatory; false escalation costs one ticket |
| Synthetic vs real data | Synthetic with verified ground truth | Real logs unavailable; ground truth > realism at this stage |
| Judge strictness | Strict on no_false_info & legally_correct; balanced elsewhere | Asymmetric cost of hallucination in fintech |
| Breadth vs depth | Depth on ~10 topics / ~130 seeds | Thin slices produce noise, not findings |
| Offline vs online truth | Offline eval = regression gate + prioritization compass, never impact proof | Avoided-contacts formula is an illustrative proxy |

## Guardrails map (enforced where they execute; reviews only audit)
| Guardrail | Layer | Enforced by | Verified by |
|---|---|---|---|
| Critical requests never resolved by bot | Runtime | SYSTEM_PROMPT routing rule (`ACTION: escalate`) | 26 critical cases; `missed_critical_escalations` = 0 (absolute count) |
| No sensitive-data requests/leaks (PIN/CVV/OTP/password) | Runtime | Deterministic regex on every generated answer | `sensitive_data_violations` = 0 (absolute count) |
| Decline & redirect when KB lacks the answer | Runtime | SYSTEM_PROMPT rule (candidate lever for 02: retrieval-score threshold) | 26 unknown cases; unknown escalation rate |
| No financial advice / toxicity / competitor mentions | Runtime | SYSTEM_PROMPT constraints | `judge_legally_correct` (LLM-judged — weakest link, noted) |
| Optimization cannot regress safety | Experiment | Pre-registration floors/ceilings; frozen test split | Paired before/after on the locked split |
| Ground truth cannot silently rot | Data | validate_dataset.py (labels, leakage, answerability) on every benchmark change | Validation summary committed with the change |
| Prompt/judge changes cannot ship unmeasured | Process | Rule: any SYSTEM_PROMPT/judges.py change → re-run critical+unknown subset (44 cases, <$0.50) before commit | 3-line subset report pasted into the commit message |
| Secrets cannot leak | Process | scripts/check_secrets.sh + gitleaks CI | CI status green |

Strength ordering: deterministic code > prompt rule > LLM judge > human review — always use the strongest
available; safety-critical guardrails must never rely on an LLM judge alone.

## Cadence
End of every stage: run product-validation skill on results + ponytail-review on the repo;
update this file only if a position changed; write a one-page decision memo ("what I'd tell the Head of Support").
