# 2026-11-23 — Postconversion NBC105 ESM workflow, provenance and efficiency review

## Scope and read-first preflight

Reviewed the screenshots and pasted ESM GUI log provided on 2026-11-23;
current active GitHub sources `components/equivalent_static/calculation_and_gui.py`,
`organized_exports.py`, `components/modal/rayleigh.py`, matching source guides,
output-layout and saved-evidence tests. Git starting HEAD:
`3a81ec8cf3581e39d7387afa16821df1aa0d2e36` on `main`.

Read: `AGENTS.md`,
`engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`,
`.agents/skills/etabs-opensees-read-first/SKILL.md`,
`CORE_RULES.md`, `ENGINEERING_GATES.md`, and governing-code matrix.
No private native EDB, 2026-11-23 ESM ZIP, ETABS case output, live Windows GUI,
source model SHA, workbook SHA or full OpenSees solver traces were available to
this review. **This is a bounded software/source audit, NOT native engineering
acceptance or a line-by-line repository-wide audit.**

- PHYSICAL FOUNDATION: 32 actual supported source joints; 44 additional
  wall mesh points, which must retain correct edge/MPC load transfer.
- GRAVITY BENCHMARK: full 1.0D + 1.0L.
- SEISMIC WEIGHT: NBC 105:2025 §5.2/Table 5-1, distinct from full gravity.
- CURRENT GEOMETRY: two 12-m X walls with openings; three 6-m Y walls.
- ESM source/code decisions: NBC 105:2025; project-specific IS exceptions
  are separately recorded and not made generic ESM rules.
- SOURCE IDs/HASHES: unavailable; no numerical parity or source identity claim.

## Observations directly from the provided run

| Observation | Reported value / evidence | Interpretation |
| --- | --- | --- |
| Effective X wall index | Aw-X = 2.07317452 m² | New grouped-wall geometry **reviewed**, not code accepted |
| Effective Y wall index | Aw-Y = 2.20308033 m² | Needs original section / opening audit |
| Site reference | Kirtipur, Soil C, Z=0.35 | Vs30 missing, >40m soil classification NOT VERIFIED |
| ULS X equivalent base shear | 29,849.619 kN, k=1.6016 | Comparison-only ULS applied force |
| ULS Y equivalent base shear | 26,450.735 kN, k=1.7110 | Comparison-only ULS applied force |
| Script generation | 12 runners, six per axis | Generating scripts is not running solvers |
| Case execution | no 12-case saved status/response supplied | Native OpenSees response NOT VERIFIED |
| Calculation file root | 03_ESM/RUNS/ULS/<case> | Canonical calculation writer |
| Auto review ZIP root | OpenSees_Analysis_Results/<case>/07_EXPORT_ZIP | Distinct legacy GUI output/packaging root |
| Approximate calculation/export duration | 9–10s per direction | Not evidence of 12 full-model solves |

Changing only `E+`, `E-`, `E0` while preserving earthquake-direction
polarity leaves `V` unchanged. It changes applied `Mz = ±0.05b F`, so
inherent/accidental torsion should instead be compared in solved displacement,
edge drift, forces, reactions and rotational response. Independently verify
perpendicular `b_X` and `b_Y` from the model; do not infer them from the
same default entry.

### Gate 1: code applicability and site

NBC 105:2025 §3.2.1 permits ESM for SLS generally but restricts ULS ESM
to the published height, period or regularity conditions. The ~95m
source building fails the logged ULS method screen and is **COMPARISON ONLY**.
NBC §4.1.3.1 requires Vs30 at >40m. Choosing "Soil C" does not replace
native geotechnical Vs30 evidence. The GUI correctly warns about both;
future dashboard must show them independently from process success.

### Gate 2: output-path split — targeted source patch

Before patch, `_exact_calculation_roots(legacy_case_root)` located
`03_ESM/RUNS/<state>/<identical_case_name>`, but `_source_files`
copied only its `NBC105_ESM_Calculation_*.json` and
`NBC105_ESM_Storey_Forces_*.csv`. All other stage-owned outputs
including generated `.py`, plots, solver response files and recorder
indexes were missed by the combined manifest. `_latest_batch_status`
expected only runner scripts in the legacy selected directory, not the
canonical case directory even though `CASE_STATUS.json` can be saved
to legacy. That can cause `PARTIAL_OR_FAILED` for an actually successful
batch.

**This patch:** enumerate all recognized, copy-only, case-level artifacts
from exact canonical sibling; validate status against runner filenames from
both directories. It does **not** recursively pull neighboring model variants
or change active output destinations. The ZIP and workbook remain new immutable
snapshots and no historical source file is moved or rewritten. Source SHA
equivalence is **not inferred from a matching basename**. Tests use synthetic
fixtures and never touch private ETABS data.

### Gate 3: runner generation vs structural execution

`ESMGui._calculate` generates X/Y force tables and 12 runner scripts, then
may start an automatic review ZIP before running OpenSees. Separately,
`_run_generated` creates fresh child processes, reconstructs the model,
applies initial checks, performs static analysis, validates saved evidence and
records `CASE_STATUS.json`. The GUI should never describe
`Calculate + export` as a completed solver batch.

