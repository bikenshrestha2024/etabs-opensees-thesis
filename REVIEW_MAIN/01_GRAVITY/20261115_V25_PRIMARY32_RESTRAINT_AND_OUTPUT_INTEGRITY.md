# V25 — Primary 32 support definition, signed reaction export and path integrity

Date: 2026-11-15. Baseline main SHA: `4e18cb32efcdb38ab110a6bbb4a3a7d3e655f723`.
**Engineering acceptance:** `SOURCE_EVIDENCE_HARDENED_NATIVE_32_76_97_EQUIVALENCE_OPEN`

## Findings verified by source reading
1. `components/gravity/etabs_reaction_support_filter.py::classify_supports()` previously formed `original_fixed` by skipping entries whose DOF array was not length six. A corrupted source flag record was silently absent from the audit. `bool("0")` can also wrongly treat a text "0" UZ flag as restrained. V25 requires exactly six literal 0/1/bool flags for **every source record**, refusing malformed restraints before filtering.
2. `export_primary_32_comparison()` previously constructed a dictionary from selected ETABS node mappings, silently overwriting a repeated tag. It now rejects duplicates. Nonfinite source ETABS FZ and nonfinite reactions/totals block publication.
3. JSON, CSV and Excel were previously written directly to final filenames, and the output directory could be a symlink. V25 retains all three original filenames and schema but routes JSON/CSV through the shared staged contract, uses an atomic staged XLSX replacement and refuses linked destination directories and linked output files.

## Regression / source identity
- `tests/verify_primary_32_support_reactions.py`: malformed six-DOF flags, duplicate mappings, nonfinite ETABS FZ, linked report directory and existing conventional 32-node synthetic comparison.
- `.github/workflows/nltha-quality.yml` now triggers on both primary-32 selector and its tests, and executes the verifier in the ordinary Python-quality suite.
- No actual source EDB, Excel workbook, soil C accelerogram or physical restraints were modified.

## Mandatory native evidence to close 32/76/97
Retain separately the independently verified physical 32 original base locations, 76 source restraint positions and 97 continuous wall-base diagnostic. Do not substitute a zero ETABS reaction for a verified free DOF. Source input must include native CSI GetRestraint six vectors, DOF axes, original/canonical point names and XYZ, generated shell edge connectivity, geometry/stiffness and load ledger, solver convergence, signed six-component foundation reactions including moments, source EDB fingerprint and reviewer-approved tolerance for identical quantities. Record independent 32/76/97 source and result SHA plus wall/slab-frame transfer evidence. Do not mark equivalent from these synthetic tests alone.

## Output structure
For newly migrated gravity runs use `<SELECTED_LOCAL_EXPORT>/02_GRAVITY/RUNS/<STATE>/<CASE>/<UTC_RUN>/{00_INPUT_SOURCE,01_LOGS,02_RESULTS,03_EXCEL,04_FIGURES,05_COMPARISONS,06_REVIEW,07_EXPORT_ZIP}`. Existing 32-support report filenames remain unchanged until the GUI reader migration has been individually verified. Store comparison review under `REVIEW_MAIN/01_GRAVITY`, no local private data in public GitHub.
