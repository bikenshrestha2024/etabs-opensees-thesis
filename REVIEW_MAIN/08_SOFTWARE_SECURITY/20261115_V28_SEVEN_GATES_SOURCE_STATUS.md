# V28 — seven requirements and source evidence scope

Date: 2026-11-15. Base main SHA `d1284fe9a9ee74502b35317dae9bbf20063a396e`.
Status: `TARGETED_ENGINEERING_DATA_INTEGRITY_CORRECTIONS_SEVEN_GLOBAL_GATES_OPEN`.

The starting recursive Git tree contained **2,998 tracked blobs**, not 2,998 semantically reviewed files. Read active `AGENTS.md`, engineering rules, source guides, `components/inputs/output_contract.py`, `components/validation/design_checks.py`, `components/validation/saved_case_identity.py`, quality workflow and focused fixtures. Source fingerprints of inspected active changed code are recorded at `docs/review/ledger/REVIEW_LEDGER_V28_20261115_TARGETED.csv`. No full-repository line-by-line semantic completion is asserted.

## Concrete corrections
- The canonical run-status writer refuses an invalid/misfiled/symlinked run manifest rather than upgrading an unrelated run's status.
- The saved drift reader checks full run identity before treating `COMPLETED_SOLVER_ONLY` as a completed solver case.
- The CSV and MRSM JSON drift import now commits all or none of the rows from each evidence file. Linked drift evidence is rejected.
- A test-only change to the critical V135 completion gate now triggers NLTHA CI via the push file path filter.
- Existing source EDB, authoritative Excel Aw/T1, all original ground motions and M0–M6 geometry, material/reinforcement and source supports remain unchanged.

## Seven requirements
| Requirement | This V28 contribution | Acceptance state |
|---|---|---|
| All tracked files semantic audit | Reviewed selected active code paths, tests, workflow and exact source blobs | **OPEN** — remaining current files and callers unreviewed |
| Complete legacy writer/reader migration | Upgraded one canonical status writer and one saved-design-check reader | **OPEN** — legacy producers/consumers and archive imports remain |
| Interactive Windows GUI regression | Existing Windows headless output contract smoke retained | **OPEN** — no native desktop Tk/ETABS OAPI interaction |
| X-wall first-step instability | No nonlinear material/solver parameters altered; V26 evidence capture retained | **OPEN** — reproduce first-step failure on native source |
| 32/76/97 physical support equivalence | No supports changed | **OPEN** — source restraints, wall mesh and six-DOF reaction comparison |
| ETABS–OpenSees numerical equivalence | Blocks forged or partially corrupt numerical drift proof | **OPEN** — real matching source and numerical benchmark |
| Full-duration nonlinear sensitivity | No native transient run performed | **OPEN** — 224 complete real XY/YX orientation analyses, calibration and sensitivity |

## Structured folder owners
`REVIEW_MAIN/07_ETABS_OPENSEES/` contains the detailed drift gate. `REVIEW_MAIN/08_SOFTWARE_SECURITY/` contains seven-gate summary. `docs/review/ledger/` contains exact source blob/line evidence. `engineering/agent_edits/` identifies tool editor. The selected private ETABS export—not the public GitHub repo—owns native `03_ESM`, `05_MRSM` and other run results, with `RUNS/<STATE>/<CASE>/<RUN_ID>/{00_INPUT_SOURCE,01_LOGS,02_RESULTS,03_EXCEL,04_FIGURES,05_COMPARISONS,06_REVIEW,07_EXPORT_ZIP}`.

No source-code test establishes physical model equivalence, seismic-code acceptance or full-duration transient completion.
