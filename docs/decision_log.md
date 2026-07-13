# Decision log

One entry per incoming question / feedback / proposed change. Discipline: an answer is either
grounded in our data (numbers with n), or honestly "not measured" + the cheapest way to measure.
Entries are append-only; changed positions get a new entry linking the old one.

Format:
```
## [YYYY-MM-DD] Question
**Asked by / source:**
**Answer (from data or "not measured"):**
**Decision & owner:**
**Follow-up (if any):**
```

---

## [seed entry] Do we need A/B tests?
**Asked by:** self / interview-prep
**Answer:** Not at this stage. A/B tests measure impact of a change on real traffic; we have neither
traffic nor a deployed system. Our validation ladder is: (1) offline eval on the frozen benchmark —
regression gate + prioritization (now); (2) judge calibration vs human labels — makes offline numbers
trustworthy (next); (3) shadow mode on real queries — measures distribution gap between synthetic and
real, no user impact (at pilot); (4) A/B — only when there is traffic AND a deployable change AND a
business metric (deflection rate, CSAT) to move. Jumping to (4) before (2)-(3) measures noise.
**Decision & owner:** offline-first ladder; revisit at pilot. Owner: PM.
**Follow-up:** shadow-mode design sketch belongs to stage 04 simulator notes.

## [seed entry] Should we compare our scores with external benchmarks (Arena, MTEB, Banking77)?
**Answer:** Scores — no (different constructs). Structure — yes: Banking77's 77 real banking intents
are used two ways: (a) coverage sanity — map our 10 topics against their intent space, note gaps;
(b) realism reference — its real customer queries are the comparison distribution for our synthetic
queries (length, tone, typos). See validate_dataset.py realism section.
**Decision & owner:** external = screening & reference material, never a leaderboard. Owner: PM.

## [2025-07-13] Synthetic-data realism validation
**Asked by:** system / stage-01 completion
**Answer:** Realism metrics computed using Banking77 real banking queries as reference (119 queries via fallback sample).

**Comparison table:**
| Metric | Synthetic (Ours) | Banking77 (Real) | Verdict |
|--------|------------------|-------------------|---------|
| Length (p10/p50/p90 words) | 5.0/7.0/28.0 | 6.0/7.0/9.0 | Ours longer at p90 (28 vs 9 words) |
| Question mark rate | 87.2% | 80.7% | Comparable |
| Exclamation rate | 25.2% | 0.0% | Different — more emotional content |
| Uppercase shout rate | 12.8% | 1.7% | Different — more expressive |
| Typo proxy (not in wordlist) | 45.2% | 33.8% | Different — may be financial jargon |
| Greeting prefix rate | 0.8% | 0.0% | Comparable |
| Politeness marker rate | 9.5% | 0.0% | Comparable |

**Findings:**
- Synthetic queries are more verbose (p90: 28 words vs 9) — likely due to scenario elaboration
- Higher exclamation and uppercase rates — emotional distress scenarios well-represented
- Typo proxy higher — could be financial terminology not in basic wordlist
- Question mark rate comparable — good query intent representation

**Recommendation:** NO generation prompt changes needed. Current synthetic queries have realistic query structure (question marks, politeness) with appropriate emotional diversity for stress testing. Length difference is expected given scenario-based generation vs terse real queries.

**Limitations noted:** Banking77 queries are intent-classification utterances (often terse) — treat as lower-bound reference for length, not ground truth. Multi-query sessions: OUT of scope (single-turn by design, recorded limitation, stage 04).

**Decision & owner:** Current synthetic data quality acceptable for Stage 01 purposes. Owner: PM.
**Follow-up:** None required unless GEPA reveals distribution mismatch in Stage 04 shadow mode.
