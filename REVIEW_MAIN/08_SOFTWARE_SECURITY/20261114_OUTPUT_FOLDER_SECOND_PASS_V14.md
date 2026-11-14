# Second-pass folder and output ownership audit — 2026-11-14

**Scope:** Current `main` live source reviewed for output-layout ownership. Changes made on a review branch, not a claim of physical ETABS/OpenSees equivalence. **No source EDB or Excel workbook moved or modified.**

## Confirmed source inconsistencies and corrections

1. `components/inputs/folder_audit.py` used **only** `STAGE_FOLDERS` to define accepted top-level directories. It mistakenly flagged legitimate `02_MODEL`, `08_ETABS_COMPARISONS`, `09_SOFTWARE_DIAGNOSTICS`, `90_UPLOAD_PACKAGES`, `00_SOURCE_MANIFEST`, and `REVIEW_MAIN` as unexpected. The auditor now uses the shared `AUXILIARY_FOLDERS` registry and established project-manifest/review folders; legacy run roots are accepted as compatibility.
2. The auditor did not distinguish **loose files at canonical stage roots** from files within per-case runs. Its JSON/Markdown now includes an immediate-child `loose_stage_outputs` inventory with explicit `LOOSE_STAGE_OUTPUTS` findings. This is **inventory only** and cannot safely infer a destination by basename alone.
3. The newly introduced NBC settings exporter wrote .json and .xlsx directly into `09_SOFTWARE_DIAGNOSTICS/ANALYSIS_SETTINGS`. New exports now use `09_SOFTWARE_DIAGNOSTICS/ANALYSIS_SETTINGS/RUNS/<timestamp>/JSON/` and `.../EXCEL/`, a single run owning both files.
4. Top-level `DESIGN_CHECKS_V135.md` still instructed readers to look under the old `OpenSees_Analysis_Results/Design_Checks_V135`. Instructions now distinguish the actual **new writer** path `09_SOFTWARE_DIAGNOSTICS/DESIGN_CHECKS_V135` from legacy input/evidence compatibility.
5. Added tests for false unexpected-directory alarms, loose-stage detection and paired settings audit run directories.

## Canonical destination registry

| Stage | Destination | Ownership |
|---|---|---|
| Import/conversion | `01_ETABS_EXPORT` | classified source audit, mapping and origin manifest copies |
| Gravity | `02_GRAVITY` | native gravity runs, independent foundation and load path comparisons |
| Model/mesh | `02_MODEL` | slab mesh configurations, section model building and source snapshot |
| ESM | `03_ESM` | comparison-only cases where NBC eligibility is not met |
| Modal | `04_MODAL` | eigen, mass participation and mode shape |
| MRSM | `05_MRSM` | spectrum/CQC/forces/drift and code scaling |
| Linear time-history | `06_LINEAR_TIME_HISTORY` | paired motion runs and linear output |
| Nonlinear time-history | `07_NONLINEAR_TIME_HISTORY` | sensitivity runs, material tests and history |
| ETABS comparisons | `08_ETABS_COMPARISONS` | independently matched native cross-solver responses |
| Diagnostics | `09_SOFTWARE_DIAGNOSTICS` | NBC settings, V135 design-check review, migration checks and warnings |
| Upload packages | `90_UPLOAD_PACKAGES` | upload-ready manifest + ZIP snapshots, no original EDB |
| Engineering review | `REVIEW_MAIN` | issue-level decisions and limitations |

Suggested new case structure for a writer that has a complete producer/reader migration: `<STAGE>/RUNS/<case_or_timestamp>/00_INPUT_SOURCE, 01_LOGS, 02_JSON, 03_EXCEL, 04_PLOTS, 05_ZIP`. **Do not create empty fake solver results; no "PASS" inferred from files or folder names.**

## Important incomplete migration

The shared registry exists, but active legacy writers, readers, GUI browse controls and saved scripts may still produce `OpenSees_Analysis_Results/<state>/<model>` and export-root files. The non-destructive `09_ORGANIZE_ETABS_EXPORT.py` mirrors eligible source files into `01_ETABS_EXPORT` and retains originals because several model builders still resolve flat source names. This is **not** a completed cutover.

Safe migration order: (1) inventory live writers and readers; (2) select exact case identity (source EDB SHA, assembly/config SHA, solver state, mesh, supports and case name); (3) modify one writer and every consuming reader together; (4) run tests plus Windows-native paired cases; (5) retain immutable old results and compatibility lookup; (6) only then retire old write paths. No automatic bulk move, silent rename or overwritten duplicate evidence.

## Practical validation

Run `python -m unittest tests.test_folder_audit tests.test_output_layout tests.test_nbc_settings_panel_v12 -v` from an updated checkout. On the Windows export folder run `python 22_AUDIT_EXPORT_FOLDERS.py "D:\\Thesis Opensees\\ETABS 11-14-2026\\3"`; this writes locally under `01_ETABS_EXPORT/00_MANIFEST/FOLDER_AUDITS`. Generated report includes local paths and must **not** be published to public GitHub.

No structural input, native solver, 32/76/97-node reaction comparison, or MESH_04/08/16 evidence has been altered or certified by this organization pass.
