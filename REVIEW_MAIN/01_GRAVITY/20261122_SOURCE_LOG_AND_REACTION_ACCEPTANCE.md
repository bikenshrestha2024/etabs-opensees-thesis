# 2026-11-22 Gravity export and reaction acceptance audit

## Scope and evidence provenance

Reviewed the user-supplied `ETABS_Conversion_Worker(1).log` (2026-11-22
08:12:36–08:13:30 Asia/Kathmandu) and active source in
`components/gravity/gui_and_reports.py`,
`components/inputs/etabs_table_bundle.py`,
`components/validation/etabs_split_beam_forces.py`, and the November 20
gravity reaction reconstruction. Attached ZIP contents were **not** parsed
in this execution environment. No native ETABS or OpenSees process was run.

## Source conversion findings

| Log statement | Evidence and consequence |
|---|---|
| Source EDB digest | `3f1f039722ae77c39eb000a93b3ad2ec1b8f5f87b41fc8ffc6f297c85ea449f1`; require same digest for the *actual* analyzed comparison EDB |
| `Cannot open ... .Y_` | ETABS ancillary-buffer warning while opening a working EDB copy; OpenFile later returned OK, but do not assume linked analysis results were complete without a native solve |
| API inventory | 1,101 points, 1,367 frames, 725 areas, zero links; 55 frames have no non-empty section assignment, to classify as intended null/none or unexpected |
| Area load query | Reports zero direct area-object assignments while 350 areas / 1,050 expanded load-set components exist; these are distinct source representations, prevent duplicate or missing load application |
| Support setting | 76 base nodes fixed in six DOFs; **no** 32/76/97 solver result shown |
| Mesh and segments | 10,400 ShellMITC4 cells, 3,862 frame segments; export only, no gravity point-force acceptance |
| Storey gravity | 286,419.758231 kN and near-zero *internal ledger* residual; this may represent configured gravity/seismic preload, **not** the 1D+1L native benchmark of 311,367.313880 kN |
| Deferred outputs | `FORMULA_XLSX=DEFERRED`; CSV/JSON gravity ledger available; avoid claiming a completed formula workbook |
| Completion gate | `EXPORT_COMPLETED_REVIEW_REQUIRED`, `analysis_ready_reported=false`, `model_equivalence=NOT_VERIFIED` |

### Native 32/76/97 scenario gate

A conversion run with one fixed-support topology is **not** three solved
gravity cases. Mark each of 32, 76, 97 separately as RUN_VERIFIED only when
that case includes: solver success flag, exact source EDB/config digests,
full support identity and DOF restraints, applied DL/LL/roof load profile,
sum of six DOF reactions, per-node coordinates and reactions, comparison
point mapping, and a matching native ETABS analyzed output. Otherwise
status is NOT_RUN, FAILED or EVIDENCE_INCOMPLETE.

For 32 primary reaction-bearing nodes, current best published project
comparison still has max absolute vertical point discrepancy 768.045 kN
and sum absolute discrepancy 10,072.106 kN. It is NOT a pass. The original
76 fixed-node problem is compounded by 44 shell-only base positions with
nontrivial OpenSees support reaction but zero ETABS point-object FZ.
The 97-node case changes support topology and is diagnostic.

### Required root-cause tests (not yet performed here)

1. Validate native ETABS object and analytical element restraints, auto
   edge constraints, and original wall and floor auto-mesh connectivity.
2. Compare physical wall-base cut F3/M1/M2 and column-base resultants
   from both programs, about a common origin, without using nodal
   reaction attribution as a surrogate for wall internal force transfer.
3. Compare beam-end and intermediate forces via source unique frame
   IDs, member local axes and stations, offset faces and segment mapping
   from the **entire** user-selected beam-force workbook set.
4. Repeat isolated dead and live patterns and compare region-specific
   loading, shell-edge stiffness, offsets, and in-plane wall modifiers.
5. Only propagate ACCEPTED source-identical elastic model state to
   downstream ESM/MRSM/TH/NLTHA workflows after numerical tolerance
   requirements and source identity checks are demonstrated.

## Folder ownership and immutability

Current GUI beam-force stage:
`01_ETABS_EXPORT/03_BEAM_FORCES/RUNS/<timestamp>/` containing
`ETABS_Beam_Forces_Consolidated.csv` and
`ETABS_Beam_Forces_Manifest.json`.
One canonical private registry:
`01_ETABS_EXPORT/00_MANIFEST/PROJECT_SOURCES.private.json`.
The original XLSX inputs are read-only and must remain outside public git.
The registry contains absolute private paths and is not intended for upload.
Gravity solver outputs and native reaction comparisons remain under their
existing gravity-module run directories, never intermingled with the
beam-force source-only audit.

## Current pass/fail

- GUI multi-select and beam-source consolidation integration: CODE COMMITTED.
- GUI static AST regression: CODE COMMITTED, not executed here.
- ZIP line-by-line review: BLOCKED — inaccessible archive contents.
- Native 32/76/97 analysis: NOT RUN IN THIS SESSION.
- Reaction equivalence: FAIL/NOT VERIFIED.
- Full repository line-by-line semantic audit: NOT COMPLETE.

Do not close this engineering blocker based on code commit or export success.
