# evals-chatbot

Evolution of a RAG chatbot through systematic LLM-based evaluation and optimization.

This repo tells the story of building a minimal FAQ chatbot and progressively improving it using:
- Synthetic data generation (personas × scenarios × modifiers)
- Binary LLM-as-a-judge evaluation
- Pass rate metrics as optimization targets

## Business Goal

**Reduce support cost safely** by automating first-line resolution for common, low-risk queries while ensuring high-risk cases are escalated appropriately.

├── **Safe resolution rate** (answer-cases: Hit@4 ∧ correctness ∧ groundedness ∧ no safety violation)
│   ├── **Correctness / Groundedness**: Binary judges verify factual accuracy and KB-grounding
│   └── **Retrieval**: Hit@4, MRR (mean reciprocal rank)
└── **Correct routing rate** (predicted_action == expected_action)
    └── **Critical escalation recall** (critical cases routed to escalate / all critical)

**Estimated avoided contacts** = daily volume × RAG-eligible share × safe resolution rate
*(Illustrative offline proxy, not measured savings. No DAU/NPS/CSAT claims.)*

**Guardrails map:** See [docs/PRODUCT.md](docs/PRODUCT.md) for enforcement layers and verification.

## Roadmap

| Stage | Focus | Goal | Status |
|-------|-------|------|--------|
| **01_rag_baseline** | RAG + judge pipeline | Establish baseline pass rates on 150 synthetic queries | ✅ |
| 02_gepa_optimization | Prompt optimization | Use GEPA to optimize prompts against frozen eval set | Planned |
| 03_skills_experiments | Advanced skills | Explore tool-calling, multi-step reasoning, agentic patterns | Planned |
| 04_simulator | User simulator | Automated end-to-end testing with simulated users | Planned |

## Quickstart (Stage 01)

1. **Install dependencies:**
   ```bash
   cd 01_rag_baseline
   pip install openai numpy pandas python-dotenv tqdm seaborn matplotlib jupyter
   ```

2. **Set up API key:**
   ```bash
   # Copy to project root or stage folder
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   # Optionally set BASE_URL for OpenRouter
   ```

3. **Run the notebook:**
   ```bash
   jupyter notebook faq_rag_chatbot.ipynb
   # Execute all cells top-to-bottom
   ```

The notebook will:
- Load 786 Revolut help articles
- Build embeddings and retrieval (numpy, no vector DB)
- Generate 150 synthetic queries (personas × scenarios × modifiers)
- Run queries through RAG
- Judge every answer with 6 binary criteria
- Visualize pass rates

## Repo Structure

```
evals-chatbot/
├── README.md                      # This file
├── .env.example                   # API key template
├── .gitignore                     # Standard ignores
├── 01_rag_baseline/
│   ├── README.md                  # Stage-specific guide
│   ├── faq_rag_chatbot.ipynb     # Full pipeline (EXECUTED)
│   ├── generate_dataset.py       # Synthetic query generation
│   ├── judges.py                  # Binary LLM-as-a-judge functions
│   └── data/
│       ├── revolut_help_articles.jsonl       # Knowledge base (786 articles)
│       ├── synthetic_queries.csv              # Generated queries (150)
│       ├── synthetic_rag_outputs.csv          # RAG outputs
│       └── synthetic_eval_results.csv         # Judge verdicts
├── 02_gepa_optimization/         # Planned
├── 03_skills_experiments/        # Planned
└── 04_simulator/                  # Planned
```

## Key Design Principles

**Clean code:** Flat files, no frameworks, no over-engineering. If a helper is used once, inline it.

**Binary judges:** Each judge returns true/false + reasoning. No 0-5 scores, no weighted composites, no calibration machinery.

**Notebook as source of truth:** All code runs and commits in the notebook, outputs visible in GitHub preview.

**Frozen eval set:** `synthetic_queries.csv` from stage 01 becomes the fixed evaluation set for all future comparisons.

## Stack

- **Embeddings:** OpenAI `text-embedding-3-small`
- **Chat:** Weak model (gpt-3.5-turbo class) — makes failures easier to find
- **Judges:** gpt-4o with structured output
- **Data:** numpy (similarity search), pandas (CSVs), seaborn (plots)
- **All in-memory:** No vector DB, no infrastructure

## Security

See [SECURITY.md](SECURITY.md) for secrets policy, prompt injection surface, and reporting guidelines.

## License

MIT
