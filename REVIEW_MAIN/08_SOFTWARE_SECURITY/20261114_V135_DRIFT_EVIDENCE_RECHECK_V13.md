# V135 design drift PASS audit V13 — 2026-11-14

**Observed software defect:** `components/validation/design_checks.py::scan_drift` compares the numeric saved design drift against NBC 105:2025 limits and labels it PASS/FAIL. `run` previously imported that raw status without checking against the active serialized ETABS/OpenSees model SHA or the original numerical run completion status. Thus, a stale, copied, unverified, or interrupted run could appear in the latest V135 `Seismic drift` workbook as PASS. V142's source-screening protections were not previously applied to V135.

## Correction

- A V135 project run now reuses `components.validation.saved_case_identity.identity_screen` to compare source SHA and numeric payload/manifest SHA. A proven conflict is *excluded* with the exact file and reason in `Open items`.
- All remaining rows add `source_identity_status` and `run_completion_status`. A numerical `PASS` is withheld (`NOT EVALUATED`) if source model identity is missing, if there is no corresponding canonical run manifest, or if the saved run is `CREATED`, `RUNNING`, `INTERRUPTED`, `INCOMPLETE` or `FAILED`. The original purely numerical comparison remains in `raw_limit_status` for forensic review.
- The V135 JSON includes `drift_source_mismatch_excluded_count`, `drift_source_unverified_row_count`, and `drift_run_completion_unverified_row_count`.
- A matching source hash and `COMPLETED_SOLVER_ONLY` leave the saved numeric NBC drift-limit result visible as a **saved-result check only**. This *does not* validate ETABS equivalence, correct Rμ/kd scaling, structural strength, P-Delta, member acceptance or full NLTHA record duration.

## Risk/limitations

- Old user-generated drift CSV lacking a source identity/manifest remains available, but may not display a confirmed PASS until it is traced to the exact native model and solved case.
- Failures and out-of-limit responses are not cleared: a numerical FAIL stays visible for conservative review, including when provenance is unverified.
- Run completeness is a source-record claim; independent accepted-time vectors and all required seismic combinations are still needed for a formal structural drift assessment.
- This change is a non-destructive report classification fix; no ETABS `.EDB`, project Excel workbook, source model JSON, load assignment, material parameter or solver algorithm is changed.

**Regression:** `python -m unittest discover -s tests -p 'test_v135_drift_source_completion_v13.py' -v`

**Native Windows checks:** regenerate V135 from updated main, verify actual report path in `09_SOFTWARE_DIAGNOSTICS/DESIGN_CHECKS_V135`, check known source case, unknown historical CSV, incomplete MRSM and mismatched manifest/payload; confirm no invalid numeric pass is promoted.
