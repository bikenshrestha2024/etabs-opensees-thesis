# Native MRSM results and nonlinear readiness

Editor: Codex. Base: `5cfc420` (GitHub main, PR #124).

- Extended the existing ETABS comparison loader to discover run-bound native reference CSVs with matching EDB and CSV SHA-256 values. Reference rows retain their native case and basis. Case equivalence requires separate review.
- Bound approval for the generated nonlinear builder to the model script, model configuration including FSAM assignments, and configured nonlinear material file. CI now exercises readiness and ETABS ingest tests.
- Verified 84 test cases and 21 subtests on Windows. Native ETABS ran the two spectrum cases on a verified working copy. Native Tk loaded 102 ETABS values and opened the 16-item model-bound readiness editor.
- The native test covered spectrum analysis and the readiness GUI. Production NLTHA, project material and device calibration, and native conversion-ingestion validation remain open. Project results and absolute paths are held locally.
