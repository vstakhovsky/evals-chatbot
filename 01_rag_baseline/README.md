# 01 RAG Baseline

Minimal single-turn RAG chatbot evaluated end-to-end on synthetic data with LLM-as-a-judge metrics.

**What it shows:** Complete pipeline from knowledge base → embeddings → retrieval → generation → binary evaluation → pass rate visualization.

**How to run:** 
1. Copy `.env.example` to `.env` and add your OpenAI/OpenRouter API key
2. Run `jupyter notebook faq_rag_chatbot.ipynb` and execute all cells top-to-bottom
3. Or generate data separately: `python generate_dataset.py`

**Key result:** Baseline pass rates across 6 binary judges (relevancy, conciseness, helpfulness, correctness, legal compliance, redirects) on 150 synthetic queries, showing which dimensions fail most and where GEPA optimization (stage 02) should focus.

### Pass Rates (150 queries evaluated)

| Judge | Pass Rate | Notes |
|-------|-----------|-------|
| **Legally Correct** | 99.3% | ✅ Safe content, minimal issues |
| **Helpful** | 90.0% | ✅ Provides actionable guidance |
| **Relevancy** | 89.3% | ✅ Answers address user issues |
| **No False Information** | 88.0% | ✅ Mostly grounded in context |
| **Not Excessive** | 76.7% | ⚠️ Some answers contain unnecessary detail |
| **Redirects When Unknown** | 59.3% | ❌ **WEAKEST**: Bot guesses instead of admitting unknowns |

**Main takeaway:** The baseline RAG system struggles most with **redirects when unknown** (59.3% pass) — when context lacks the answer, it frequently guesses or invents information rather than admitting ignorance and redirecting to Help Center. This is the primary failure mode for GEPA optimization to address in stage 02.
