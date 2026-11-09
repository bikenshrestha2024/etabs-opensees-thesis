# Physical self-weight vs section stiffness vs seismic mass — ETABS v23 / OpenSeesPy

**Scope:** 25-storey asymmetric RCC wall–frame high-rise, full `1.0D + 1.0L` gravity comparison, ULS elastic NBC 105:2025 stiffness, modal / ESM / MRSM and later NLTHA.

**Primary code**: `components/model/physical_weight_modifiers.py`; source metadata extraction and model assembly: `components/model/assembly.py`; full source reconciliation: `components/gravity/source_load_reconciliation.py`; independent source and mass ledgers: `components/model/single_count_self_weight.py`.

## Engineering determination

**Cracked section stiffness reductions are not reductions in physical self-weight.** For the full gravity comparison, member physical weight is generated from the actual original cross-section, original length or shell area, physical section thickness and material unit weight. Applied member self-weight remains `gamma × physical volume`, subject to the original ETABS material, member/section *independent weight modifier*, original self-weight load-pattern assignment, and a separately verified non-duplicated geometric volume ownership policy. Never apply `EI=0.35EI_g`, `EI=0.70EI_g`, `wall 0.5`, or `slab bending 0.25` to `gamma`, physical `A` used for weight, or physical `t` used for weight.

**Exception to the phrase "no modifier":** CSI ETABS explicitly provides separate section and object **MASS** and **WEIGHT** modifiers. When the original ETABS model has a nonunity weight modifier, blindly assigning 100% geometric weight cannot reproduce its original analysis. We read the native modifier and **stop export on a nonunity weight** rather than silently remove it. A nonunity mass modifier is separately reported because it affects modal/RSA/NLTHA source mass, not the physical gravity dead load.

### Three independent quantities

1. **Physical permanent weight**: `W_D = Σ gamma_i × V_i + additional assigned superimposed dead loads`. Use actual volume; no cracked stiffness reduction. Physical self-weight is allocated to ETABS load patterns (normally one Dead/Self Weight pattern with multiplier 1, all others 0). The *pattern multiplier* allocates existing self-weight; it is not an extra second application or a stiffness reduction.
2. **Analysis stiffness `K`**: depends on `EA`, `GA`, `GJ`, `EI22`, `EI33` and shell membrane/bending/shear modifiers. The governing small-displacement linear problem is `K u = F`, with restrained support reactions `R = K_cf u_f - F_c` (after partitioning the equilibrium system) and global static balance `Σ R_z = W_applied`. Changing `K` changes displacements and load sharing, not the independently prescribed physical `F`. For P-Delta and nonlinear problems a tangent/secant formulation is required; `K u=F` is not a complete nonlinear material law.
3. **Seismic mass**: `M` is assembled independently using the mass-source / NBC effective seismic live-load factors. The 0.3 imposed-live fraction for qualifying occupancy and excluded roof live in seismic mass **must not** reduce floor, roof or other live load in the independent `1.0D+1.0L` gravity reference case.

A reduction in `EI` can increase drifts and change force/reaction distribution or period. It is **not simply an extra safety factor**: in a statically indeterminate structure, it can either increase or decrease force in particular wall/column branches. ULS design and serviceability must use the appropriate independently documented section stiffness assumptions. A 32/76/97-support choice changes boundary conditions, not gravity source weight.

### NBC 105:2025 clause-level basis

* **Clause 3.4, Table 3-1: "Effective stiffness of cracked sections"**: 0.35 `E_c I_g` beam, 0.70 column, 0.50 cracked wall and 0.25 flat slab under ULS are representative flexural stiffness definitions; these are **not weight multipliers**. The same table has different SLS factors. Shear and torsional behavior require separate treatment and can differ from the simple flexural coefficients.
* **Clause 5.2, Table 5-1: seismic weight**: dead load and applicable fraction of imposed loads for the earthquake mass model. It does not replace full 1D+1L gravity verification.
* **Clause 3.6: load combinations**: ULS load factors govern strength combinations. They are NOT modifiers of concrete material density or geometry. The verification case `1.0D+1.0L` is separately labelled, even if the structural *stiffness model* uses ULS cracked properties.

