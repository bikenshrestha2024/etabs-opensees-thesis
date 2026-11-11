# Implementation checkpoint — 2026-11-10

Branch: `fix/primary-gravity-seismic-inputs`.
Source commit: `a7e26466c1613fb0db32cee88c322444167d5343` (main).
PR #13 is merged; PR #15 is an open draft with overlapping input-default work.
This branch implements the user's eight follow-up requests incrementally; the
entire V4 architecture migration is not complete.

## Completed changes

- EXTEND existing gravity GUI: 32-node primary default, private source defaults,
  explicit fingerprint-checked saved-case plot action for 32/76/97 results.
- EXTEND existing project workbook reader: SHA256-scoped private source registry;
  original engine's labelled `ETABS Sync` adopted-period outputs are readable.
- EXTEND existing ESM GUI: reuse known EDB/workbook/engine/output directory,
  prefer original matching linked audit over provisional geometric Aw,
  expose adopted periods separately from modal/Rayleigh periods, and include
  solved response-profile images in existing Matplotlib selector.
- EXTEND existing MRSM GUI: current source/state output root for viewers,
  manual full evidence ZIP, source-matched original adopted-period fallback.
- EXTEND gravity recorder: every frame/shell global end-force vector; recovered
  interface Fz and joint vertical force balance in gravity workbook and JSON.
- FIX scorecard lookup: selected run's direct comparison precedes parent root.
- Preserve solver equations, restraints for each selected case, source datasets,
  old scenario identifiers, compatibility imports, and all historical results.

## Executed verification

- Initial focused regression: 39 tests plus 5 subtests passed.
- Static active inventory: 416 modules, no syntax errors, missing canonical
  launchers or missing source guides at execution time.
- Native Tk gravity construction: primary 32 default and both workbook entries
  populated from the local source registry.
- Original linked workbook read: X=2.03856740011866 s,
  Y=1.9219797767063125 s (adopted design periods).
- Native OpenSeesPy 32-node run on an isolated copy: reaction
  311367.31387954945 kN, applied 311367.3138795495 kN,
  maximum downward displacement -0.021017645469009413 m.
  These reproduce supplied saved values. 14262 element vectors recorded,
  11097 joints, largest vertical equilibrium residual 3.97e-10 kN.
- Final broader gravity/ESM/MRSM regression: 197 passed plus 5 subtests.
  Native Tk workbook export succeeded: 26 recovered interfaces and 11097
  joint balances. Offline native-table/32-node reaction comparison workbook
  was also generated. All rerun displacements and support Fz reproduce the
  saved solution exactly (maximum difference 0.0).

## Engineering blockers

Local foundation reactions still differ despite matching global gravity.
Native ETABS auto offsets/rigid factor and the 32-node model's released base
points are not equivalent. The provided beam-force sheet reaches Excel's row
limit; full beam-response coverage cannot be assumed. See the investigation
report. No native ETABS solve, full seismic rerun, stiffness correction or
code/engineering acceptance is claimed.

## Already inspected instructions

User V4 prompt, AGENTS.md, CLAUDE.md, engineering migration/start guide,
CORE_RULES, ENGINEERING_GATES, MODULE_BOUNDARIES, PROVENANCE, AI_ATTRIBUTION,
thesis acceptance/reference registers, active engineering review/canonical run
order, program index, nonlinear NBC implementation guide, and module READMEs.

Next executable engineering action: reconcile actual ETABS end-zone stiffness
and internal base mesh constraints against the preserved 32-node main case;
compare new recovered frame/shell interfaces with native section cuts under
the same load discretization. Do not tune support reactions to fit totals.

Last completed implementation commit: `c6585598d72d480cb42d164868ff7bce154cd890`.
Draft PR: https://github.com/bikenshrestha2024/etabs-opensees-thesis/pull/17
Final source/test state: 197 tests plus 5 subtests passed; native Tk workbook
and offline ETABS reaction-comparison exports completed.

CI follow-up: compilation/navigation and clear-beam workflows passed. The first
quality run found missing reference tags on three public helpers; tags were
added and all four reference-tag tests passed locally. The six new source/force
regressions are now included in the quality workflow.

## User-directed publication follow-up

The user authorized merging the implementation into main, publishing the
supplied Excel workbooks, consolidating workbook paths under excel/, and
using 01.py as the main launcher. 68 workbooks are catalogued; 63 existing
ones retain identical bytes. The 530969448-byte full export uses Git LFS.
Canonical launcher order and portable source/runtime handling were updated.
See EXCEL_AND_LAUNCHER_PUBLICATION_DECISIONS.md for scope, compatibility,
engineering limitations and the explicit publication authorization.

Publication regression: 214 tests and 5 subtests passed; reference tags passed;
419-module static inventory clean; Git LFS object integrity verified locally.


## V4 follow-up checkpoint — 2026-11-11 (draft PR #18)

