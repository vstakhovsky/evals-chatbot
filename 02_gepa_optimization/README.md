# Stage 02 — GEPA Prompt Optimization

**Status:** Planned

## Purpose

Optimize routing and answer-generation prompts against the optimization split while preserving the development and holdout sets.

## Entry Criteria

- Human-labeled sample completed
- Holdout approved and frozen
- Canonical baseline results available

## Planned Outputs

- Baseline vs optimized comparison
- Metric deltas by scenario and risk
- Regression report
- Optimization history
- Development and holdout results

## Non-Goals

- No GEPA optimization before human label review
- No optimization against holdout
- Split by case family (no row-level leakage)
- No improvement claims from optimization-set results alone
