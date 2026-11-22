# Modal mass operators: SOURCE_DISTRIBUTED versus STORY_LUMPED_NBC

**Status:** implementation walkthrough and engineering comparison; **NOT** native ETABS/OpenSees dynamic equivalence or NBC 105 approval. **Owner:** `components/model/assembly.py` and `components/model/story_mass_operator.py`. The same selection is exposed in Modal/MRSM/LTHA/NLTHA and controlled by `OPENSEES_SEISMIC_MASS_POLICY`. Preserve the default `SOURCE_DISTRIBUTED` until exact source-specific checks support another operator.

## What the two options actually do

`SOURCE_DISTRIBUTED` is **spatially distributed NODAL lumped mass**, not a consistent element mass matrix. The complete-model assembly creates gravity/load-derived `nodal_mass` from the model's seismic mass factors and assigns, to each originally unrestrained source node, `ops.mass(tag, m, m, m, 0, 0, 0)`. Originally restrained source X/Y points are assigned zero active horizontal mass. ShellMITC4 `ElasticMembranePlateSection` density is **zero** in this builder, so the existing source nodal masses are not supplemented by an independently invented shell inertial density. Their X/Y mass locations retain the local structural mesh distribution; rigid diaphragm constraints may transform these masses into effective rigid-body translation and torsion.

`STORY_LUMPED_NBC` is an **explicit changed dynamic mass operator**, not a mandatory rule of NBC 105. It first totals the same eligible `nodal_mass` into each 25-storey tributary group using the source floor elevations; source mid-height wall/frame mesh nodes are assigned to their story. For each diaphragm master at `(x_m,y_m)`, it computes

\[
m_i=\sum_{j\in i}m_j,\quad
x_{CM,i}=\frac{\sum_jm_j x_j}{m_i},\quad
y_{CM,i}=\frac{\sum_jm_j y_j}{m_i},\quad
J_{z,i}=\sum_j m_j\left[(x_j-x_m)^2+(y_j-y_m)^2\right].
\]

The model requires the computed center of mass to coincide with the diaphragm master within **0.001 m** (default); otherwise it rejects the condensation. It then sets eligible source node X/Y masses to zero, **retains their source Z-direction masses**, and assigns `ops.mass(master,m_i,m_i,0,0,0,J_{z,i})`. The code checks that floor numbers, master IDs, elevations and actual seismic weights `W_i=m_i g` match the current assembled `NBC105_ESM_Story_Weights_Assembled_V118.csv` before this change can be applied. The project gravity constant is `g=9.81 m/s²`.

**Important:** assigning the same total `m_i` to both independent horizontal DOFs does **not** mean counting floor physical mass twice. The two entries are the coefficients in separate (X) and (Y) inertial DOFs. With rigid diaphragms and matched mass centres/inertia, translational-and-torsional effective inertia can approach equivalence; local shell/mesh inertia, coupling and semirigid deformation may still differ. Never infer identical eigenperiods simply from matching total `W_i`.

## Direct comparison

| Check | SOURCE_DISTRIBUTED | STORY_LUMPED_NBC |
| --- | --- | --- |
| Seismic mass origin | Source-assembled gravity-pattern seismic mass at original nodal locations | **Same** eligible source seismic masses reassigned by story |
| Horizontal nodal mass | Eligible mesh/frame nodes each retain `m_j` in X/Y | Source nodes X/Y set to zero; each story master gets `m_i` in X/Y |
| Vertical nodal mass | Existing `m_j` | Original source `m_j` remains on the source node |
| Torsional inertia | Spatial nodal distribution with valid diaphragm constraint transformation | Explicit polar `J_{z,i}` at the diaphragm master |
| Mass centre | Actual spatial distribution | Explicitly rejected if centre/master mismatch > 0.001 m |
| Intermediate-height wall nodes | Retain their source horizontal inertia | Mapped to their story group per elevation |
| Local and global modes | Retains inertia at original mesh nodes | Can alter local dynamic participation, mode shapes, torsion and periods |
| Source ETABS equivalence | **NOT VERIFIED** pending source mass/constraints comparison | **NOT VERIFIED** and requires a separate sensitivity/equivalence rerun |
| Default | **YES** | Only explicit opt-in |

## Recommended source-matched acceptance tests

1. Identify source `EDB`, exact current export, story-ledger and source model/config SHA256. Retain the original 32 foundation supports; 44 additional wall-mesh points are **not independent ground supports**. Confirm mesh-to-foundation MPC/load transfer.
2. Compare total active X/Y seismic mass, all story `W_i`, mass centres and floor polar inertia against native ETABS with the same diaphragm, wall, section, shell thickness and assignment assumptions. Do **not** compare a 1.0D+1.0L full gravity test to a separate code seismic mass case as if they were identical.
3. Before comparing periods, resolve the source wall effective stiffness basis (current `LEGACY_GROSS_SHELL` versus applicable NBC Table 3-1 / ETABS actual modifiers), primary 32 support model and actual current source mass ledger.
4. Under `SOURCE_DISTRIBUTED`, verify 3D modal eigenperiods/eigenvectors and at least 90% mass participation in each horizontal direction, plus torsional mode participation and support compatibility. Save the same evidence for a separate `STORY_LUMPED_NBC` model run **without overwriting** the original.
5. If switching operators, independently compare `T_X,T_Y,T_{torsion}`, mode shapes/MAC if useful, eccentric drift at opposite floor edges, MRSM shears, and NLTHA response to identical verified bidirectional records. Never call a matching total seismic weight proof of dynamic equivalence.
6. For NBC105:2025, soil classification and applicable `V_{s,30}`, project damping, period bounds, ground-motion matching and member nonlinear law qualification are separate input reviews. A mode count, model GUI selection or numerical convergence is not engineering approval.

## Output and interface clarification

The canonical run creator creates *all* folders, including `07_EXPORT_ZIP`, at run initialization. That folder can correctly remain **empty** after a modal analysis because `components/modal/gui_and_reports.py` saves numerical outputs to `02_RESULTS`, Excel to `03_EXCEL` and figures to `04_FIGURES`; it does **not** automatically package a modal review ZIP. An existing MRSM package in `05_MRSM/.../06_REVIEW/Organized_Results/.../ZIP_Exports` is **not** the missing modal ZIP and must not be copied into another run as evidence. Do not create automatic ZIPs of private source data without the user's explicit local export action.

## Source references

- Code owners: `components/model/assembly.py` (section "seismic mass operator") and `components/model/story_mass_operator.py` (`story_lumped_mass_plan`).
- NBC 105:2025 §5.2/Table 5-1 (seismic weight factors); this code clause does **not** itself certify a particular nodal mass operator. Official text: https://giwmscdnone.gov.np/media/files/NBC_105_2025_Seismic%20Design%20of%20Buildings%20in%20Nepal_lqqvx6a.pdf
- OpenSees `modalProperties` documentation: https://opensees.github.io/OpenSeesDocumentation/user/manual/analysis/modalProperties.html (mass matrix, nodal vs element masses, rotational participation).
- Bentley RAM Technical Note, *Eigenvalue Analysis with Meshed Diaphragms: Distributed Mass Idealization*: https://docs.bentley.com/LiveContent/web/RAM%20Structural%20System-v2024/Help/en/Topic/RAM_Frame/Technical_Notes/c-rssfa_Eigenvalue_Analysis_and_Meshed_Diaphragms_Distributed_Mass_Idea.html (parallel-axis/diaphragm condensation illustration).
