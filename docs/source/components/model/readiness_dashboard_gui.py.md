# readiness_dashboard_gui.py — project review UI

**Code:** [`components/model/readiness_dashboard_gui.py`](../../../../components/model/readiness_dashboard_gui.py)

This module is part of the model-specific, read-only nonlinear readiness tool. It discovers candidate evidence and SHA256 fingerprints or displays the evidence dashboard. It does not modify source ETABS exports, apply material profiles, approve nonlinear analyses or bypass the existing model-bound readiness criteria.

Units are not inferred from filenames. Reviewer claims and actual native solver/experimental validation remain different categories.

**Tests:** `tests/verify_readiness_dashboard.py` checks missing evidence, stale model hash, nonpromotion of candidate files and report export.

**References:** [NBC105 seismic index](https://dudbc.gov.np/pages/24231978/), PEER 2015/12 and [thesis gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module index](../../00_SOURCE_GUIDE_INDEX.md)

## 2026-11-12 responsive evidence refresh

**What:** audit work is moved off Tk's single UI thread. **When:** opening dashboard, changing project/model or clicking Refresh evidence. **Why:** repeated hashing of evidence files can pause scrolling and interactions.

**How:** worker thread performs `audit()` on captured folder/model string inputs; a 100-ms GUI-thread polling callback applies the result. Each refresh increments a request ID and discards results from older scans, preventing stale model evidence being shown after changing projects. Tk widgets are never accessed from workers. The old evidence is cleared while a scan is in progress; Export refuses to save an incomplete/stale report.

**Where:** `components/model/readiness_dashboard_gui.py`; state remains in this window. **Which:** source model hash, twelve review workstreams, evidence SHA and review status. **Who:** UI maintainer verifies responsiveness; structural engineer approves actual source evidence.

**Limitations:** no cancellation of an already-started disk hash (stale results are discarded). No native Windows/Tk benchmark has been performed; solver performance is unchanged by this UI implementation. No model/material approval is automated.