Suggested next UI statuses:

- `INPUTS_CHECKED` — source and field consistency only
- `PERIOD_CALCULATED` — ULS/SLS matched Rayleigh result
- `FORCES_EXPORTED` — 12 case load files generated, **0/12 solved**
- `SOLVER_RUNNING` — N/12 with current case/time/log
- `SOLVER_PARTIAL` / `SOLVER_COMPLETE_ONLY` — exact status and runner SHA check
- `ETABS_COMPARISON_PENDING` / `ENGINEERING_ACCEPTANCE_PENDING`

Use explicit Run ID, model SHA, case SHA, limit state and report purpose as
status identity. Avoid a single undifferentiated green 'FINISHED'.

### Gate 4: reviewer ZIP and source provenance

`_auto_bundle_seismic_review` currently receives
`Path(self.outdir.get())` and executes after **force export** and after a
solver batch. That can build a pre-solver archive in a different root from
stage-owned calculations. Future patch should pin packaging to an immutable
per-run manifest with explicit `force_only` / `solved_response` purpose
and independently recorded missing required files. Its auto-publishing
should not be interpreted as proof of 12 completed cases.

The existing batch status SHA is not an executed-runner SHA. Two distinct
runner generations can use the same filename. Future status must store
`sha256(executed_script)`, source-model SHA, output JSON SHA and case config;
reject stale `CASE_STATUS` from a regenerated runner even if the name matches.

### Gate 5: model/mass/supports and physical parity

Source ledger and master-node/story tag agreement does not guarantee ETABS
source dead/live weight equivalence or solver mass operator equivalence.
Require each category D/Storage L/Other L/Roof L participation, `ΣWi`,
`W`, floor COM and inertia, and distributed vs lumped mass differences.
The 32 actual supports/44 wall mesh points must stay connected through
native edge/constraint transfer: do not fix 44 additional nodes or force-match
joint reactions. Record six-component common-cut results, incremental
reaction vectors, mismatch norms and global equilibrium separately.

Current saved gravity residuals involve distinct archived models and do not
prove the ESM current source was matched. Do not update physical constants or
promote these ESM comparison forces into final MRSM / NLTHA acceptance.

### Gate 6: numerical consistency to investigate using actual ZIP

Audit source-matched inputs for both directional cases:

`EDB SHA; workbook SHA/cells; model variant; stiffness state; Aw pier grouping;
Vs30; Rmu; Omega_u/Omega_s; Ch(T); Rayleigh and adopted T; W; Cd(T); k; Fi;
sum(Fi)-V; Mz; true support reactions; signed eccentricity; drift at both
floor ends; native ETABS force/deformation comparisons.`

The current X base shear is higher than some historical ETABS ESM/scaling
references; **do not call it a calculation defect** until same-source `W`,
`Cd`, stiffness state and period selection are proven. The independently
reported Y value alone is not a validation of the X/Y mass split.

## Next changes — ordered by correctness and efficiency

1. **P0** Keep the new exact canonical/legacy reader regression in CI.
2. **P0** Unified run-manifest owner passed to force writer, solver status,
   auto ZIP and consolidated Excel. Add source file hashes and forbid stale
   runner/CASE_STATUS identity; no state or model-variant mixing.
3. **P0** Saved native comparisons: full D+L, Table 5-1 W, source supports
   and 32-support six-component foundation cuts; no fabricated parity.
4. **P1** Separate `Calculate`, `Run`, `Review` statuses and show 0/12
   versus 12/12. Enable 'Complete Review ZIP' only for a status-tagged
   snapshot, otherwise export `FORCE_ONLY` archive explicitly.
5. **P1** Display Rayleigh and adopted T for X/Y side by side, with the
   matching ULS/SLS source fingerprint, empirical cap and status.
6. **P1** Derive orthogonal plan dimension `b` from verified footprint and
   report both ±5% moments; audit inherent torsion separately.
7. **P2** Avoid regenerating identical period/Ch/Cd/W/Fi physics six times
   per axis, but keep unique polarity/eccentricity `Mz` and solved responses.
   Cache verified source hashes and generate shared force/plot data once;
   keep individual scripts and independent fresh OpenSees domains.
8. **P2** Compact GUI to a stepwise page (Inputs → Periods → Cases → Solver
   → Comparison → Exports). Scrollbars, copyable log, contextual review
   warnings and responsive cancellation; no hidden acceptance gates.

## Verification status (this review)

- Source-targeted patch and synthetic regression: staged in a PR branch;
  test result must be checked against GitHub Actions before claiming PASS.
- Native Windows UI: NOT RUN.
- 2026-11-23 private ZIP and source EDB: NOT INSPECTED.
- ETABS/OpenSees numerical parity: NOT VERIFIED.
- NBC 105 project compliance, Vs30, high-rise ULS ESM: NOT ACCEPTED.
- No physics calculations, material/geometry/mass changes or source-file
  relabeling were introduced by the targeted export fix.