Reference: [Official NBC 105:2025 PDF, Government of Nepal / Kathmandu eBPS](https://ebps.kathmandu.gov.np/UploadFiles/NBC_105_2025_Sesmic_Design.pdf). Verify exact occupancy live fractions and ULS load-combination selection in the official edition; do not generalize a universal live 0.3 reduction to full-gravity loads.

### CSI source API proof — ETABS section and object modifiers are multiplicative

* [CSI Property/Stiffness Modification Factors](https://docs.csiamerica.com/help-files/etabs/Menus/Define/Property_Stiffness_Modification_Factors_Form.htm): object and section factors multiply when assigned at both levels; default 1.0.
* [Frame section GetModifiers](https://docs.csiamerica.com/help-files/etabs-api-2016/html/7d1dfebd-5f84-d02f-63e0-9c635d293692.htm) and [frame object GetModifiers](https://docs.csiamerica.com/help-files/etabs-api-2016/html/a1bbbe54-46b4-cb9b-ed83-713b4c9328c1.htm): eight independent factors, indexes 0–5 stiffness, 6 mass, **7 weight**.
* [Area property GetModifiers](https://docs.csiamerica.com/help-files/etabs-api-2016/html/1a82e2fa-47bc-0196-1e52-79559c5b.htm) and [area object GetModifiers](https://docs.csiamerica.com/help-files/etabs-api-2016/html/8a110f33-95a6-d7ad-8c6d-3f418baf4b9a.htm): ten factors; indexes 0–7 membrane, bending and plate shear; 8 mass, **9 weight**.
* [CSI Analysis Reference Manual, Frame/Shell Property Modifiers and End Offsets](https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf): stiffness, section weight and section mass are separately modified. Frame insertion point offsets may not carry loads; beam end offsets are part of a model's member length and loading and require separate review.
* [OpenSeesPy ShellMITC4](https://openseespydoc.readthedocs.io/en/latest/src/ShellMITC4.html) and [ElasticMembranePlateSection](https://openseespydoc.readthedocs.io/en/latest/src/elasticMembranePlateSection.html): the elastic shell section uses physical thickness and a separate mass-density input, with optional plate-bending stiffness modifier. The current converter assigns gravity as explicit equivalent nodal loads and uses separately built nodal seismic masses, so assigning additional hidden body loads would be double counting.
* [OpenSeesPy nodeReaction](https://openseespydoc.readthedocs.io/en/latest/src/nodeReaction.html): read actual restrained-support response; `ΣR_z` is a gravity **balance check** and does not establish that original ETABS source self-weight is correct.

## Actual program flow

1. Read original source sections, ETABS material unit weights and 3D geometry. Preserve original slab 150 mm, wall thickness and beam/column gross section dimensions for geometric weight.
2. Read native CSI `FrameObj.GetModifiers`, `PropFrame.GetModifiers`, `AreaObj.GetModifiers` and `PropArea.GetModifiers`; record section + object separately in `OpenSees_Source_Model_Metadata_V118.json`. If any extraction fails, record the gap — don't infer 1.0 from silence.
3. Verify **every native weight factor is unity**. On nonunity weight, emit the contradiction to `Gravity_Physical_Weight_Modifier_Audit.json/.xlsx` and block physical 100%-gravity export. Do not change native ETABS data to make it pass. Separate mass discrepancies remain an outstanding seismic mass audit.
4. Require the total original ETABS self-weight pattern allocation to equal 1.0 for the 100% full-gravity comparison; if missing, classify as incomplete. Avoid a second explicit self-weight load in addition to the already converted member weight.
5. Frame `A × L × gamma` and shell `A_polygon × t_physical × gamma` are assembled once into original source load-pattern nodal force ledgers. Actual geometric intersection ownership and original ETABS beam self-weight convention remain separate verification gates: the default does **not** subtract a guessed 150 mm slab, 800 mm joint, 8,652.444 kN clear-length candidate, or 19,360 kN repeated-joint estimate to force equality.
6. Apply selected **gravity load case** factors separately (1.0D+1.0L for validation). Apply the independent seismic mass fractions only in the mass ledger.
7. Solve with actual `K`, get each `nodeReaction(tag,3)`, integrate 32/76/97 support reactions and compare against the **independently applied** F. Equal reactions and applied load prove equilibrium, not original source equivalence.
8. Audit source member component totals, slab physical weight, ETABS weight modifiers, beam end lengths, overlap solids and actual native ETABS material-list totals. Remaining global load error and support-region distributions must have separate gates.

### One-location output contract

All project-native source files remain next to the export. A **single consolidated evidence copy** is produced by the Gravity GUI's `Bundle gravity evidence ZIP` function under the selected gravity output root:

```text
<Selected gravity output root>/
  Gravity_Evidence_Upload/
    Gravity_ETABS_OpenSees_Evidence_Vxx.zip
    Gravity_ETABS_OpenSees_Evidence_Vxx/
      EVIDENCE_MANIFEST.json
      EVIDENCE_FILE_PATHS.txt
      source/Gravity_Physical_Weight_Modifier_Audit.xlsx
      source/Gravity_Physical_Weight_Modifier_Audit.csv
      source/Gravity_Physical_Weight_Modifier_Audit.json
      source/Gravity_Single_Count_Self_Weight_Audit.json
      source/Gravity_Slab_Self_Weight_Audit.xlsx
      source/Gravity_Joint_Type_Overlap_Review.xlsx
      source/ETABS_OpenSees_Beam_Weight_Reconciliation.json
      source/OpenSees_Complete_Model_Data_V118.json
      opensees/Gravity_Result_V110.json
      ...
```

Some filenames may be reported missing in `EVIDENCE_MANIFEST.json` if the original ETABS API extraction or corresponding native gravity run has not been performed; **do not manufacture or replace them with guessed values**. The GUI logs the exact ZIP and extracted-folder paths for upload. A successful model analysis must not be reported as fully ETABS-validated unless source provenance and all weight/volume checks pass.

## What remains unverified

The earlier 8,680.475 kN ETABS vs OpenSees difference has a previously reported beam end-offset candidate near 8,652.444 kN plus approximately 28.031 kN steel area discrepancy. This is neither a stiffness-modifier effect nor proof that beam/slab/column joint overlap should simply be deducted; the true ETABS Material List and source weight setting must confirm it.

The code **does not** promise exact physical union volume accounting for irregular wall junctions, rotated beam insertion lines, or slab polygons outside the supported geometry. Those cases require a verified source model representation, not an arbitrary force correction.

Author of this documentation and related changes: ChatGPT GPT-6. Historic commits and other AI contributions remain unattributed without direct evidence.
