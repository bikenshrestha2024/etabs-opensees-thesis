# P0 engineering review — 3D RCC core E-SFI wall mapping and actual material evidence

**Date:** 2026-11-04. **Scope:** source-code review and deterministic solver-free tests only. The existing first-step X-direction 3D wall instability is **NOT resolved by these patches**, and no user-specific ETABS structural model or native OpenSeesPy transient has been executed.

## 1. Confirmed source-level defect and corrected panel convention

**Original issue:** `components/nonlinear_time_history/wall_diagnostics.py:inspect_wall_geometry` previously verified that wall shells were vertical parallelograms, but it did not verify **which edge encoded the wall's local width**. In `components/model/assembly.py:build_complete_model`, the OpenSees `E_SFI_MVLEM_3D` command computes `width=distance(node_i,node_j)`. A vertical quad with first edge following the building height could pass the old preflight, causing *macro-fiber widths to be derived from storey height*, not wall panel width.

**Fixes committed:**
- At geometry preflight, require bottom `i→j` width edge horizontal (no Z rise) and `i→l` panel height edge vertical, upward, and nonzero; require a valid finite wall thickness and positive panel area. Store checked panel width/height in result JSON.
- During assembly `_wall_panel_nodes`, normalize bottom-first orientation and reject unsupported tilted or misoriented panels before computing E-SFI macrofiber widths. Report a meaningful error if bottom nodes are not adjacent.
- The existing quad's 4-node counterclockwise order and normal are still necessary. **A geometric screen does not prove constitutive correctness.**

**OpenSees command and units** (`kN-m-s`, 3D, six DOFs per node):

```python
ops.model('basic', '-ndm', 3, '-ndf', 6)
# After validated source-node ordering (i,j,k,l) with bottom i->j:
width = math.dist(xyz_i, xyz_j)         # horizontal wall segment width [m]
m = 5                                   # example only: require mesh sensitivity
thicks = [t_m] * m                      # [m]; sourced from actual ETABS wall section
widths = [width/m] * m                  # [m], sum(widths) = width
matTags = [fsamTag] * m                 # existing research WEB-only assumption
ops.element('E_SFI_MVLEM_3D', wallTag, i,j,k,l, m,
            '-thick', *thicks,
            '-width', *widths,
            '-mat', *matTags,
            '-Density', 0.)
```

The published E-SFI implementation has `-CoR` default .4, `-ThickMod` default .63, `-Poisson` default .25 and `-Density` default 0. These defaults **must be reviewed for the actual thesis building**, as should the source mass implementation. The fiber `m` count must not be treated as experimental validation. Reference: [OpenSees E-SFI-MVLEM-3D element](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html), Kolozvari, Lopez, Massone (2023), *Engineering Structures* 294, 116700, https://doi.org/10.1016/j.engstruct.2023.116700.

## 2. RCC core openings are not optional in thesis-labeled runs

**Original issue:** No opening manifest produced `UNVERIFIED_NO_MANIFEST`, but the runtime could continue. A present manifest declaring zero openings produced `UNVERIFIED_NO_DECLARATIONS`, also permitting progress.

**Fix:** `analysis_intent=THESIS_NLTHA` now requires a real `wall_openings_manifest` JSON, a nonempty `wall_openings` array and geometric void check `GEOMETRY_SCREEN_PASSED`. Missing, empty or filled openings reject a thesis-labeled run **before gravity or nonlinear transient computation**. Exploratory probes can still use unverified openings, but the output is clearly labeled non-approval.

**Manifest schema (example ONLY; all coordinates must come from ETABS analysis mesh/drawings):**

```json
{
  "wall_openings": [{
    "id": "ETABS_VERIFIED_OPENING_ID",
    "plane": "XZ",
    "constant_m": 0.0,
    "horizontal_min_m": 1.0,
    "horizontal_max_m": 2.0,
    "z_min_m": 0.0,
    "z_max_m": 3.0,
    "source": "Review-approved drawing and ETABS opening audit SHA"
  }]
}
```

This helper supports only global axis-aligned XZ/YZ rectangular voids. Openings on inclined, slanted, rotated, multi-polygon or nonrectangular RCC core segments **must not be coerced into this geometry**; implement a source-mesh-derived extension first. This check does not validate coupling beams, diaphragm wall interaction, pier axial-flexure, spandrel cyclic shear, or source mesh coincidence.

## 3. Project wall and frame materials: production remains blocked

**Source finding:** `components/nonlinear_time_history/research_building_materials.py:define_building_materials` currently selects either `PEER_Web_ESFI_Patch.json` or `M30_Fe500_SFI_MVLEM_3D.json`. Frames are instantiated using nominal Fe500 and Concrete01 assumptions; wall reinforcement ratios use a default two-curtain 20mm at 200mm source template unless overridden. The wall region report expressly states **UNCONFINED WEB THROUGHOUT**; there is no validated actual project boundary/core wall material and reinforcement schedule.

