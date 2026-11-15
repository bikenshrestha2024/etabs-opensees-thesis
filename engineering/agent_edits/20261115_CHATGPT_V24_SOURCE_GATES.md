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
