# 01 RAG Baseline — Fintech Support Benchmark

**Business problem:** First-line support RAG for retail fintech. Low-risk queries (payments, transfers, fees) should be answered from KB; high-risk requests (fraud, account takeover, stolen card) must be ESCALATED, never fully resolved by bot. Routing = exactly two actions: **answer** or **escalate**.

**v1 (legacy):** 150 synthetic queries, 6 quality judges, pass rates 59-99%.

**v2 (current):** 355 canonical cases (121 human-designed seeds + 234 controlled variants), routing + safety metrics, provisional fintech-support benchmark.

**Current status:** ⚠️ All labels are provisional (0/355 human-validated). No canonical model run executed yet.

**What it shows:** Complete pipeline from knowledge base → embeddings → retrieval → routing → generation → binary evaluation → safety metrics.

**How to run:** 
1. Copy `.env.example` to `.env` and add your OpenAI API key
2. Run `python validate_dataset.py benchmark/cases.jsonl` to verify dataset structure
3. Run `python run_baseline.py` to execute canonical baseline (cost: ~$15-25 for 355 cases)
4. View results in `faq_rag_chatbot.ipynb` (offline presentation report)

**Key results:** When canonical run completes, this will show routing accuracy, critical escalation recall, and safe resolution rates on 355 canonical cases.
