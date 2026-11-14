# Gravity 2026-11-14 10:37–10:57 — source evidence and unresolved node reactions

**Engineering state: NOT VALIDATED / REVIEW REQUIRED.** Based on the user's uploaded GUI screenshots, full timestamped 2382-line pasted log, MESH_04 workbook metadata and attached review packages. Uploaded ZIP contents could not be independently traversed by the current runtime; this document does not claim to inspect every file within the ZIP or execute the ETABS/OpenSees models.

## Native comparison / numbers
- Source EDB copied and opened in a private ETABS instance without saving; the compare log identifies `WORKING_COPY_ANALYZED_FROM_SOURCE_EDB`. Independently verify source SHA against rebuilt source when running production.
- Identical 1.0D+1.0L case applied = `311367.31387955` kN; ETABS base FZ = `311367.31387954` kN. OpenSees 32 support Rz = `311367.31387955` kN; global equilibrium is near machine precision. This only proves whole-model force balance.
- 2026-11-14 10:45:38: OpenSees `ETABS_SOURCE_SUPPORTS` 76-node case solved with Rz `311367.313880` kN; `CONTINUOUS_WALL_BASE_FIXED` 97-node case solved at the identical Rz. Both PASS refers to solver equilibrium, not per-node equivalence.
- Direct ETABS comparison at 10:48:50 is **the selected 32-node solution only**: 32 coordinate matches, 44 unmatched ETABS supports, axes verified, zero ambiguous. Node36 (ETABS 263, x12/y6/z0) ETABS `14748.522205506191` kN versus OpenSees `17789.787978010492` kN, ETABS minus OpenSees = `-3041.265772504301` kN; node41 (ETABS 264, x12/y12/z0) has the symmetric discrepancy. Nodes 8,13,64,69 show approximately -1725.174 kN each; nodes42 and35 approximately +1583.722 kN. Errors cancel in the global sum.
- Log repeatedly flags `44 ETABS zero-Rz points have nonzero OpenSees source support reactions` in 76-source audit; some ZIP manifests simultaneously report 76 source reactions *unverified* because they reference a selected 32-node run. Do not merge these mismatched run identities into one accepted comparison.

## Most likely physical causes, ranked hypotheses (not proven)
1. **Source ETABS wall-base auto-mesh/edge constraints and boundary-condition semantics** vs 32 selected reaction points, 76 original supports, 97 supplemental wall-base fixities. A zero reaction does not prove freedom; zero-load supports may be restrained. Compare all 6 source DOFs and actual shell-footprint coupling.
2. **ShellMITC4 wall-to-column/beam shared nodes, line constraints and condensation**. Confirm slab-to-frame and wall-to-frame common edge node or exact multi-point constraint operators, 3D shell local orientation and no duplicate/missing elements.
3. **Effective wall and frame stiffness mismatch**: model report indicates gross in-plane wall stiffness, while NBC Table 3-1 values are design modelling references; ETABS assigned modifiers must be verified before changing OpenSees. Cracked section assumption changes load distribution without changing total weight.
4. **Frame/braces offsets and end-release stiffness**, including pinned braces with torsional `J=0` idealization, rigid ends and coupling beam representation. Compare individual source frame forces and source local axes before changing topology.
5. **Distributed load application differences**: report source patterns in OpenSees: Self Weight 201267.3138795 kN, Floor Finish 18000 kN, Partition 18000 kN, Wall 26100 kN, Live 48000 kN. Same sum does not prove same spatial nodal loads or moment resultants; inspect first/second moments for each pattern and local tributaries.
6. **Object self-weight overlap**: potential geometry overlap `19358.5274517` kN and separate beam-end candidate `8652.4443516` kN are mutually exclusive diagnostic hypotheses, not corrections. Source quantity audit states 750 beam weights and source total matching. Do not subtract either potential mass blindly.

## Minimal credible experiment sequence
A. Fix model provenance: exact ETABS EDB copy hash, original ETABS workbook hash, OpenSees rebuilt source hash, DOF and units, identical 1D+1L cases. Compare 76-source supports before 32 and 97 diagnostic modes; do not conflate run paths.
B. Extract source reactions at all 76 ETABS restrained nodes, and solver reactions at the exact mapped 76 nodes from the **same** model state. Set ETABS-local vs global axis flags explicit; point coordinate checksum.
C. Make a 76-by-6 restraint comparison plus shared-node geometry and 3D wall-base stiffness mapping. Include master/slave constraints and ETABS auto meshing.
D. Inspect the spatial gravity load ledger and signed resultant moments for every source pattern; beam, wall and floor per-object weights; shell/wall and frame end actions.
E. Run isolated axial brace, beam-with-hinge, slab-to-beam patch, shell-wall-base, and wall opening/coupling beam benchmarks. Only then compare MESH_04/08/16 on identical loads and restraints.
F. Compute per-node signed errors, abs errors, distribution L1 error, grouped wall/column reaction sums, region resultant moments, and convergence ratios; no acceptance by summing zero.

## Program/code UX review
The old `Step 13` label is a **historical workflow module name** (`OpenSees_Step13_Analysis_Basis_V115.py`), **not NBC clause 13**. Proposed GUI text is `P-Delta initial cases, stiffness + damping (legacy module 13)`, preserving imports. NBC and adopted IS clauses remain separately named.
The repeated pasted JSON and formula-reference content is not itself evidence that the GUI generated duplicate content: `components/ui/application.py` currently constructs its formula-reference text from a single `summary` string. If a specific window shows duplication within one render, capture its source text or UI event trace; do not infer duplication solely from copies pasted into chat.
**Mass-vs-gravity:** NBC Table 5-1 0.3Live is seismic mass, not by itself a 1D+1L gravity test. The 1D+1L comparison in this audit used Live=1.0. Initial P-Delta/limit-state load combinations are separate, with NBC governing seismic cases and the two expressly adopted IS 16700 project exceptions documented in AGENTS.md.
**Wall/slab effective stiffness:** do not apply wall EI multipliers as a blind single scalar to all membrane/shear behavior or change gross self-weight thickness. Confirm ETABS modifiers, local axes, shell section formulation and equivalent OpenSees bending response. Preserve approved conventional slab 0.25/0.35 as separately documented project settings, pending applicability review.

## Output ownership
All **new gravity result runs** should ultimately write beneath `<export>/02_GRAVITY/` with consistent per-run case folders, source evidence, comparison, logs, Excel, plots and upload ZIP. The immediate software patch (PR #44) moves only the **gravity-specific immutable review snapshots** under `02_GRAVITY/REVIEW_SNAPSHOTS`; legacy solver writers/readers and existing ETABS files remain unchanged. Full canonical writer/reader migration needs an explicit manifest resolver and regression tests for old runs. Global all-module packages remain a separate intentional action; gravity GUI must not implicitly aggregate MRSM/ESM.

## Status
- Global applied load and reaction reconciliation: PASS EQUILIBRIUM (not ETABS physical equivalence).
- Individual 32-node reaction distribution: FAIL SCREENING.
- 76/97 numerical cases: SOLVER PASS, per-node ETABS matching not established.
- Native 4/8/16 mesh convergence: NOT VERIFIED.
- NRC/IS/NBC design acceptance: NOT GRANTED.
