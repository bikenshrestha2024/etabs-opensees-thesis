# 2026-11-15 — Exact 32/76/97 ETABS/OpenSees gravity reaction evidence and staged output reconciliation

**Case:** uploaded 2026-11-15 run, `GRAVITY_1.0D_1.0L`, native ETABS `1. DL + LL`.  
**Review status:** NUMERICAL_EQUILIBRIUM_PASS; MEMBER_REACTION_EQUIVALENCE_FAIL; NATIVE_ENGINEERING_NOT_VERIFIED.  
**Source protection:** original EDB/Excel/CSV/ZIP/source models never modified or uploaded to GitHub. Uploaded evidence is analyzed privately; public record contains aggregates only.

## 1. Global totals are not equivalence

| Source | Supports | Total applied and solved Rz (kN) | Minimum UZ (mm) |
| --- | ---: | ---: | ---: |
| ETABS native extracted joint-reaction sum | source 76 fixed | 311,367.313600 | NOT PROVIDED for matching source joint set |
| OpenSees 32 diagnostic | 32 | 311,367.31387955 | -21.017645 |
| OpenSees source restraints | 76 | 311,367.31387955 | -20.737735 |
| OpenSees extra wall-base fixity sensitivity | 97 | 311,367.31387955 | -20.732239 |

Global ETABS/OpenSees difference **0.00027955 kN** or **approximately 8.98e-8%**. This checks **aggregate vertical arithmetic only**.

When matched **per source node**, the 32-support diagnostic has an absolute reaction discrepancy sum **37,297.027 kN**; the 76-support source-restraint case has absolute per-node reaction differences totaling **208,926.027 kN**. Signed residuals cancel globally. Some of the worst source-point differences in the 32 case are ETABS point 263 / OpenSees node 36 and ETABS 264 / OS 41, each ETABS **14,748.5222 kN** vs OS **17,789.78798 kN** (+3,041.26578 kN, 20.6208%). The native ETABS source joint IDs are *not* OpenSees numeric tags.

## 2. A source restraint is not interchangeable with a zero-reaction node

`GRAVITY_NATIVE_EQUIVALENCE_PREFLIGHT.json` records **76 source-restrained base points, all six source DOFs `111111`**, and the primary 32 diagnostic **releases 44 such original fixed points**. The 44 released points have `FZ_ETABS=0`, yet their reactions sum to **104,463.014 kN** in the 76-support OpenSees case, approximately **33.55% of total gravity**. This is a **confirmed distributional mismatch**, not an arithmetic issue. The upload manifest `Gravity_ETABS_OpenSees_Evidence_V04/EVIDENCE_MANIFEST.json` expressly lists `node_audit_76/ETABS_ZERO_VS_OPENSEES_NONZERO` as a **required engineering mismatch**, with 17 optional items not produced. Packaging a ZIP is not a native validation.

Do not deduce **44 physically free points** from FZ=0. An ETABS restrained point can be zero-force in a particular result, or its output reaction may be transferred to another mesh/model object. Compare exact **original ETABS global restraints, point vs internal analysis-element identity, mesh constraints, wall-base transfer and per-point F1–F3/M1–M3** before deciding which OpenSees base restraining topology physically matches ETABS. The 32 case may resemble ETABS FZ distribution better **by releasing valid source constraints**; that alone does not justify treating it as the correct physical model. The 97 model adds 21 non-source supports, explicitly a boundary sensitivity and not an ETABS-native model.

## 3. Rigid-zone and gravity-weight evidence

The preflight independently identifies **1,367 ETABS frame end-offset metadata entries requiring rigid-end-zone review**; none was missing/invalid. Common native offsets include I=0/J=0.8 m (450), I=J=0.55 m (300), I=J=0.625 m (100), and no offsets (167). The recorded ETABS rigid-zone factor is 1.0 for these reviewed records. CSI's official ETABS End Length Offset help differentiates offset/rigid-zone factors from beam clear self-weight: **the factor affects bending and shear stiffness**, and **does not alter axial/torsional deformation**. Passing `ETABS_BEAM_CLEAR_LENGTH` self-weight quantity (750 beams) does **not** prove equivalent rigid-zone element stiffness, local end transfers or frame releases.

The source gravity log records `ETABS_NATIVE_BEAM_QUANTITY_GATE: SOURCE_IDS_OFFSETS_AND_TOTAL_MATCH`; it also records **8,652.444 kN** as beam end-offset candidate and **19,358.527 kN** joint-overlap alternative as **mutually exclusive audit-only hypotheses**. Do not subtract either automatically after the clear-beam source export. Current comparison must preserve actual 1.0D+1.0L patterns and source hash; do not mix with the 0.3-Live mass/preload case.

## 4. Input uploads and review completeness

The audit examined the uploaded eight relevant gravity/comparison ZIPs and their entries: **1,539 archive entries**, grouped into **417 CRC32+size content signatures** (possible same-content duplicates; CRC32 is a quick audit indicator, NOT cryptographic provenance). Around **229 MB of text-format entries** were scanned **line by line** in relevant small JSON, CSV, logs and Markdown; **75 log/manifest-like entries** were indexed and **69 selected issue-bearing lines** retained as examples. The audit did **not** manually read every binary Excel/PDF cell or plot pixel; entries can be duplicates across package versions, and no numerical claim is derived solely from filename presence. All original ZIP files remain immutable.

