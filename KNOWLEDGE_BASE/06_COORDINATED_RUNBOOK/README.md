# 06 — Coordinated thesis operations: source → verified analysis → reported evidence

**Updated:** 2026-11-13. **Status:** procedural guidance; not a structural design certificate.
**Governing seismic code:** **NBC 105:2025 for the complete thesis seismic workflow**. **Two deliberately adopted IS 16700:2023 exceptions only:** **COMPULSORY initial EQ P-Delta cases** §7.2(d) and **REQUIRED** conventional RC slab flexural stiffness (Table 5: strength 0.25 Ig; serviceability 0.35 Ig). All remaining IS references are labelled *supplementary verification, never NBC replacement*; 2025 BIS amendment text pending. Read the **[mandatory governing-code and exceptions matrix](NBC105_GOVERNING_CODE_MATRIX.md)** and [amendment tracker](../../LITERATURE/Codes_Standards/IS16700_2023_AMENDMENT_TRACKER.md).

This guide **extends** existing [run order](../../00_READ_FIRST_RUN_ORDER.md), [workflow cards](../01_WORKFLOWS/WORKFLOW_CARDS.csv), [launcher index](../../docs/programs/00_PROGRAM_INDEX.md), [engineering gates](../../docs/00_THESIS_ACCEPTANCE_GATES.md), [canonical review register](../../REVIEW_MAIN/README.md), and [AGENTS.md](../../AGENTS.md). It does not rename entry points, relocate historical outputs, change solver physics or duplicate their implementation.

**Searchable engineering explanations and recorded questions:** [REVIEW_MAIN/09_ENGINEERING_QA](../../REVIEW_MAIN/09_ENGINEERING_QA/README.md) (governing code, gravity/mass, initial P-Delta, ETABS/OpenSees tangent stiffness and dynamic handoff). See also [the detailed static-EL versus NLTHA-start explanation](../../REVIEW_MAIN/09_ENGINEERING_QA/02_PDELTA_INITIAL_STATES/01_SIGNED_EL_VS_GRAVITY_START.md).

## Code precedence and exceptions

The explicit case-by-case selection and load-case firewall are in [NBC 105 governing-code matrix](NBC105_GOVERNING_CODE_MATRIX.md). No IS 16700 seismic combination, spectrum, ESM, MRSM, elastic TH or nonlinear TH procedure may replace NBC 105:2025. Treat the **compulsory** IS initial P-Delta combinations as independently converged X±/Y± cases using NBC seismic-coefficient EL before P-Delta enabled linear/nonlinear TH; no-P-Delta / zero-initial branch is a **control only** and cannot be accepted as NBC-compliant. Verify initial-state transfer without static EL + dynamic acceleration double counting; keep §5.2 gravity in the analysis. See [P0 transfer review](../../REVIEW_MAIN/00_MODEL/20261113_NBC_IS_INITIAL_PDELTA_CODE_HIERARCHY.md).

## Exactly one accountable flow

