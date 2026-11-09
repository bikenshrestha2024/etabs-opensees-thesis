# ETABS v23 ↔ OpenSeesPy: EQX/EQY and P-Delta verification (2026-11-09)

## Exact original ETABS X case definitions (from user's screenshots)

**Native nonlinear initial case** `EQX+ P Delta Initial`:
- Nonlinear Static, zero initial/unstressed state.
- `Self Weight=1.2; Floor Finish=1.2; Partition=1.2; Wall=1.2; Live=0.5; EQX=+1.5`.
- `Geometric Nonlinearity Option=P-Delta`; Full Load;
  nonlinear parameters user defined, iterative event-to-event;
  results Final State Only; source modal case `Modal Ritz`.
- The displayed initial state is the **positive** lateral action:
  `1.2DL + 0.5IL + 1.5EL_X`. The negative counterpart
  `1.2DL+0.5IL-1.5EL_X` required by IS 16700:2023 §7.2(d)
  remains a separate case to find and verify. Y cases are claimed
  analogously by the user but their native case records must be extracted.

**Native dependent linear case** `EQX+ P-Delta`:
- Linear Static, P-Delta/Nonlinear Stiffness
  `Use Nonlinear Case (Loads at End of Case NOT Included)`.
- Nonlinear stiffness source `EQX+ P Delta Initial`.
- Applied load pattern `EQX × 1.0`, no gravity load patterns in the
  linear dependent case. The result is a lateral-response increment
  computed about the selected initial tangent stiffness, **not**
  `1.2D+0.5L+2.5EQX`. Do not compare it with the initial case's
  total displacement and do not superpose the initial forces twice.
- Confirm the corresponding case in Y and any negative initial-stiffness
  branches directly from native ETABS case tables. Case names are
  references only until native definitions have been read.

**Seismic load patterns** from displayed source:
- EQX user-defined NBC 105 dual RC shear-wall load,
  displayed `C_X=0.087597`, `k_X=1.769284`.
- EQY displayed `C_Y=0.09291`, `k_Y=1.71099`.
- The source user-defined pattern screens show 0.05 accidental
  eccentricity, plus/minus branches selected. These are **not**
  assumed to be the same signed response step or case.
- Exact Aw-X, Aw-Y and adopted T1-X/T1-Y come from the user's
  original `NBC105_RS_Scaling.xlsx` workbook; record original
  cell addresses, full source SHA256 and the original versus current
  source EDB identity. Never replace the adopted values with a
  hard-coded period or recomputed generic effective wall area.
  The screenshot C and k are observed values, not fresh code proof.

## Validated prerequisites before static earthquake case comparison

- **Gravity correction first:** separate native ETABS source Material List
  independently confirmed gross beam self-weight excess
  8652.44435 kN, with beam clear-length matching ETABS and
  750/750 beam source/offset crosswalk. Re-export a NEW corrected
  OpenSees model with the native workbook verification gate. Fresh
  32-support gravity equilibrium and the local foundation reactions
  remain to be checked; 76/97 are sensitivity configurations. Do not
  delete wall mesh nodes based on their zero ETABS FZ.
- **Seismic mass:** ETABS MsSrc1, relevant load/mass pattern factors,
  roof-live exclusions, vertical/horizontal distribution, and
  OpenSees nodal masses must be audited independently. The
  `GRAVITY_1.0D_1.0L` diagnostic is not automatically the
  `1.2D+0.5IL±1.5EL` initial PDelta state.
- **Stiffness and PDelta:** identical effective RC frame/shell
  stiffness, beam insertion/end-offset geometry, actual first-order
  versus geometric stiffness, diaphragm and mesh connectivity, wall
  opening/membrane settings, 32-support primary boundary sensitivity,
  and initial load-step solver convergence. The OpenSees
  `geomTransf('PDelta')` is not by itself a complete equivalence
  demonstration for ETABS wall/shell geometric stiffness.
- **Existing OpenSees limitation:** the old ESM runner executes
  independent `PD_INIT_EL_X/Y_PLUS/MINUS` diagnostic cases,
  then builds a *new* model for ESM. Those tests do not prove that
  the second OpenSees run uses the exact tangent stiffness from
  `EQX+ P Delta Initial`. The new comparison requires
  `opensees_tangent_from_matching_initial_state_verified=true`,
  supported by actual saved solver state, otherwise BLOCK.

## Case matrix and output measures

| Native case | Type | Applied load | Comparison |
| --- | --- | --- | --- |
| EQX | Verify native | EQX, native factors | Ordinary first-order / configured static baseline |
| EQY | Verify native | EQY, native factors | Ordinary first-order / configured static baseline |
| EQX+ P-Delta | Linear, stiffness from EQX+ initial | EQX × 1.0 | Raw signed increment |
| EQY+ P-Delta | Analogous, independently extract | EQY × 1.0 | Raw signed increment |

Also retain positive and negative X/Y **nonlinear initial** stage
evidence separately, not as four extra interchangeable linear EQ
responses. Record initial baseline, applied load history, tangents
and independent signed foundation reactions.

For each matching ULS/SLS source condition, ±5% eccentricity branch,
axis, coordinate and final response step record:

1. **Seismic force input**: seismic weight by story; adopted C, k,
   floor force and cumulative applied story load; sum of lateral loads
   versus source base shear and reaction equilibrium. Compare source
   Excel/ETABS object values without rescaling spectral matches.
2. **Base shear**: signed incremental global X/Y support reaction
   `-ΣΔR_X/-ΣΔR_Y` in kN; zero lateral reference and load-state
   baseline must be explicit. Do not compare a nonconcurrent envelope
   with a signed static result.
