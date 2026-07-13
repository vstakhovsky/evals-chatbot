---
name: product-validation
description: Use when reviewing or approving anything product-level in this repo — benchmark design or expansion, new/changed metrics, judges, personas, scenarios, eval results and their interpretation, error-analysis conclusions, stage plans (GEPA, skills, simulator), README/report claims. Validates that measurements connect to decisions, ground truth is trustworthy, sample sizes support conclusions, and trade-offs are explicit. NOT for code style, file structure, or architecture — use ponytail-review for that.
---

# Product Validation Filter

You are reviewing a product/eval artifact, not code. Apply every check below.
Output format: a verdict table `check | pass/fail/n-a | evidence (quote the number or line)`,
then a list of blocking issues, then non-blocking suggestions. Never approve with a blocking issue open.

## 1. Problem linkage
- State in one sentence which problem this artifact serves: the modeled one (safe first-line
  fintech support) or the real one (demonstrating eval-quality reasoning). If neither — recommend cutting.
- Does it move a node in the metric tree (safe resolution / correct routing / critical recall)?
  If it measures something outside the tree, either the tree is incomplete (say so) or the metric is decorative.

## 2. Decision-changing test (the core filter)
For every metric, chart, table, persona, scenario, judge in scope ask:
"If this number/entity were different, would any recommendation change, and whose?"
- No identifiable owner + action → decorative → recommend removal.
- A new persona/scenario/variant family is justified ONLY if it changes expected behavior
  or routing, not for diversity.

## 3. Validity chain
Walk the chain: business problem → metric tree → benchmark → judges → numbers → decisions.
Name the weakest link explicitly. Standard checks:
- Ground truth: is expected_action/expected_article/required_facts verified (validate_dataset.py
  green), or asserted? Unverified ground truth = blocking.
- Judges: is there human calibration (agreement % on a labeled sample)? If not, every judge-derived
  claim must carry the caveat "uncalibrated judge". Optimizing (GEPA) against an uncalibrated judge = blocking.
- Leakage: do paraphrases of one seed cross train/dev/test? Any leakage = blocking.

## 4. Sample-size gating
- Every published number must show n (numerator/denominator). A % without n = blocking.
- Slice conclusions with n < 20 must be labeled "hypothesis, needs more cases", never "finding".
- Deltas (before/after) must state the minimal meaningful difference; a 2 p.p. change on n=40 is noise.

## 5. Error-analysis discipline
Every failure-analysis conclusion must end in exactly one of five outcomes:
(a) fix prompt, (b) fix KB/content, (c) fix retrieval, (d) fix benchmark label, (e) accept as known limitation.
Analysis that ends in none of these is decorative — flag it. Check that outcome (d) is genuinely
considered: mislabeled ground truth is a legitimate and common root cause.

## 6. Trade-off explicitness
For any threshold, target, or design choice, the artifact must state what was traded away and why:
- safety vs deflection (asymmetric error costs: missed critical ≫ false escalation),
- judge strictness vs false alarms,
- breadth (personas/topics) vs depth (n per slice),
- offline proxy vs online truth.
A target with no stated trade-off ("recall > 0.95") is incomplete — require one sentence of rationale.

## 7. Honesty of claims
- No production/impact claims from offline eval (avoided-contacts formula must be labeled illustrative proxy).
- Limitations section present and matching reality — no aspirational checks that don't exist.
- If a question can't be answered from current data, the answer is "not measured; planned for stage X",
  never an invented number.

## 8. Product over-engineering symptoms (flag, propose cut)
Metrics without owners; dashboards nobody reads on a cadence; report longer than its analysis;
"for completeness" sections; expansion (more cases/personas/judges) not blocked-decision-driven.
Rule: expand the benchmark only when a specific pending decision is blocked by lack of data.

## 9. Pre-registration (for optimization stages)
Before any GEPA/optimization run, verify a pre-registration doc exists and is committed BEFORE results:
target metric + minimal meaningful delta + guardrail metrics with floors/ceilings + evaluation split.
Results reported without prior pre-registration = blocking for "improvement" claims
(may still be reported as exploratory).

## 10. Guardrail placement & coverage
For every stated guardrail (see docs/PRODUCT.md Guardrails map), verify three things:
- **Enforced at the executable layer**, not only documented: runtime rules live in the pipeline
  (system prompt / deterministic checks on every answer), experiment rules in metrics.py + pre-registration,
  process rules in CI/scripts. A guardrail that exists only in a README = not a guardrail →
  blocking if safety-critical.
- **Strength ordering respected**: deterministic code > prompt rule > LLM judge > human review.
  Flag any safety-critical guardrail whose only enforcement is an LLM judge.
- **Benchmark coverage**: every runtime guardrail has cases that would catch its failure
  (critical cases → escalation rule; sensitive-data patterns → the regex; unknown cases → decline rule).
  A guardrail with zero covering cases is untested → blocking.
Also verify the regression rule held: any change to SYSTEM_PROMPT or judges.py in scope was
accompanied by a re-run of the critical+unknown subset before commit.
