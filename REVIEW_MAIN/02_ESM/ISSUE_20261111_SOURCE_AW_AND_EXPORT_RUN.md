# P0 — ESM export runner, Aw source, and comparison readiness

Status: OPEN_HIGH. ESM finished 12/12 cases for one ULS comparison run but the interface reportedly stalled on another attempt.

## Observations
- ESM log: Excel SCALING SUMMARY B14 Aw-X=1.9582936 m2, B15 Aw-Y=2.2030803 m2; candidate workbook B4 references a distinct SERVICE EDB; this is *not* verified to be the selected ULS source EDB.
- OpenSees continuous-pier diagnostic: Aw-X=1.9306371191 m2; Aw-Y=2.2030803324 m2. X gap=0.0276564809 m2 (~1.4123% of adopted Excel X).
- Screenshot: 12 of 12 ESM exported runners eventually succeeded, indicating one completed batch; an earlier hang needs process-status logs to reproduce.
- Uploaded ESM review package: `Comparisons/ETABS_Comparison_V148/run.json` reports `row_count=0`, `etabs_file=""`, `direct_api=false`, `evidence_verified=false`, without exclusions. This is a missing comparison source, NOT zero physical response.

## Engineering judgment
Preserve spreadsheet-calculated Aw as an explicit project research reference **only when it belongs to the current source EDB and is supported by source hashes**. Do not substitute geometry diagnostic. ULS high-rise ESM is labeled comparison-only by the supplied program; do not promote its solver convergence to NBC code acceptance. Require independent core openings and first-storey effective pier classification.

## Required fixes
1. Spawn generated runner scripts as cancellable subprocesses, one case at a time, with PID, start/end, rolling stdout, stderr, return code, elapsed time, and last stage in a progress table; do not run model loops on Tk main thread.
2. Detect stale or missing runner scripts and Windows Python interpreter mismatch; never show `RUNNING` indefinitely after child exit.
3. Make `Re-run failed only`, `Cancel`, `Open output folder`, and `Copy log` explicit controls.
4. After successful case finish, index saved response rows separately by source SHA256/ULS-SLS/direction/eccentricity and report comparison readiness. Don't reuse stale response rows.
5. Export a single read-only discrepancy manifest under `REVIEW_MAIN/02_ESM/<case-id>` in the selected local output root, not into the public source tree.

No ESM runner or source-calculator code changed by this review issue.