- **Source:** main `62d4450eccc98126e0489abd352f0c39bcb7d7c1` (newer than draft PR #15 base). Draft PR: https://github.com/bikenshrestha2024/etabs-opensees-thesis/pull/18.
- **Primary selection:** Gravity GUI displays "Primary ETABS-matched set (32 nodes)" by default, but all legacy `ETABS_NONZERO_REACTION_DIAGNOSTIC` scenario IDs, saved-case formats and support nodes are untouched. Individual joint equivalence remains unverified.
- **ESM periods:** Workbook-adopted T1 X/Y now shown immediately beside Aw as read-only labelled values, separately from ETABS measured eigenperiods, OpenSees Rayleigh and computed design-action period. No period value hardcoded or used as a substitute.
- **Main entry:** README, program index and start guides present the existing `01_WORKFLOW_START.py` as canonical. The `01.py` alias and original launcher code are retained byte-for-byte.
- **Regression:** GitHub Actions run `42942405420` passed source compilation and four offline checks: https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/42942405420.
- **No edits:** Original EDB, original workbooks, gravity loads, supports, stiffness, model assembly, analysis algorithms, numerical output files, analysis ZIPs or earthquake records.
- **Next native acceptance gate:** compare ETABS source auto end-offset/rigid factors and actual 32-node base constraints with OpenSees model; reproduce joint 263/264 reaction difference 3041.265778 kN and check joint 718 Uz before any physical correction. Use recovered frame/shell interface and story load audits already in main. Continue with independent modal/ESM/MRSM comparison and source provenance verification.
- **NOT verified by this PR:** Spyder GUI on Windows, ETABS v23 COM run, OpenSees numerical regression, any ETABS-equivalence or code-compliance gate.

## 2026-11-11 — Gravity / ESM / Modal corrective checkpoint

Current source HEAD at start: `d0b9b2e1b2c097081aa9abd7fe42266199e29a69`.
Changes committed directly to `main` in this checkpoint:

- Gravity: `components/gravity/three_case_comparison.py` and GUI action produce an explicitly source-fingerprint-checked comparison of separately solved 32/76/97 support scenarios, with no changed physical restraints. Added synthetic regression test and source guide.
- ESM: `components/equivalent_static/aw_reconciliation.py` and GUI action compare source-EDB-matched original Excel contributions with the separate OpenSees continuous-pier diagnostic. They intentionally reject unmatched EDBs and do not claim wall-by-wall equivalence where identifiers are missing. Label ETABS-linked workbook plots separately from solved OpenSees response plots.
- Modal: `components/modal/rayleigh_ledger_audit.py` and `components/modal/rayleigh.py` check unique/exported diaphragm coverage, independently reconstruct Rayleigh quotient X/Y, and record numeric audit terms. Preserve V123 compatibility.
- Compare: `components/validation/etabs_comparison.py` reports empty solved-response evidence instead of presenting a blank table as zero response.
- Source guides and [REF] annotations added for new modules and existing untagged LFS/native-gravity audit modules.
- Fixed ESM GUI literal newline escape regression found by CI at `28f02159`, corrected at `393ccdc4`.

### Engineering acceptance NOT established

- 32-primary support reactions globally balance ETABS, but local mapped reaction/stiffness/load-path differences remain. Native ETABS 6DOF restraint/edge-mesh/1,367 rigid-offset evidence is required.
- Original Excel X Aw approx 1.95829363 m² versus continuous-pier geometric X approx 1.93063712 m²; Y approx 2.20308033 m² in both. No common first-storey wall-ID and opening mapping yet proves the exact source of X difference.
- Native solved ETABS ESM/MRSM story shear, drift, displacement, reaction and mass/stiffness equivalence not demonstrated. An Excel worksheet and applied floor-force diagram are NOT solved structural response data.
- Preliminary Rayleigh solver still needs full ETABS mass-bearing level inventory, physical stiffness, centre-of-mass, and torsion checks; matching exported diaphragm tags alone is insufficient.
- Windows ETABS v23/OpenSeesPy actual-model numerical and GUI verification not executed in Linux CI; separately run ULS and SLS and preserve evidence.

### Next reproducible engineering check

1. On the source-matched model, complete separate gravity cases 32/76/97; click **Compare solved 32 / 76 / 97 + Excel**, then run native six-DOF support/end-offset preflight and map the largest per-joint errors.
2. In the ESM GUI, run ETABS-linked original Excel (same verified EDB), then **Audit Excel vs continuous-pier Aw**; inspect source registers and identify actual opening/pier physical IDs before changing any Aw calculation.
3. For X and Y and each ULS/SLS stiffness state, run all-storey Rayleigh and matching native ETABS modal/MRSM response cases; compare only same-case, same-unit, same-model results using the current comparison GUI.
4. Review status from GitHub Actions for the newest commit. A syntax/documentation CI pass is not full ETABS-equivalence acceptance.

Preserve all original source EDB, original Excel workbooks, old launchers, native records, results ZIPs and prior output paths. No structural model changes were performed in this checkpoint.

## 2026-11-11 — organized evidence export extension (no legacy output migration)

A separate method-oriented **snapshot publisher** is now available in
`components/ui/organized_results.py`. New Gravity, ESM and MRSM GUI buttons
create dated `Organized_Results/<timestamp>/` folder snapshots with
`Gravity/`, `ESM/`, `Modal/`, `MRSM/`, `Comparisons/`, and
`Unclassified/` folders, per-method `*_Review_UPLOAD.zip` files,
`ALL_MODULES_Review_UPLOAD.zip`, `EVIDENCE_MANIFEST.json`, and
`LATEST_ORGANIZED_RESULT.txt` at the snapshot parent level.

This is intentionally **not** an in-place rename of active solver folders:
historical JSON indices, runner output paths, response viewers and downstream
scripts still read the original locations; new category folders contain
SHA256-verified copies. It does not attempt to merge unrelated model/state
runs, include `.EDB` contents in ZIP, or invent SLS/native ETABS responses.

Non-native regression: `tests/test_organized_results.py`. GitHub Actions
NLTHA Python quality workflow run `42968205156` completed successfully,
including this test, on commit `934f8779`. Windows ETABS v23 GUI end-to-end
and large model integration are still pending.

The saved MRSM screenshots from 11:01 AM show six ULS cases complete with
gravity and sparse eigen-analysis, but SLS result panels blank (SLS was not
run); the ETABS comparison table has unpaired OpenSees-only responses and
the deformation graphic is a CQC envelope illustration, not a physical
time-history animation. These require further data and UI tests independent
of folder organization.