**Fix:** `check_project_material_qualification` now blocks the production `THESIS_NLTHA` intent for both existing literature/sensitivity material bases. It does **not** accept a user-set `project_calibrated=true` as a bypass. Research-only ZERO/X/Y/XY probes remain permitted and retain their assumption register.

**To implement a real production material adapter, required actual inputs are:**
1. **RCC frame source**: beam and column section width/depth, effective cover, exact individual bar positions/areas and grade; hoop/crosstie spacing and diameters, confined versus cover concrete, splice and hinge region data.
2. **RCC core with openings**: wall web and flange thicknesses by height, boundary zones and reinforcement, orthogonal web junctions, pier/spandrel and coupling beams, source floor connectivity and real axial load, local axes and 3D mesh.
3. **Cyclic laws**: actual concrete cylinders/stress-strain envelopes and confinement parameters for `ConcreteCM`/`Concrete02`; measured steel stress–strain and `Steel02`/`SteelMPF` transition parameters; verified `FSAM` rhoX/rhoY by wall region and `nu`/`alpha`.
4. **Outrigger steel/BRB/FVD**: source SHS material/area and end-connection stiffness, BRB yield core and fatigue/overstrength, FVD `K,Cd,alpha`, stroke force/velocity and physical connection location. All include signed cyclic work/energy and experimental source citations.
5. **Evidence for each source**: exact local files and SHA256, specimen literature/DOI, version of the constitutive model, source reviewer and acceptable matching errors. One paper specimen is not automatically the physical building.

A future explicitly implemented adapter must be tested on isolated beam/column sections, 2D wall specimens, **3D core with openings** and then the full gravity and bidirectional transient sequence. **Do not turn off the material gate by setting an approval flag**.

## 4. First-step failure: what is presently known and how to test

Earlier actual V168 logs found a t≈0.005 s Kobe X-only failure and post-failure nonfinite element force at 110280 / 112778, source wall AREA:354 / 482. These are symptom locations; a post-failure response is not a proven initiating material or element. The newly added orientation gate is a potential *input defect screen*, **not a diagnosis of those exact source objects**.

Reproduction procedure using the project’s native Windows environment:

1. Retain the original ETABS model exports and source file SHA256.
2. Run static preflight and inspect `NLTHA_Wall_Geometry_Preflight.json`. It now reports E-SFI bottom width/vertical height. If an invalid panel is detected, stop and correct the ETABS assembly/node order, not the numerical material parameter.
3. If project openings are known, supply the verified `wall_openings_manifest` and inspect `NLTHA_Wall_Opening_Preflight.json`. No manifest means NOT VERIFIED.
4. Before a full record, perform separate fresh-domain ZERO, X, Y and XY diagnostic cases using identical material, gravity and time step; retain source model and record SHA plus every solver fallback.
5. Use `20_TRACE_FAILED_ELEMENT.py` or `21_TRACE_FAILED_ELEMENT.py` to map solver tag to source ETABS area and 3D source nodes. Confirm axis, pier height, plan location and surrounding coupling nodes. Verify `RCPanel`, `globalForce`, `Curvature`, `ShearDef` support by installed OpenSees build.
6. Compare last **accepted** state with failed-step snapshot; the snapshot can contain rolled-back, incomplete or nonfinite values and cannot alone establish causal initiation.
7. Run material/element sensitivity and time-step refinement, then full X/Y, XY/YX and independently verify grav/mass/torsion. Only a complete native run and actual project calibration justifies promotion beyond research-diagnostic status.

Source docs: [OpenSees E-SFI](https://opensees.github.io/OpenSeesDocumentation/user/manual/model/elements/E_SFI_MVLEM_3D.html), [PEER Report 2015/12](https://peer.berkeley.edu/sites/default/files/webpeer-2015-12-kristijan_kolozvari_kutay_orakcal_john_wallace.pdf), [NBC 105:2025 official PDF](https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf). Clauses §9.3.1–§9.3.3 apply to 3D NLTHA; §5.5.3 supplies referenced drift limits.

## 5. Tests / evidence

```powershell
python tests/verify_wall_geometry_preflight.py
python tests/verify_wall_openings.py
python tests/verify_project_wall_material_gate.py
python tests/verify_v168_diagnostics.py
python tests/verify_failure_evidence.py
```

The first three are solver-free and can be run in GitHub Actions. The latter two exercise diagnostic output paths with fixtures; they do not replace the native failed-element reproduction. **Current native wall-element runtime status: NOT RUN / failure unresolved**.
