# V24 editor provenance

- Date: 2026-11-15.
- Target branch: `main` in `bikenshrestha2024/etabs-opensees-thesis`.
- Editor: ChatGPT (OpenAI); model family GPT-6.
- Base SHA: `68f9b5a959965d4b761a525781a0e694b77d2623`.
- Primary changed source: `components/validation/etabs_equivalence_report.py`, `components/nonlinear_time_history/variant_comparison.py`, `tools/audit_soil_c_case_completion.py`.
- Regression: `tests/verify_etabs_direct_equivalence.py`, `tests/verify_variant_comparison.py`, `tests/verify_soil_c_case_completion.py`.
- Audit classification: semantic inspection of **named functions**, not all repository files; targeted improvements to source integrity and numerical screening.
- Tools: connected GitHub repository API, GitHub Actions; native ETABS/Windows GUI/OpenSees solver not available in this environment.
- Strictly preserved: original EDB, original Aw/T1 Excel, 32/76/97 independent physical restraints, material calibration gate and original ground-motion records.
- Source modification does not count as native model acceptance. Existing uncommitted external local data were not accessed.

## Supplementary V24 reader fix

- `components/validation/case_review.py::collect` source and `tests/test_case_review_canonical_output.py`: recover safely from damaged or nonfinite saved profile, drift and deformation evidence; preserve legacy reader output paths and model SHA checks.
- Per-file inspected line range recorded in `docs/review/ledger/REVIEW_LEDGER_V24_20261115_TARGETED.csv` with source blob ID.
- Native Windows GUI remains unexecuted; no originally generated results were overwritten or moved.

- Additional saved-result publisher inspection: `components/validation/case_review.py::export` and corresponding regression now enforce non-linked report directories and atomic XLSX replacement without moving legacy GUI paths. Blob SHA and inspected ranges recorded in dated ledger.