| Stage | What / why | When / entry point | How / which evidence and pass condition | Where / who |
|---|---|---|---|---|
| 01 Source | Freeze the exact ETABS EDB/export and original workbooks; do not compare wrong model vintages | Every new source EDB, before any new build; use the existing import launcher indexed in `docs/programs/00_PROGRAM_INDEX.md` | Model SHA256, EDB path identity, object/tag map, units, 3D topology, load-pattern ledger, unsupported-action report; hard stop if untraced | Private input; provenance manifest; **operator**, independently checked by **structural reviewer** |
| 02 Model | Build reproducible frame, slab, wall and diaphragm mechanics and their model objects | After 01 and for **each** mesh or material change | ETABS→OpenSees IDs, section properties, beam/column and beam/wall end offsets, wall openings, gap-free connectivity, support DOFs, floor shell load distribution; create distinct `MESH_04`, `MESH_08`, `MESH_16` configurations, rebuild and solve each; never equate formula workbook with solved load path | `02_MODEL/SLAB_LOAD_PATH` in selected export; **operator**, model-review **engineer** |
| 03 Gravity | Verify vertical load paths and isolate mass from load-case purpose | After model assembly; before dynamics | Separate `GRAVITY_1.0D_1.0L`, documented transient preload, and NBC seismic-weight ledger (dead 100%; storage 60%; other live 30%; roof live 0% where supported by occupancy/source). Compare equivalent ETABS and OpenSees load definitions only; total, story, individual reactions, joints, mesh sensitivity, displacement | `REVIEW_MAIN/01_GRAVITY`; **structural reviewer** |
| 04 Modal | Establish valid physical modes and dynamic mass participation | After gravity/state + stiffness freeze; for ULS and SLS where required | Eigen convergence, mode shape X/Y/Rz, effective modal mass, matched ETABS mode, full eigenperiod versus *code-adopted period* recorded separately | `REVIEW_MAIN/03_MODAL`; **numerical reviewer** |
| 05 ESM | Generate **comparison only** when ESM is ineligible for this high-rise | After source seismic weights, soil and periods documented | X/Y Aw and adopted periods with source workbook cells/hashes; shear and story forces; applicability/soil Vs30/eccentricity; explicit comparative-only watermark, no design-acceptance label | `REVIEW_MAIN/02_ESM`; **code reviewer** |
| 06 MRSM | Obtain elastic modal-response checks with correct CQC and scaling interpretation | After modal | ULS/SLS matched model, modal participation, force-only scaling vs displacement/drift, X/Y/torsion, floor-edge drift, ETABS independent result alignment | `REVIEW_MAIN/04_MRSM`; **structural reviewer** |
| 07 Linear TH | Diagnose input, damping and elastic runtime without silently changing dt | After gravity/modal/records validated | Input hashes, paired XY/YX, units applied once, complete 4094-step type checks as applicable, actual native `analyze()` vs recorder profiling, same-mesh baseline/optimized identical histories | `REVIEW_MAIN/05_LINEAR_TH`; **numerical reviewer** |
| 08 Components | Validate nonlinear RC frame, 3D perforated wall, FVD, BRB behavior before building NLTHA | Before full nonlinear suite, not after it | Project reinforcement mapping, confinement, single-element cyclic experiments, force–displacement/velocity/energy, identified test specimen, objective error, sensitivity and transfer limits; published card ≠ calibrated building | `LITERATURE/`, `REVIEW_MAIN/06_NONLINEAR_TH`; **materials reviewer** |
| 09 NLTHA | Execute only qualified, full-duration M0–M6 XY/YX variants and interpret 3D responses | After G00–G06 gates pass; failing X-wall first step remains blocker | ZERO/X/Y/XY fresh-domain triage, dt, all accepted finite states, consistent earthquakes/site/spectral matching, full response history and case-by-case status; M0–M6 differences only in controlled outrigger/device configuration; no truncated trial as completed suite | `REVIEW_MAIN/06_NONLINEAR_TH`; **researcher + earthquake engineer** |
| 10 Evidence | Preserve enough information to reproduce or challenge every result | Every step and release | Independent source/model hash, solver version, environment, exact script/parameters, logs, rejection cause, accepted steps, raw response, derived Excel, charts and complete zip manifest; signoffs never inferred | `REVIEW_MAIN` and private run output; **maintainer + reviewer** |

The numbered **workflows remain the canonical module numbering**. This 01–10 table is a dependency and handoff checklist, not a second launch menu.

## Required run metadata — WHAT / WHEN / WHY / HOW / WHERE / WHICH / WHO

Each execution's private `RUN_MANIFEST.json` should have:
```json
{
  "schema": "THESIS_RUN_MANIFEST_V1",
  "case_id": "ULS_KOBE_XY_M0_MESH_04",
  "what": "analysis and physical scope",
  "when": {"started_at": null, "finished_at": null},
  "why": "engineering question and gate being tested",
  "how": {"script": null, "git_sha": null, "python_version": null, "opensees_version": null, "solver": null, "dt_seconds": null, "accepted_steps": null},
  "where": {"private_evidence_root": null, "review_register": "REVIEW_MAIN"},
  "which": {"edb_sha256": null, "assembled_model_sha256": null, "load_profile": null, "stiffness_state": null, "mesh_subdivisions": null, "record_sha256": null, "code_references": []},
  "who": {"operator_role": "RESEARCHER", "independent_reviewer": "NOT_ASSIGNED"},
  "status": "NOT_STARTED",
  "review_status": "NOT_VERIFIED"
}
```
These are **schema examples, not actual project case results**. Private roots, user names and identifying personal paths must be excluded/redacted from public Git commits and review ZIPs.

