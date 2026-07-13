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
