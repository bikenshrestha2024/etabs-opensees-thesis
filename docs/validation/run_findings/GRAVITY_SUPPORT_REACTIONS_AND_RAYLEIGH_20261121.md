# Gravity support-reaction distribution and Rayleigh period review (2026-11-21)

Status: `SOLVER_OR_LOG_EVIDENCE_ONLY_NOT_ENGINEERING_ACCEPTANCE`

Numbers: [GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.json](GRAVITY_SUPPORT_REACTIONS_AND_RAYLEIGH_20261121.json). No ETABS or OpenSees run was made for this review. Every solver number below was read from the uploaded evidence files. Every other number is hand arithmetic on those files and is marked as an estimate where it depends on an assumption. g = 9.81 m/s² (`components/nbc105/constants.py`).

## 1. Evidence used

Paths are relative to the uploaded review bundles. `GRAV_DIRECT` = `Grav/Gravity/Analysis/Gravity_Reaction_Diagnostic/20261121_110905_845717/Gravity_ETABS_OpenSees_Direct`. `T_` = `GRAV_DIRECT/ETABS_Native_Quantity_Tables/etabs_table_`. `M04` = `MESH_04/.../RUN_20261121_105741_5b380a16`.

| File | SHA256 prefix | Used for |
|---|---|---|
| GRAV_DIRECT/Direct_Gravity_Comparison.json | 7655678481da299f | totals, strategy, stiffness basis |
| GRAV_DIRECT/Gravity_All_Support_Nodes.csv | 33e14fbd808c9d7c | 32 matched reactions with x, y |
| GRAV_DIRECT/Gravity_All_Model_Nodes.csv | 06be3788e614daab | OpenSees nodal Uz, ETABS point ids |
| GRAV_DIRECT/OpenSees_Applied_Nodal_Gravity_By_Pattern.csv | 2eb3c89364e30f5e | tributary benchmark loads |
| GRAV_DIRECT/OpenSees_Applied_Nodal_Gravity_Summary.json | acd685727cdf335d | clear-beam export, pattern totals |
| T_960ec61b7e20c23d.csv (Joint Displacements, 1. DL + LL) | 33da61ed7c62e9b0 | ETABS Uz at 1101 joints |
| T_95526b0bc1af4636.csv (Diaphragm centre of mass) | 204e8e4e98c8ff92 | ETABS storey mass |
| T_2e6b12ebf681a176.csv (Auto seismic, user coefficient) | 468b4d06893ce7c6 | ETABS WeightUsed, K |
| T_58451a4200c00d44.csv (Slab property) | 2e2e3d34ae9f8f1c | slab modifiers |
| T_7adf2cc6c2af137f.csv (Wall property) | abbfc38b003a553a | wall modifiers |
| T_2fde14d5545fe8ea.csv (Concrete frame sections) | ca186ef5858d10dc | frame modifiers |
| T_ff0fe2ed05651a2e.csv (Material list by object type) | ab698c7b0c8367d3 | ETABS self-weight by type |
| T_da60e80c69278cbf.csv (Story forces) | d517679578071d51 | base P = 311,367.3139 kN |
| T_a18e5c9f4b4e0b56.csv (Linear static case definitions) | 3f1c11a9f6a89d56 | Dead/Live case type |
| T_072de811bf9b19b9.csv, T_70b73049efcc094b.csv (auto mesh) | b149bd45dd6c7c7b, bc6fcb3c63bca229 | floor/wall meshing |
| T_8f4cb3cb84084c6d.csv (End length offsets) | a06991ccf5fd5360 | rigid-zone factor |
| T_5e26941f713b29df.csv, T_fe62985f97f0505f.csv, T_af5a3c13053a3ba6.csv | 884273cf107a93dc, 3604dbfbb3f71d9b, d62965c35ad4015b | column/beam storeys and sections |
| Grav/.../Gravity_Native_Equivalence_Preflight/.../GRAVITY_NATIVE_EQUIVALENCE_PREFLIGHT.json | ca413fb661e8222b | 44 released supports |
| Grav/.../ETABS_END_ZONE_STIFFNESS_REVIEW.csv | e74cc0017ec6df29 | offsets 0.55/0.625/0.8 m, factor 1.0 |
| Comp/.../ETABS_OpenSees_All_76_Source_Support_Reactions.csv | a57993a8c2a50f83 | 32/76/97 support runs |
| Comp/.../Gravity_Wall_Base_Nodal_Reaction_Differences.csv | fba8efe87c27a4dc | source vs continuous wall base |
| ESM/OpenSees_Direct/NBC105_Rayleigh_Preliminary_V127.json | 3a30b1eeb4ad0753 | Rayleigh rows, audits |
| ESM/OpenSees_Direct/NBC105_Rayleigh_Preliminary_V127_ULS.log | 9266ada05726011e | preload total 286,419.758 kN |
| M04/OpenSees_Complete_Model_Data_V118.json | 8cb0cafa659c51fe | = V127 `model_sha256` |
| M04/NBC105_ESM_Story_Weights_Assembled_V118.csv | da89db0861422d0c | = V127 `story_weights_sha256` |
| M04/Gravity_Storey_Load_Breakdown_V131.json | cf0322f6b1438aa4 | storey loads |
| M04/ETABS_OpenSees_Beam_Weight_Reconciliation.csv / .json | edbb1f6ab5fcd37a / cca6c891d9aa77da | beam clear-length deduction |
| M04/OpenSees_Joint_Volume_Ownership_Audit.json | 5110958a876c5768 | 112 unsupported items |
| M04/OpenSees_Complete_Export_Report_V118.json | be1e03b506649c5d | 55 none-section frames |
| M04/OpenSees_Runtime_V118/components/modal/rayleigh_mass_audit.py, rayleigh.py, model/assembly.py | a975367b454c8666, fe54e0b391546986, 1fa009c5252356e5 | runtime code identity |