`Gravity_Review_UPLOAD(9)` and `Comparisons_Review_UPLOAD(9)` already package stage-owned evidence with local paths redacted. The raw Windows export root still contains legacy CSV, JSON, XLSX, HTML and their `.processing.json` sidecars: current `components/inputs/export_mirror.py` is a **SHA-verified copy-only mirror** precisely because many legacy importers/readers still expect those original root paths. This is a **preserved compatibility contract**, not proof that root output cleanup was implemented. Deleting/moving flat legacy outputs without coordinating every reader, source hash manifest, and source model writer would break stages. Analyze concrete writer/reader references, make new runs canonical, then migrate older paths only when tests verify the path adapters.

## 5. Changes made in this PR

`components/gravity/three_case_comparison.py` now can join the 32-case native source audit (from the registered *exact 32-case* result sibling) to all independently solved 32/76/97 reaction tags, creating a **full 97-row CSV** and **ETABS vs OpenSees all** worksheet in `Gravity_32_76_97_Comparison.xlsx`. It includes all **76 actual source-restraint rows**, including the 44 zero ETABS FZ points, and identifies 97-only points as lacking direct ETABS source reactions. Existing 32/76/97 native solver outputs remain unchanged. The extra report is **SOURCE_NODE_MAPPED_REACTIONS_NOT_STRUCTURAL_EQUIVALENCE**, with aggregate/absolute spatial differences; no stale audit is chosen by scanning unrelated directories.

Only when the matching source-audit file is found beside the currently registered 32-case result is the join enabled. Otherwise the comparison remains available with `SOURCE_ETABS_SUPPORT_AUDIT_NOT_FOUND`; it will not manufacture ETABS results. Fail closed on duplicate points, missing original restraints, 32-case tag mismatch, nonfinite FZ and inconsistent source totals.

Synthetic regression: `tests/test_gravity_full_source_reactions.py` plus the existing three-case tests.

## 6. Engineering resolution sequence — **not** a forced numerical match

1. Re-open exact ETABS EDB, identify source point objects **and actual analysis elements**. Export `PointObj.GetRestraint`, JointReact F1–F3/M1–M3 for the exact load case and both object/element IDs, the internal wall auto-mesh/constraint mapping, slab/beam/wall connectivity and all input hashes.
2. Enforce the **native 76 restraints** at the matching physical coordinates as the current source-equivalence *candidate*; **compare all six reactions and source mesh load transfer**. Also retain the 32 diagnostic and 97 continuous-base sensitivity runs. Do **not** edit original source to delete 44 supports merely to match a plotted pattern.
3. Compare member/end-zone stiffness with explicit ETABS end offsets and rigid factor. Match stiffness in bending/shear only, preserving proper axial/torsional mechanics. Use representative 1-bay and wall-base interface with equivalent missing-superstructure actions; then whole-building gravity vs ETABS.
4. Reconcile original source dead/live/roof, shell loads and self-weight exactly once; compare separate beam/wall/column and slab reaction shares, internal joint forces, horizontal/vertical equilibrium and displacement; use existing 04/08/16 mesh studies for convergence, but only with complete native results.
5. Compare mode periods/participation, natural rigid body modes, lateral load and seismic mass before claiming ETABS/OpenSees structural equivalence. Preserve the previously adopted **provisional pin-ended steel diagonal truss** modeling decision; it has no role in falsifying gravity reactions.
6. After accepted source-identical linear baseline, run G00–G10 staged nonlinear gates, including actual RC reinforcement/confinement, calibrated wall FSAM, buckling/BRB/FVD, initial P-Delta and bidirectional full-history acceptance.

## 7. Official technical references (no numerical calibration claimed)

- CSI ETABS **End (Length) Offset**, source help: https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Frame/End_Length_Offset.htm — offset calculation and rigid-zone factor for bending/shear stiffness, not axial/torsion. *(Use source version matching your ETABS model.)*
- CSI ETABS **Joint Restraints**, source help: https://docs.csiamerica.com/help-files/etabs/Menus/Assign/Joint/Restraints_Joints.htm — actual global six-DOF restraints; zero reaction is not definition of zero restraint.
- CSI ETABS API **AnalysisResults.JointReact**: https://docs.csiamerica.com/help-files/etabs-api-2016/html/2f434351-3116-da4d-ad8f-5e26ed6e51a2.htm — original object/element joint reaction F1/F2/F3/M1/M2/M3.
- CSI **Analysis Reference Manual**: https://docs.csiamerica.com/manuals/etabs/Analysis%20Reference.pdf — reactions may include restraints, springs and grounded links; source and analysis element IDs differ. **This is mechanics reference, not a project-specific ETABS validation**.
- Choi et al., *Outrigger Design for High-Rise Buildings* (CTBUH), §§2.2/2.8: core–outrigger–perimeter load path and interface behavior; referenced under the established pin-ended diagonal decision DB-OUT-2026-11-15-01.
- Dvorkin & Bathe (1984); Bathe & Dvorkin (1985): shell formulation framework, not an identity of ETABS and OpenSees shell/load paths.

**Acceptance:** Source evidence supports **solved gravity equilibrium**. It **does not** support matching node reaction distribution or native ETABS/OpenSees physical equivalence. No original model was modified, and no native solver was run in this public-code correction.
