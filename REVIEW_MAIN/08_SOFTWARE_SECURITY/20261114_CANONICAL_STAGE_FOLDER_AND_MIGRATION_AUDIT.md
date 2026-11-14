# One-case / one-stage output organization — review 2026-11-14

## Objective and constraints

The selected ETABS export root is the single owner of subsequent analysis evidence. Every stage must keep its own active runs, inputs, logs, results, figures, and review packages. Existing flat source files and legacy analysis-result directories **must not be moved** until each Python importer, GUI callback, worker, case index, ZIP publisher and comparison reader has passed a native regression test against the replacement path.

The categorizer creates **byte-for-byte copies** and a manifest. It does not move originals, read confidential engineering contents into GitHub, or prove physical ETABS/OpenSees agreement.

## Expected folder taxonomy

```text
<SELECTED_ETABS_EXPORT_CASE>/
├── 01_ETABS_EXPORT/
│   ├── 00_MANIFEST/                 # stage index + local FOLDER_AUDITS
│   ├── 01_SOURCE/                   # exported source identities, model ledgers
│   ├── 02_MAPPING/                  # ETABS unique ID to OpenSees IDs
│   ├── 03_LOADS/                    # gravity/seismic source pattern ledgers
│   ├── 04_VISUALIZATION/            # 3D/plan/ID lookup HTML
│   ├── 05_AUDITS/                   # export properties, loads, actions
│   ├── 06_CONFIG/                   # reviewed model configuration
│   ├── 07_LOGS/                     # export/build logs
│   ├── 08_PROCESSING/               # exported runnable model code
│   └── 09_REVIEW/                   # unresolved import/equivalence notes
├── 02_GRAVITY/
│   ├── RUNS/<model-case>/<support-case-or-timestamp>/
│   └── REVIEW_SNAPSHOTS/<timestamp>/
├── 03_ESM/
│   ├── RUNS/<ULS-or-SLS>/<X-or-Y>/<eccentricity>/<timestamp>/
│   └── REVIEW_SNAPSHOTS/<timestamp>/
├── 04_MODAL/
│   ├── RUNS/<ULS-or-SLS>/<timestamp>/
│   └── REVIEW_SNAPSHOTS/<timestamp>/
├── 05_MRSM/
│   ├── RUNS/<ULS-or-SLS>/<X-or-Y>/<eccentricity>/<timestamp>/
│   └── REVIEW_SNAPSHOTS/<timestamp>/
├── 06_LINEAR_TIME_HISTORY/
│   ├── RUNS/<state>/<record>/<XY-or-YX>/<timestamp>/
│   └── REVIEW_SNAPSHOTS/<timestamp>/
├── 07_NONLINEAR_TIME_HISTORY/
│   ├── RUNS/<M0-to-M6>/<record>/<XY-or-YX>/<timestamp>/
│   └── REVIEW_SNAPSHOTS/<timestamp>/
└── OpenSees_Analysis_Results/       # HISTORICAL LEGACY: retain/read only
```

**Important:** This is a *target taxonomy*, not a claim that every stage's solver currently writes these exact nesting levels. At present, new GUI gravity cases from legacy path selections route to `02_GRAVITY/RUNS/<model-case>`, while existing old gravity analyses and other consumers retain their historical paths. Migration of other stage run writers/readers is still open. Actual case directory labels must follow stable source IDs plus source-model/state hashes; timestamps alone are not sufficient for comparing analyses.

## Run-folder contract (target)

Every completed analysis **should** eventually own:
- `00_INPUT_SOURCE/` — immutable source hash, units, model-state config and case IDs
- `01_LOGS/` — full solver log, timing, traceback, convergence, cancellation
- `02_RESULTS/` — numerical CSV/JSON/HDF5 as applicable; no silently substituted data
- `03_EXCEL/` — user-readable analysis/reconciliation spreadsheets
- `04_FIGURES/` — consistent 2D/3D plots, original source tags and solver tags
- `05_COMPARISONS/` — ETABS-specific source-matched results, with missing vs verified labels
- `06_REVIEW/` — unresolved discrepancies, engineering judgment, conditions of use
- `07_EXPORT_ZIP/` — one compact manifest-backed upload package

This is a design contract requiring stage-by-stage testing, **not yet a live automatic writer behavior**.

## Folder audits (implemented)

Use `python 22_AUDIT_EXPORT_FOLDERS.py "<export_case>"` to produce JSON and Markdown under `01_ETABS_EXPORT/00_MANIFEST/FOLDER_AUDITS/`. It will list:

1. all currently loose flat top-level source filenames and copies missing from the categorized mirror;
2. categorized-copy hash conflicts (no overwrite);
3. explicit processing sidecars excluded from mirroring;
4. existing legacy analysis-case folders and unexpected top-level directories;
5. actual per-stage folders/subfolders and loose files, without claiming that their presence proves a solver run or NBC compliance.

Use `--mirror` for byte-identical categorized copies first. If an existing copy differs, the command fails without overwriting it. Large files can make hashing costly; `--skip-hash` is available for inventory-only runs and must not be considered provenance verified. Report data stays LOCAL (contains actual absolute paths, including possibly confidential names). Do not add a local report to the public Git repository.

## Reconcile before any move

| Priority | Module | Present risk / requirement | Gate |
|---|---|---|---|
| P0 | ETABS export | flat source files still used by active importers; transient processing sidecars create clutter | enumerate consumers, verify copy hashes, then dual-path reader tests |
| P0 | Gravity | correct total reactions do not establish 32/76/97 point reaction equivalence | native support-DOF, wall-base, mesh, load-path comparison |
| P1 | ESM | old all-module result files may coexist with stage-specific snapshots | preserve adopted Aw/period source; identity-matched result scanners |
| P1 | Modal & MRSM | named stage folders do not verify modal/CQC or drift results | verify model SHA, mass, stiffness, response, and source-matched base shear |
| P1 | Linear and nonlinear histories | results can be in legacy folders with differing model basis | preserve complete record/step status, case and motion fingerprints, fail-closed acceptance |
| P1 | V142/design review | blank drift plot previously confused missing records with zero drift | search canonical + legacy; log missing responses and verify ULS/SLS case IDs |
| P2 | GUI/results/ZIP | output selectors/registries may assume legacy flat locations | test each Windows GUI button, cache, export manifest and historical reopen before migration |

## Acceptance evidence

- Unit and source audit: `python -m unittest discover -s tests -p "test_folder_audit.py" -v`.
- Existing folder-layout regression: `python -m unittest discover -s tests -p "test_output_layout.py" -v`.
- Mirror regression: `python -m pytest tests/test_export_mirror.py` if pytest is installed.
- Native Windows end-to-end model runs **still required**; Python filesystem tests are not physical equivalence evidence.
- No automatic cleanup of the 32/76/97-node records, SHA-identified EDB/Excel originals, raw solver results, or historical `Saved_Project_V156` references.

## Source governance

Project engineering conventions: `AGENTS.md`, `KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK/`, `REVIEW_MAIN/README.md`, `components/inputs/output_layout.py`. NBC 105:2025 governs seismic actions and seismic acceptance; **folder numbering is a software/provenance policy**, not a code clause. The required project-adopted conventional slab flexural stiffness remains 0.25 Ig / 0.35 Ig per IS 16700:2023 Table 5 (project setting, not an NBC prescription). Any physical section modifier requires generated solver-command evidence before model equivalence is accepted.