The V127 runtime `rayleigh.py` and `rayleigh_mass_audit.py` are byte-identical to origin/main (commit 891843e). The runtime `assembly.py` is identical to this branch.

## 2. Task A: support-reaction distribution

Run analysed: ETABS `1. DL + LL` against OpenSees `GRAVITY_1.0D_1.0L`, 32-support diagnostic set, `LEGACY_GROSS_SHELL`, verified clear-beam export. Totals agree (311,367.3139 kN both).

### Pattern

- **Pure group redistribution.** Core walls (supports in the plan box 6 ≤ x ≤ 18, 6 ≤ y ≤ 12) carry 109,278.2 kN in ETABS and 127,926.8 kN in OpenSees (ratio 1.1707). The 18 perimeter columns carry 202,089.1 kN in ETABS and 183,440.6 kN in OpenSees (ratio 0.9077). The 76- and 97-support runs give a core total of 130,603.4 kN and 130,656.1 kN. Changing the base support set therefore moves load inside the core and leaves the core-to-perimeter split almost unchanged.
- **Two numbers explain most of it.** Scaling every ETABS reaction by its group ratio removes 82.7 % of Σ|OpenSees − ETABS| (37,297.0 → 6,439.7 kN). The largest residual is 524.4 kN at ETABS 263/264, (12, 6)/(12, 12), down from 3,041.3 kN. The "3,000 kN joint-node discrepancy" is therefore mainly the core taking 17 % more load, plus a ±0.5 MN local term.
- **Doubly symmetric.** Across 64 mirror pairs about x = 12 m and y = 9 m the delta pattern is symmetric to 1.6e-10 kN.
- **Differential shortening changes sign.** Roof Uz in ETABS: core (6, 6) −13.476 mm, column (6, 0) −12.383 mm, so the core shortens more. In OpenSees: core −9.466 mm, column −10.415 mm, so the core shortens less.
- **Axial-stiffness indicator** (`tools/gravity_reaction_attribution.py`), EA_os/EA_etabs ≈ (N ratio)/(Uz ratio):

  | Group | z = 95.0 m | z = 49.4 m |
  |---|---|---|
  | core walls | 1.677 | 1.721 |
  | perimeter columns | 1.041 | 1.015 |

  Both programs give the columns the same axial flexibility. OpenSees makes the core about 1.7 times stiffer than ETABS does.
- **Tributary statics** (nearest reaction-bearing support in plan, ties split): core 120,181.3 kN, perimeter 191,186.0 kN. ETABS sits 10.9 MN below this for the core and OpenSees 7.7 MN above. The two programs depart from the statics benchmark in opposite directions, which is a stiffness effect. A load-allocation effect would move both the same way.

### Hypothesis table

