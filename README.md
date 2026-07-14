# evals-chatbot

**Evolution of a RAG chatbot through systematic LLM-based evaluation and optimization.**

This project demonstrates building a minimal FAQ chatbot and progressively improving it using:
- Synthetic data generation (personas × scenarios × modifiers)
- Binary LLM-as-a-judge evaluation
- Pass rate metrics as optimization targets

## Business Problem

**Reduce support cost safely** by automating first-line resolution for common, low-risk queries while ensuring high-risk cases are escalated appropriately.

**Key metrics:**
- **Safe resolution rate**: Correct, grounded, safe answers to answerable queries
- **Critical escalation recall**: High-risk cases correctly escalated
- **Correct routing rate**: Predicted action matches expected action

**Note:** "Estimated avoided contacts" and business impact calculations are illustrative proxies for evaluation methodology, not measured savings.

## Current Status

**Implemented:**
- ✅ Stage 01 RAG + judge pipeline
- ✅ Canonical benchmark: 355 synthetic queries
- ✅ Deterministic dataset generation with hash verification
- ✅ Artifact validation and reproducibility checks
- ✅ Tested metric contracts with proper applicability rules

**Provisional:**
- ⚠️ All labels are `needs_review` (not human-validated)
- ⚠️ Split assignments are provisional (holdout not frozen)
- ⚠️ Judges are not calibrated
- ⚠️ No canonical baseline run completed yet

**Planned:**
- 📋 Stage 02: GEPA prompt optimization
- 📋 Stage 03: Skills experiments (tool-calling, agents)
- 📋 Stage 04: Multi-turn user simulator

## Quickstart

**For presentation:**

1. **View benchmark examples:**
   ```bash
   # View canonical benchmark structure
   head -n 3 01_rag_baseline/benchmark/cases.jsonl

   # Check current split distribution
   python3 -c "
import json
cases = [json.loads(l) for l in open('01_rag_baseline/benchmark/cases.jsonl')]
from collections import Counter
print(Counter(c['split'] for c in cases))
   "
   ```

2. **Validate dataset integrity:**
   ```bash
   python3 01_rag_baseline/validate_dataset.py 01_rag_baseline/benchmark/cases.jsonl
   ```

**For reproduction:**

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API key:**
   ```bash
   # Create .env file with your OPENAI_API_KEY
   echo "OPENAI_API_KEY=your_key_here" > .env
   ```

3. **Run baseline evaluation:**
   ```bash
   cd 01_rag_baseline
   python3 run_baseline.py
   ```

## Repository Structure

```
evals-chatbot/
├── README.md                      # This file
├── requirements.txt               # Python dependencies
├── .gitignore                     # Standard ignores
├── 01_rag_baseline/
│   ├── README.md                  # Stage-specific guide
│   ├── run_baseline.py           # Main evaluation script
│   ├── validate_dataset.py        # Dataset validation
│   ├── judges.py                  # Binary LLM-as-a-judge functions
│   ├── metrics.py                 # Metric calculation with proper formulas
│   ├── faq_rag_chatbot.ipynb     # Analysis and visualization
│   ├── benchmark/
│   │   └── cases/
│   │       ├── canonical.jsonl    # Canonical benchmark (355 cases)
│   │       └── hash.sha256         # Benchmark hash for reproducibility
│   ├── data/
│   │   └── reference/
│   │       ├── revolut_help_articles.jsonl    # Knowledge base
│   │       └── banking77_queries.txt            # Real queries for realism validation
│   └── results/
│       └── canonical/              # Canonical run artifacts
├── 02_gepa_optimization/         # Planned: Prompt optimization
├── 03_skills_experiments/        # Planned: Advanced skills exploration
└── 04_simulator/                 # Planned: Multi-turn user simulation
```

## Benchmark Construction

**Dataset:** 355 synthetic queries constructed from:
- 121 seed cases (manually authored scenarios)
- 234 variant cases (seed × persona × modifier combinations)
- Deterministic deduplication and hash verification
- Stratified splits: optimization (175), development (61), holdout_candidate (119)

**Personas:** Berlin expat freelancer, Spanish student, UK small business owner
**Scenarios:** Card frozen, payment declined, crypto taxes, bereavement, etc.
**Modifiers:** Short/mobile, typo/noisy, non-native English, emotional distress

**Label status:** All 355 cases are `needs_review` (provisional, not human-validated)

## Metric Definitions

All metrics use **applicability-aware** denominators:

| Metric | Numerator | Denominator | Applicability Rule |
|--------|-----------|------------|-------------------|
| Routing accuracy | `predicted_action == expected_action` | Cases with `expected_action` | All labeled cases |
| Critical escalation recall | `predicted_action == escalate` | `risk_level == critical AND expected_action == escalate` | Critical escalation cases only |
| Correctness pass rate | `correctness.correct == true` | `predicted_action == answer AND has correctness result` | Answer cases with judge results |
| Groundedness pass rate | `groundedness.grounded == true` | `predicted_action == answer AND has groundedness result AND has context` | Answer cases with context |
| Safe resolution rate | All applicable checks pass | `expected_action == answer` | Answer cases only |

**Key design principle:** Metrics divide by **applicable cases only**, never total dataset size.

## Current Baseline Status

**❌ NO CANONICAL RUN EXISTS**

The repository contains legacy results from a 363-case run that is **incompatible** with the current 355-case canonical benchmark due to:
- 8 extra result cases (removed duplicates)
- Different dataset hash
- Outdated metric formulas (incorrect denominators)

**Legacy metrics invalidated:**
- ❌ Correctness: 188/363 (wrong denominator)
- ❌ Groundedness: 154/363 (wrong denominator)
- ❌ Routing: 293/363 (incompatible dataset)

**Required before reporting metrics:**
1. Run canonical baseline on 355 cases
2. Use proper applicability-aware metric formulas
3. Validate artifact consistency (result count == benchmark count)

## Technical Stack

- **Embeddings:** OpenAI `text-embedding-3-small`
- **Chat:** `gpt-4o-mini` (weak model for evaluation)
- **Judges:** `gpt-4o` with structured output
- **Retrieval:** NumPy (no vector DB needed for this scale)
- **Data:** pandas for data manipulation, JSONL for structured data

**Design principles:**
- Flat files, no frameworks, no over-engineering
- Binary judges with reasoning (no 0-5 scores)
- Reproducible runs with hash verification
- Applicability-aware metrics (honest denominator calculation)

## Limitations

**Dataset:**
- Synthetic queries (not real customer traffic)
- All labels provisional (`needs_review`, not human-validated)
- No production distribution validation
- Small scale (355 cases vs real traffic volume)

**Evaluation:**
- LLM judges not calibrated
- No measured business impact (CSAT, cost savings, etc.)
- Single-turn only (no conversation context)
- No tool-use or multi-step reasoning

**Scope:**
- FAQ domain only (not comprehensive support coverage)
- English language primarily
- Revolut-specific knowledge base

**These limitations are intentional** for Stage 01 baseline establishment. Later stages address validation, calibration, and coverage expansion.

## What Stage 02 (GEPA) Will Optimize

Once the benchmark is frozen and human-validated:
- Prompt optimization against frozen test set
- Generation prompt refinement (answer quality)
- Judge prompt calibration (agreement measurement)
- A/B testing with proper statistical validation

## Security

See [SECURITY.md](SECURITY.md) for secrets policy, prompt injection surface, and reporting guidelines.

## License

MIT
