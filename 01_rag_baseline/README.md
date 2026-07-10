# 01 RAG Baseline

Minimal single-turn RAG chatbot evaluated end-to-end on synthetic data with LLM-as-a-judge metrics.

**What it shows:** Complete pipeline from knowledge base → embeddings → retrieval → generation → binary evaluation → pass rate visualization.

**How to run:** 
1. Copy `.env.example` to `.env` and add your OpenAI/OpenRouter API key
2. Run `jupyter notebook faq_rag_chatbot.ipynb` and execute all cells top-to-bottom
3. Or generate data separately: `python generate_dataset.py`

**Key result:** Baseline pass rates across 6 binary judges (relevancy, conciseness, helpfulness, correctness, legal compliance, redirects) on 150 synthetic queries, showing which dimensions fail most and where GEPA optimization (stage 02) should focus.
