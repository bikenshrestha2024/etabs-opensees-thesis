# V25 — Independent source hash integrity, writer migration and seven open engineering gates

Date: 2026-11-15. Baseline main SHA: `4e18cb32efcdb38ab110a6bbb4a3a7d3e655f723`.
**Status:** `TARGETED_SOURCE_REPAIRS_COMMITTED_NATIVE_ACCEPTANCE_OPEN`

## Source review scope
The repository currently contains approximately 2,987 Git-tracked blobs. This is a file inventory, not a semantic review of every tracked blob. Exact V25 inspected source functions: `components/validation/saved_case_identity.py::source_model_hash_evidence/identity_screen`, `components/gravity/etabs_reaction_support_filter.py::classify_supports/export_primary_32_comparison`, associated regression tests, source docs and quality CI. Existing `docs/review/ledger` remains the per-version source inspection record. Older V24 source files are not automatically re-certified after edits.

## Confirmed code inconsistencies and fixes
- **V25-01 saved-case provenance (P1):** present but corrupted `00_INPUT_SOURCE/CASE_MANIFEST.json` could be ignored and the payload-only SHA treated as verified. Now returned `invalid_manifest` with source path, and `identity_screen` excludes result under `INVALID_RUN_MANIFEST_EXCLUDED`. A genuinely absent historical manifest remains distinguishable as legacy unverified evidence. A linked manifest is refused. Tests: `tests/test_saved_case_identity_v142.py`.
- **V25-02 physical support flags (P1):** malformed flags were silently skipped during 32-node selection, and nonbinary/text flags could distort selected UZ. Strict six-DOF binary validation now fails closed on *every* source support row. Tests: `tests/verify_primary_32_support_reactions.py`.
- **V25-03 primary 32 report integrity (P1):** repeated ETABS mapping tags overwrote previous evidence; nonfinite original ETABS reactions weren't independently blocked; direct JSON/CSV/XLSX writes could publish incomplete files through linked outputs. Refuse duplicates/nonfinite values; write to the established atomic output APIs and staging XLSX; keep filenames and readers intact. Tests same as above.
- **V25-04 regression coverage (P1):** original primary-32 source/test paths were not in the NLTHA CI path filter or test execution list. Added both.

## Seven requirements: scientific acceptance
| ID | Area | V25 action | Remaining acceptance |
|---|---|---|---|
| G1 | Complete semantic audit | Inspected selected functions, recorded exact blob and ranges | **OPEN:** all remaining current code and historical blobs, caller-reader graphs |
| G2 | Legacy writer/reader migration | One existing primary-32 writer now uses atomic contract and retains legacy names | **OPEN:** every other producer, GUI consumer, ZIP and report importer |
| G3 | Native Windows GUI | Existing Windows-latest headless CI preserved | **OPEN:** interactive desktop ETABS OAPI/Tk scroll/cancel/ZIP/open tests |
| G4 | X-wall first-step failure | Kept original native wall probe diagnostic; no material parameters modified | **OPEN:** native source wall, connected bay and full model failure evidence |
| G5 | 32/76/97 supports | Explicit six-vector source validation; no duplicate/NaN reaction records | **OPEN:** native physical restraints and signed 6-component reactions |
| G6 | ETABS–OpenSees equivalence | Source identity damaged-manifest gate hardened | **OPEN:** matching source geometry, mass, stiffness, loads, periods, ESM/MRSM and drift |
| G7 | 224 full nonlinear orientation analyses | Prior completion/duration gates preserved | **OPEN:** real complete X/Y input, convergence, materials, time-step sensitivity and responses |

CI passing confirms code contracts on synthetic fixtures, **not** physical adequacy. Do not remove original ETABS, Aw/T1 Excel, native solver logs or any previous results. Do not publish source geometry or absolute private paths on this public repository.

## Structured output contract and safe migration
Use the selected export root, the existing `01_ETABS_EXPORT`, `02_MODEL`, `02_GRAVITY`, `03_ESM`, `04_MODAL`, `05_MRSM`, `06_LINEAR_TIME_HISTORY`, `07_NONLINEAR_TIME_HISTORY`, `08_ETABS_COMPARISONS`, `09_SOFTWARE_DIAGNOSTICS`, `90_UPLOAD_PACKAGES`, `REVIEW_MAIN`. New cases adopt `RUNS/STATE/CASE/UTC_RUN/{00_INPUT_SOURCE,01_LOGS,02_RESULTS,03_EXCEL,04_FIGURES,05_COMPARISONS,06_REVIEW,07_EXPORT_ZIP}`. Keep historical `OpenSees_Analysis_Results` read-compatible. Inventory each old writer and downstream reader before any mass migration.