| # | Candidate | Verdict | Evidence |
|---|---|---|---|
| 1 | Wall shell membrane stiffness: ETABS `Wall 300…610` f11 = f22 = f12 = 0.5 (m = 0.1), OpenSees `LEGACY_GROSS_SHELL` uses gross walls (factor 1.0, `assembly.py` shell branch) | **SUPPORTED, primary** | Sign flip of differential shortening; core EA ratio 1.68–1.72 against 2.0 expected from f22 alone, columns 1.02–1.04; group scaling explains 82.7 %; direction matches (stiffer core attracts load through beams, slabs and the belt-truss outrigger). The repository's earlier rebuild with native modifiers ([20261120_GRAVITY_REACTION_REBUILD.md](../20261120_GRAVITY_REACTION_REBUILD.md)) reduced the maximum difference from 3,041.266 to 768.045 kN and the sum from 37,297.027 to 10,072.106 kN. That run was not repeated here. |
| 2 | Base support layout (32 / 76 / 97 supports, continuous wall base) | REJECTED as cause of the split; it controls the distribution inside the core | Core total 127.9 / 130.6 / 130.7 MN, against 109.3 MN in ETABS. The 44 ETABS points with zero FZ take 104,463 kN in the 76 run (classification `SUPPORT_TOPOLOGY`). |
| 3 | Total load or weight error | REJECTED | Totals agree to 1e-8 kN. ETABS Material List gives beams 45,331.61 kN, equal to the clear-length beam weight (53,984.05 − 8,652.44). The sum of all ETABS object weights is 201,267.31 kN, equal to the OpenSees Self Weight pattern. |
| 4 | One-sided mapping error, missing member, torsion | REJECTED | Delta pattern doubly symmetric to 1.6e-10 kN. |
| 5 | Staged construction / sequential loading in ETABS | REJECTED | `Dead` and `Live` are Linear Static (StiffType P-Delta). No staged-construction case exists. |
| 6 | Column AMod / BE columns | REJECTED | `Col 800/900 BE` (AMod 0.69/0.70) are not assigned. Stories 1, 13 and 25 have 18 perimeter columns of 1100 or 1250 sections, AMod 1. Column EA ratio about 1.0. |
| 7 | Slab bending factor 0.25 | REJECTED as a mismatch | ETABS `Slab 150`: f = 1, m = 0.25. OpenSees: E/√0.25 and t·√0.25 keep the membrane term and scale bending by 0.25. |
| 8 | Rigid end zones (ETABS RigidFact 1.0; offsets 0.8 m at column tops, 0.55/0.625 m on beams), centreline in LEGACY | NOT DECIDABLE, secondary | Cannot reverse the sign of differential shortening. Column EA ratio about 1.0 shows no large axial effect. It may contribute to the ≤ 524 kN residuals (and to the 768 kN after native modifiers). |
| 9 | Area-load transfer (ETABS floors `No Auto Mesh`, OpenSees meshed ShellMITC4) | NOT DECIDABLE, secondary | At group level the departures are opposite (stiffness). At 14 of the 18 perimeter supports, ETABS−tributary and OpenSees−tributary have the same sign, so the corner/mid-edge pattern is shared. Needs separate Dead and Live joint reactions. |
| 10 | Rigid diaphragm | NOT DECIDABLE, expected minor | OpenSees `rigidDiaphragm 3` ties in-plane DOFs only. The ETABS diaphragm definition (rigid or semi-rigid) is not in the exported tables. |
| 11 | 112 unsupported items in the joint-volume audit | REJECTED | They are the 112 SHS braces ("not modeled as a solid RCC rectangle"). The policy is AUDIT_ONLY, so no load or stiffness changes. |
| 12 | 55 none-section frames excluded | REJECTED | ETABS null lines carry no weight or stiffness. 450 + 750 + 112 + 55 = 1,367 frames, and ETABS weight totals match. |
| 13 | Joint-volume overlap (19,358.5 kN potential) | REJECTED | AUDIT_ONLY. Not applied, and totals match ETABS. |
| 14 | Brace / belt-truss elements | Not a separate cause; transmits #1 | ETABS releases (T, M2, M3 at i; M2, M3 at j) match the OpenSees moment releases with GJ = 0. The outrigger couples core and columns, so it carries any EA mismatch into the reactions. |
| 15 | Support DOF | REJECTED | All 76 source supports are 111111 in both programs. |
| 16 | Shell mesh density | NOT DECIDABLE for reactions | MESH_04/08/16 have the same gross RCC weight (208,639.0 kN), but no gravity reactions exist for MESH_08/16. |

**Verdict.** The cause is a modelling-assumption difference, not a code defect. The run used `LEGACY_GROSS_SHELL`, which deliberately ignores the ETABS wall in-plane modifiers (0.5). The repository already contains the opt-in fix: the `elastic_etabs_comparison` rebuild (`components/model/elastic_conversion_settings.py`, settings in `docs/validation/20261121_native_gravity_uls.json` on origin/main). No solver, material or stiffness numerics were changed in this review.

