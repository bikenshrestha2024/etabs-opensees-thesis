# readiness_dashboard.py — evidence backend

**Code:** [`components/model/readiness_dashboard.py`](../../../../components/model/readiness_dashboard.py)

This module is part of the model-specific, read-only nonlinear readiness tool. It discovers candidate evidence and SHA256 fingerprints or displays the evidence dashboard. It does not modify source ETABS exports, apply material profiles, approve nonlinear analyses or bypass the existing model-bound readiness criteria.

Units are not inferred from filenames. Reviewer claims and actual native solver/experimental validation remain different categories.

**Tests:** `tests/verify_readiness_dashboard.py` checks missing evidence, stale model hash, nonpromotion of candidate files and report export.

**References:** [NBC105 seismic index](https://dudbc.gov.np/pages/24231978/), PEER 2015/12 and [thesis gates](../../../00_THESIS_ACCEPTANCE_GATES.md).

[Module index](../../00_SOURCE_GUIDE_INDEX.md)
