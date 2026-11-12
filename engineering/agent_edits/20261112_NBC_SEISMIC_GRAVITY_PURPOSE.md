# 2026-11-12 — NBC load case purpose and profile audit

**Editor:** ChatGPT/GPT-6 via authenticated GitHub connector.  
**Base main at branch creation:** `3a768928a9fdb68cb810dc563f38dc74613e14fc`.  
**User correction:** gravity-only comparison has 100% dead, 100% other/storage live and 100% roof live. The seismic history uses NBC 105:2025 §5.2/Table 5-1 dead=100%, storage live=60%, other live=30%, roof live=0%.

**Why:** compare the 286,419.758 kN Kobe seismic preload only to equivalent ETABS seismic pattern factors, and the 311,367.314 kN 1.0D+1.0L gravity comparison only to ETABS full-gravity factor case. Distinct sums are not by themselves an error.

**What changed:** Pure case-purpose factor audit in `components/model/load_case_purpose.py`; assembly adds structured `[LOAD CASE PURPOSE]` and detailed pattern warnings to existing logs, preserving physical loads; source ledger has independent storage-live column; tests and CI; numbered `07_REVIEW_MAIN` reference and 5W1H docs; corrected previous review notes.

**What was not changed:** EDB and input spreadsheets, input earthquake motions, built model/nodal masses, strength or P-Delta factors, support selection, solver or time-step settings, previously completed Kobe histories, materials and acceptance logic. No structural model was rebuilt on Windows.

**Who reviews:** thesis operator verifies ETABS pattern classification and actual occupancy, qualified earthquake engineer checks governing Clause 5.2 and any applicable gravity preload clauses, software maintainer checks source/test conformance.

**Status:** Code checks / offline tests, not independent ETABS mass, gravity or all-story equivalence. No automatic code acceptance or material sign-off.
