# 2026-11-12 — Knowledge architecture and responsive readiness GUI

**Editor:** ChatGPT (GPT-6) through authenticated GitHub connector. **Branch:** `review/20261112-knowledge-ui-responsive`. **Base main:** `805844241f9ca873f90056c3f8c3c84df4366f79`.

## WHAT and WHY

Add an explicit six-question-plus-inputs/owner knowledge base, retain canonical folder ownership and improve Tk readiness refresh responsiveness. Existing architecture guidelines forbid mass moves of active code without import/output-reader migration.

## WHEN / WHERE / HOW

2026-11-12, exact changed modules: `components/model/readiness_dashboard_gui.py`, `components/model/readiness_dashboard.py`, `tests/verify_readiness_dashboard.py`; documentation and static navigation under `KNOWLEDGE_BASE/`; code reference audit in `tools/audit_knowledge_map.py` and its test; repository CI and README links.

GUI fix moves expensive read-only evidence audit hashing to a worker thread, with all widget changes marshaled to Tk, stale-result discarding and visible progress. Backend caches each SHA within a single refresh only. Engineering statuses and model-bound review remain unchanged.

## WHICH inputs / WHO verifies

No source EDB, private PDFs, workbook, ground motions, materials or native analysis inputs were read or changed by this PR. Documentation refers to existing repo-relative canonical files. Software reviewer confirms import/navigation and responsiveness; structural reviewer separately confirms engineering results. No human review/approval inferred.

## Validation and limits

Unit tests added for hash reuse and knowledge-card completeness. Repository CI must pass before merge. GUI responsiveness on the user's actual Windows/Spyder environment and native 25-storey OpenSees speed **NOT MEASURED**. First-step wall X failure remains unresolved; no M0–M6 run acceptance implied.

No file relocations, deletions, source-interface changes, or private model data in this public change.
