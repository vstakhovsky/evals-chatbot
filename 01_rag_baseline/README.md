# 01 RAG Baseline — Fintech Support Benchmark

**Business problem:** First-line support RAG for retail fintech. Low-risk queries (payments, transfers, fees) should be answered from KB; high-risk requests (fraud, account takeover, stolen card) must be ESCALATED, never fully resolved by bot. Routing = exactly two actions: **answer** or **escalate**.

**v1 (legacy)**: 150 synthetic queries, 6 quality judges, pass rates 59-99%.  
**v2 (current)**: 133 human-designed seeds + variant generation (planned), routing + safety metrics, validated fintech-support benchmark.

**What it shows:** Complete pipeline from knowledge base → embeddings → retrieval → generation → binary evaluation → pass rate visualization.

**How to run:** 
1. Copy `.env.example` to `.env` and add your OpenAI/OpenRouter API key
2. Run `jupyter notebook faq_rag_chatbot.ipynb` and execute all cells top-to-bottom
3. Generate data: `python generate_dataset.py`
4. Verify seeds: `python verify_seeds.py`

**Key result:** Baseline pass rates across 6 binary judges (relevancy, conciseness, helpfulness, correctness, legal compliance, redirects) on 150 synthetic queries, showing which dimensions fail most and where GEPA optimization (stage 02) should focus.