### Evidence release rules

* `PREPARED`: input/config ready, **not** a native solve.
* `RUNNING`: process active, show accepted steps/stage and *cancel requested* separately.
* `COMPLETED_NUMERICALLY`: all requested accepted steps, finite output, expected record duration and independent run checks; **not** ETABS equivalence.
* `FAILED`, `CANCELLED`, `TRUNCATED_DIAGNOSTIC`: retain failed time, original traceback, contaminated post-failure files and diagnostic flags.
* `ETABS_OPENSEES_MATCHED`, `COMPONENT_EXPERIMENT_VALIDATED`, `CODE_ACCEPTED`: separate review outcomes requiring their own evidence and signoff.
* GUI tasks use background subprocesses (never block Tk main loop), scrollable log, elapsed/wall-time and case progress; stop terminates the solver process safely and preserves partial evidence. No false global percent/ETA where adaptive nonlinear solve makes that unknowable.

## Research and change-control rhythm

1. **At source intake:** check code edition and amendments, specimen geometry, exact DOI/date/license, parameters and unit system. Keep full PDFs privately; commit only copyright-safe metadata/links.
2. **Before each run:** run deterministic preflight tests and enforce source identity, loading, physics and code-eligibility gates. Keep an immutable original ETABS EDB and Excel calculation.
3. **During a run:** collect actual live status and native solver timing; flush manifests safely. On error, preserve raw state; debug with a new domain, never resume from CSV.
4. **After a run:** generate per-run `json/`, `excel/`, `csv/`, `figures/`, `logs/`, `review/` and `zip/` subfolders **within the isolated result case**, with exact model/case/mesh IDs in filenames. Preserve pre-existing outputs and compatibility routes; do not bulk-move or delete historical source evidence.
5. **Weekly / before thesis chapter revision:** refresh official code status and paper DOIs, record retrieval date and amendment state, run citation/path scans, reconcile all open `REVIEW_MAIN` tickets and prioritize P0 blocking physics over UI polish. Use a pull request for nontrivial changes; CI passing is code integrity, not seismic acceptance.

## Highest-priority unresolved gates on 2026-11-13

- **P0:** nonfinite first-step X core-wall NLTHA failure; project wall material/reinforcement and element mapping remain unqualified.
- **P0:** independent ETABS/OpenSees gravity-load paths: 32/76/97 supports, beam-column and beam-wall joint offset/volume accounting, mesh refinement 4/8/16; compare matched gravity purposes.
- **P1:** NBC soil-class evidence (Vs30 for high-rise), wall effective stiffness, ULS/SLS state identity and adopted-vs-eigen periods.
- **P1:** verify the content of BIS **Amendment No. 1 (2025)** to IS 16700:2023 before citing an affected provision as current.
- **P2:** native solver performance, GUI consistency and upload packages; no optimization may change accepted physics without response equivalence tests.

## Source identity and bibliography

- [NBC 105:2025 — official DUDBC publication](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf)
- [BIS standard details: IS 16700:2023 and Amendment No. 1 (2025)](https://standards.bis.gov.in/website/standard-details)
- [OpenSeesPy ShellMITC4](https://openseespydoc.readthedocs.io/en/latest/src/ShellMITC4.html)
- [Official OpenSees rigidDiaphragm](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/mp_constraint/rigidDiaphragm.html)
- [Current curated references](../../docs/00_RESEARCH_REFERENCES.md) / [literature metadata and permission policy](../../LITERATURE/README.md)

**Qualification:** This guide has not run native ETABS/OpenSees, and its gate definitions do not silently change existing program code.
