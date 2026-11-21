# NBC 105:2025 engineering acceptance — separate native evidence gate

**Source file:** [components/nbc105/acceptance.py](../../../../components/nbc105/acceptance.py)

**Standards:** NBC 105:2025 §§3.2, 4.1.3.1, 5.1, 5.4, 5.5, 7.3, 7.5, 9.3 and 10. Not a replacement for signed professional review.

**Entrypoint:** `evaluate_project_evidence(evidence,rs_tolerance_fraction=0.001)`, or locally `python -m components.nbc105.acceptance path/to/V107_ACCEPTANCE.json`. The script reads the local JSON only and prints a structured report. Exit 2 means full engineering acceptance remains blocked, which is expected for the current V10.7 data.

**What it can substantiate:** It independently recomputes the relative difference between the two independently named RSX/RSY target and observed shears and checks basic source hash syntax. A matching result receives `NUMERIC_MATCH_REPRODUCED`, not a claim of overall NBC compliance.

**What it cannot substantiate from V10.7 alone:** Verified Rayleigh floor displacements and lesser-of period, coupled-wall stiffness, calibrated effective member stiffness, measured site Vs30, sufficient modal mass and missing-mass correction, ETABS vs OpenSees joint reactions, torsional/edge drift response, the X-wall first-step NLTHA failure or 224 full-duration successful histories.

**Design policy:** Always return overall `BLOCKED_NOT_FULL_ENGINEERING_ACCEPTANCE` from this preliminary evidence screen; a green software test or manually entered `PASS` flag never overrides unresolved native validation. Each open gate includes explicit reason and evidence requirement.

**Tests:** `tests/test_nbc105_engineering_acceptance.py`. No EDB or original private project data is uploaded to GitHub.