**Diagnostic added.** `tools/gravity_reaction_attribution.py` ([guide](../../source/tools/gravity_reaction_attribution.py.md)) reports, for each support, the delta, the tributary benchmark, the residual after group scaling and a `consistent_with` tag. It also gives the symmetry and axial-stiffness indicators. On this evidence all 32 matched supports are `GROUP_AXIAL_STIFFNESS_SPLIT`, and the 44 ETABS zero-FZ points are not in the 32-support OpenSees set (`UNMATCHED`).

## 3. Task B: Rayleigh period and seismic weight

### Recomputation (from the stored V127 rows)

| Quantity | File | This review | Note |
|---|---|---|---|
| T_Rayleigh X (s) | 1.661966 | 1.661966 | Σ W d² = 867.784 kN·m², Σ F d = 1264.324 kN·m |
| T_Rayleigh Y (s) | 2.383341 | 2.383341 | 3872.867 / 2743.791 |
| H (m) | 95.0 | 95.0 | no basement (PROJECT_DECLARATIONS §1) |
| T_emp = 0.075/√Aw · H^0.75, X / Y (s) | 1.585025 / 1.537584 | 1.585025 / 1.537584 | Aw 2.07317 / 2.20308 m² |
| 1.25 T_emp, X / Y (s) | 1.981281 / 1.921980 | 1.981281 / 1.921980 | §5.1.3 |
| Adopted (lesser of), X / Y (s) | 1.661966 / 1.921980 | 1.661966 / 1.921980 | §5.1 |
| Reference-load k, X / Y | 1.740640 / 1.710990 | 1.740640 / 1.710990 from 1.25 T_emp; 1.542512 / 1.518792 from T_emp | V127 builds Fi from the ESM seed at the amplified period; ETABS EQX/EQY use the same K (1.74064 / 1.71099) |
| Fi = V·Wi hi^k / Σ | n/a | max deviation 2.3e-13 kN | shape verified |
| Total seismic weight (kN) | 284,691.556 | 284,691.556 | Σ Wi of the rows |

Clause check (printed pp. 28–30, user-supplied PDF). §5.1.1 defines Fi only as "lateral force acting at level i". An ESM §6.3-shaped vector is therefore a permissible reference load, and its amplitude cancels for a linear stiffness. di must ignore torsion. The run restrains diaphragm rotation and uses constrained floor translations. The kinematic audit shows zero floor-translation spread and a base-reaction error of 3e-15, which is consistent with that requirement. The choice of k is not prescribed for the reference load. Because the Rayleigh quotient is stationary, the effect of k is second order. It was not quantified because that needs a re-solve.

### Mass lumping: mid-height or upward?

- The V127 run used the **mid-height ledger**. The runtime `rayleigh_mass_audit.py` (origin/main) calls `storey_index_for_elevation` and reports `maximum_downward_lump_m = 0.0`. The ledger CSV says "assigned by NBC 105:2025 5.2 mid-height rule".
- All upward lumping here comes from the geometry. Masses sit at three kinds of level: on floors; at floor + 2.3 m (62 nodes per storey, 545.80 kN per storey, 25 storeys); and at z = 0 on 21 free (not restrained) base nodes, 195.24 kN. 2.3 m lies above the 1.9 m mid-height, so both rules send these masses up. Nodes at z = 0 go to floor 1 under both rules (the `storey_index_for_elevation` convention). The audit's 1571 nodes, 13,841.21 kN and 3.8 m maximum lift equal 25 × 62 + 21 nodes and 25 × 545.80 + 195.24 kN.
- **Effect on T from upward-only versus mid-height: 0** (identical floor weights). Old and new audit code on the real export both return 284,691.556 kN with a 3.1e-11 kN maximum floor discrepancy.
- Estimate with intermediate masses kept at their own elevation (d interpolated linearly, forces unchanged): T_X 1.6600 s (−0.12 %), T_Y 2.3805 s (−0.12 %).
- Strict §5.2 reading (mass below the storey-1 mid-height belongs to the base, so the 195.24 kN leaves W1): T changes by less than 1e-6 relative.

### Seismic-weight reconciliation (Table 5-1: D 1.0, storage 0.6, other live 0.3, roof live 0)

From Gravity_Storey_Load_Breakdown_V131.json: dead 272,019.758 kN, live 48,000 kN, storage 0, roof live 0. Hence W = 272,019.758 + 0.3 × 48,000 = 286,419.758 kN, which equals the preload total in the log. Subtracting the BASE row (1,923.444 kN = 1,728.201 on restrained base nodes + 195.243 on free base nodes) and adding back the 195.243 kN that the ledger places in floor 1 gives 284,691.556 kN. Every floor agrees with the ledger to 0.00 kN.

