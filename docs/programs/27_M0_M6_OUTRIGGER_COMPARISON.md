# Stage 06 — controlled M0–M6 seismic response comparisons

Once all seven model variations have complete experimental and numerical input validation, use 27_COMPARE_OUTRIGGERS.py with M0_M6_Comparison_Manifest.json. The manifest must list one entry per variant M0–M6, source geometry/mass/record-settings SHA256 invariants, distinct model export SHA, outrigger floor lists, and paths to explicit case summary JSON files.

Every case summary must identify pair_id, ULS/SLS, XY/YX, record SHA, finite full-duration evidence and comparable peak metrics. The comparator rejects missing pairs, partial runs, inconsistent input hashes and missing sources. It computes only numerical maximum reductions relative to M0; it never calls a design or device acceptance.

**Not yet supplied:** Seven independently reconstructed ETABS exports with actual M0–M6 geometry/devices, at least three paired motions for ULS and SLS, full-converged bidirectional Kobe and others, and reviewed component calibration. The research-only comparison will fail closed until these exist.

Reference: NBC 105:2025 Section 9.3.2.1; Korkmaz & Kircil (2026), DOI 10.3390/buildings16040711. Do not transfer published FVD reduction percentages.

Additional integrity gate: every case summary must contain a matching variant_id and the exact source model SHA-256 specified for that variant in the manifest. Cross-assignment of M2 results to M4 is blocked even when motions match.
