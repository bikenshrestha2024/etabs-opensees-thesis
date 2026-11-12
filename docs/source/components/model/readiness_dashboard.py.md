# readiness_dashboard.py — evidence backend

**Code:** [`components/model/readiness_dashboard.py`](../../../../components/model/readiness_dashboard.py)

This module is part of the model-specific, read-only nonlinear readiness tool. It discovers candidate evidence and SHA256 fingerprints or displays the evidence dashboard. It does not modify source ETABS exports, apply material profiles, approve nonlinear analyses or bypass the existing model-bound readiness criteria.

Units are not inferred from filenames. Reviewer claims and actual native solver/experimental validation remain different categories.

**Tests:** `tests/verify_readiness_dashboard.py` checks missing evidence, stale model hash, nonpromotion of candidate files and report export.

**References:** [NBC105 seismic index](https://dudbc.gov.np/pages/24231978/), PEER 2015/12 and [thesis gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module index](../../00_SOURCE_GUIDE_INDEX.md)

## 2026-11-12 per-audit hash reuse

**What:** within one refresh, the same evidence file is hashed once even if multiple workstreams require it. **When:** `audit(root, model)` computes file fingerprints. **Why:** reduce redundant file reads and runtime without changing physical evidence.

**How:** local `Path.resolve()`→SHA-256 dictionary, discarded at the end of each audit; each new refresh computes new hashes. Verified with `tests/verify_readiness_dashboard.py::test_duplicate_evidence_is_hashed_once_per_audit`.

**Where:** `components/model/readiness_dashboard.py`. **Which:** only evidence files in allowed project locations; no new source discovery and no change to code acceptance. **Who:** software maintainer validates hash correctness and reviewer validates source identity.

**Limitation:** like any snapshot, a file modified while being hashed may invalidate project identity; don't change evidence during signed analysis.
