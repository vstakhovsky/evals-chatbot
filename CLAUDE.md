# Claude Code Instructions

## Hard Rules

**NO LABEL ACCESS — Pipeline cannot use benchmark ground truth columns (risk_level, expected_action, etc.). Any fixes must use only query text + retrieved context + system prompt. Label leakage invalidates A/B comparisons and is forbidden.**

## Project Context

This is a fintech support RAG evaluation project with validated benchmark datasets and judge-based quality metrics.

## Key Constraints

1. **No label leakage:** Benchmark ground truth (risk_level, expected_action, expected_article) is for evaluation only, never for pipeline logic
2. **Weak RAG baseline:** Use gpt-4o-mini for bot responses to make failures visible and judges useful
3. **GPT-4o judges:** All LLM judges use GPT-4o for consistent calibration (cheap judges that fail = re-run everything)
4. **Test split frozen:** Never modify test cases after first baseline run — hash is frozen in README
5. **Incremental saves:** All long-running processes must save incrementally and support resume

## Development Phases

- **Stage 01:** Build frozen baseline with validated benchmark (current phase)
- **Stage 02:** GEPA optimization against frozen baseline (future)
- **Stage 03:** Production deployment (future)

## File Structure

- `benchmark/`: Validated seed cases and generated variants
- `data/`: Knowledge base articles and pre-computed embeddings
- `docs/`: Decision log, specs, and validation reports
- `*.py`: Pipeline components (dataset generation, validation, smoke test)