3. **Story shear**: actual recovered structural section cut or native
   ETABS Story Shears table, not automatically the sum of assigned
   `F_i`. Keep a separate `applied_story_shear` load check.
   Wall mesh cuts require internal force integration with orientation
   and boundary sign verification.
4. **Roof displacement**: raw global UX/UY (m), incremental response
   at identical ETABS/OpenSees source diaphragm master or comparable
   edge node. Retain gravity/initial nonlinear baseline, and the
   amplified NBC design displacement in a different column.
5. **Interstory drift**: raw
   `(u_i-u_(i-1))/(z_i-z_(i-1))` using identical story/node
   reference points, sign and floor levels. ETABS max/corner drift
   and OpenSees diaphragm-master drift are different metrics.
   Report drift ratio and percent separately.
6. **Torsion**: master-node rotation about Z, X/Y extreme edge
   translation and +e/-e accidental torsion; plan irregularity.
7. **Critical member response**: concurrent column base axial,
   selected wall pier axial/shear, coupling-beam and outrigger
   reactions, beam end actions and support moments, with compatible
   shell-to-pier integration conventions.
8. **Second-order effect**: for like-for-like loads compare
   `Δ_PDelta/Δ_first_order`, signed reactions, residuals, and
   overall stability/θ checks. Do not treat a smaller shear/difference
   as automatically a valid equilibrium model.

## New source tools

- `components/validation/eq_pdelta_case_contract.py`: enforce
  signed initial IS factors and native dependent stiffness definitions.
- `components/validation/etabs_eq_pdelta_native_extract.py`:
  source case inventory, saved base reactions by ALL steps, raw
  available ETABS story and case-definition tables, with
  selection/units restoration.
- `tools/ETABS_EQX_EQY_PDELTA_EXPORT.py`: **Spyder-compatible**
  read-only attachment to existing ETABS, creates an indexed and
  hashed upload ZIP. Never invokes Analyze.RunAnalysis, saves
  EDB, closes an existing ETABS process or changes cases.
- `components/validation/eq_pdelta_comparison.py`: normalized
  story/roof/drift signed response comparison, Excel/CSV/JSON/PNG
  with fail-closed source identity, mass, source-case and stiffness
  gates. The 5% difference flag is a *diagnostic screen*, NOT NBC
  code acceptance.
- `tools/verify_eq_pdelta_4case_matrix.py`: offline four-case
  workbook and status matrix; incomplete data remain BLOCKED.
- `components/equivalent_static/calculation_and_gui.py`: adds
  raw interstory drift columns, labels input-force story shear,
  checks signed base-reaction equilibrium, and explicitly
  distinguishes independent initial checks from a genuinely
  reused nonlinear tangent.

## Windows usage

**First, ensure the ETABS model has actual FINISHED and SAVED
EQX/EQY initial and dependent results.** If not, run them through
your normal ETABS interface under a separate safe working EDB;
the script will NOT run missing analyses.

In Anaconda Prompt from the repository root:

```powershell
git pull origin main
conda activate etabs_env312
python tools/ETABS_EQX_EQY_PDELTA_EXPORT.py
```

Or in Spyder console:

```python
%runfile D:/path/to/opensees-nbc105-research/tools/ETABS_EQX_EQY_PDELTA_EXPORT.py --wdir
```

Select a local output folder. The script produces
`ETABS_EQ_PDelta_Evidence_YYYYMMDD_HHMMSS_UPLOAD.zip`,
with `ETABS_EQ_PDELTA_NATIVE_INDEX.json`, saved native base
reaction steps, raw story tables when available, case names,
file hashes and explicit unsupported/missing-table entries.

To compare raw ETABS/OpenSees responses, normalize each selected
original native result table to a CSV containing **exact** columns:

```csv
story_name,elevation_m,story_shear_kN,displacement_m,drift_ratio
Story1,3.6,0.0,0.0,0.0
```

The sample row is purely a SCHEMA EXAMPLE, not the user's model
data. Keep original native files unchanged, and map each field's
case, branch, step, units and source point. Do not substitute
the ESM applied-force sum for a recovered OpenSees section cut.

Then use `tools/verify_eq_pdelta_4case_matrix.py` with a
local JSON index containing the four case definitions, normalized
story paths and proof metadata. Missing data are reported as
blocked; no automatic physical correction or guessed result
is generated.

## Independent references

- CSI Linear Static dependent nonlinear case:
  https://docs.csiamerica.com/help-files/etabs/Menus/Define/Load_Cases/Linear_Static.htm
- CSI nonlinear zero initial conditions:
  https://docs.csiamerica.com/help-files/etabs/Menus/Define/Load_Cases/Initial_Conditions.htm
- CSI nonlinear geometric stiffness:
  https://docs.csiamerica.com/help-files/etabs/Menus/Define/Load_Cases/Static_Nonlinear_Pushover_Cases/Geometric_Nonlinearity_Options.htm
- CSI Analysis Reference Manual (case dependencies):
  https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf
- IS 16700:2023 §7.2(d), 1.2DL +0.5IL ±1.5EL/WL:
  https://www.services.bis.gov.in/tmp/CED20920094_14092023_1.pdf
- OpenSees `algorithm('Linear')` uses current tangent unless
  `-initial` requested, but single-step linearization does not
  alone certify equality with ETABS:
  https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/algorithm/LinearAlgorithm.html
- OpenSees `loadConst('-time',0)` fixes existing loads, but only
  for patterns created before the call:
  https://opensees.github.io/OpenSeesDocumentation/user/manual/misc/loadConst.html

**Acceptance remains pending**: native ETABS full EQ tables,
source workbook provenance, corrected 32-node gravity rerun,
same OpenSees nonlinear initial tangent state, actual recovered
story cuts, matching eccentricity and all signed result pairs.