311,367.31 kN is not the same load state. It is 1.0 D + 1.0 L (263,367.31 + 48,000) of a **different export**, the verified clear-beam model. The V127 export `8cb0cafa…` uses `etabs_beam_weight_policy = GROSS_SECTION_LENGTH`, so its beams weigh 8,652.44 kN more (346.10 kN on each of the 25 storeys).

| Seismic weight | kN | vs ETABS (275,722.6 kN = 28,106.28 t × 9.81) |
|---|---|---|
| V127 file (gross beam weight) | 284,691.56 | +8,969.0 (+3.25 %) |
| Clear-beam weights, estimate | 276,039.11 | +316.5 (+0.11 %): +195.24 base nodes in floor 1, +212 roof, −3.8 per typical floor |

ETABS `WeightUsed` = 275,628.41 kN equals 28,106.28 t × 9.80665, the internal g of ETABS.

Estimated period with clear-beam weights (displacements scaled with the base-shear ratio; stiffness held constant; P-Delta tangent change ignored): **T_X ≈ 1.636 s (−1.55 %)**, **T_Y ≈ 2.346 s (−1.55 %)**. The adopted values become X ≈ 1.636 s (Rayleigh still governs) and Y 1.922 s (unchanged, amplified empirical governs). These are estimates only; a re-run is required.

## 4. Defects found and fixed

| Path | Defect | Before | After |
|---|---|---|---|
| `components/modal/rayleigh_mass_audit.py` (branch `feat/nbc105-clauses-1-3-annexc`) | On this branch the floor allocation was upward-only while the ledger in `assembly.py` uses the §5.2 mid-height rule. Any export with mass below a storey mid-height made `rayleigh.run` raise "Mass audit floor weights fail source seismic ledger reconciliation". | Two-floor test (floors at 3 and 6 m, node at 4 m): ValueError | Floor weights [120, 80] kN, shift −20 kN·m, maximum downward lump 1.0 m. Real export unchanged (284,691.556 kN). |

The fix was ported verbatim from origin/main 891843e (module and test), so a later merge of main is conflict-free for these two files.

No Task A defect was found in the repository. The gravity stiffness basis is a documented, configurable assumption.

## 5. Open items

1. Seismic weight and Rayleigh T in V127 come from the gross-beam export. They are 3.25 % heavier than the ETABS mass source and inconsistent with the gravity comparison model. The Rayleigh/ESM JSON does not record `etabs_beam_weight_policy`. Recording it belongs in `rayleigh.py` on main (V127), which this branch does not carry.
2. Residual 768 kN after native modifiers (repository record): rigid end zones, the OpenSees shell transverse-shear/plate coupling approximation, floor meshing, and wall-base edge constraints.
3. Roof +212 kN and floor-1 +195 kN seismic-weight differences against the ETABS diaphragm mass. These need the ETABS mass-source definition.
4. Effect of k on the Rayleigh shape, and the P-Delta tangent at lower gravity: needs a re-solve.
5. Gravity reactions at MESH_08 and MESH_16 do not exist.
6. ETABS EQX/EQY user coefficient C = 0.090129 / 0.09291 against OpenSees reference Cd 0.06309 / 0.06504. This lies outside the Rayleigh review (the amplitude cancels) and should be reconciled in the ESM review.

## 6. What the user must supply or re-run on Windows

1. Rebuild the clear-beam export with **ETABS elastic settings** (`--elastic-comparison-settings` with the ULS JSON), run Gravity with the 32-point diagnostic and with 76 source supports, and then run `tools/gravity_reaction_attribution.py` on the new comparison. Expected: core ratio close to 1, explained fraction low, residuals of a few hundred kN.
2. Re-run Rayleigh (V127) and ESM on the **verified clear-beam export** (or set `etabs_beam_weight_policy = ETABS_BEAM_CLEAR_LENGTH` deliberately in the config). Expected T_X ≈ 1.64 s and Y adopted 1.922 s; confirm with the run.
3. ETABS tables to export: Mass Source definition; Diaphragm definitions (rigid/semi-rigid); joint reactions for **Dead** and **Live** separately; frame end forces at the core-beam joints; wall pier forces at the base (P per pier); Joint Reactions including internal mesh joints.
4. Gravity runs at MESH_08 and MESH_16 with the same support set and stiffness basis.
