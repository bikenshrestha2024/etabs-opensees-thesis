# Independent 32/76/97 gravity reaction partition — 2026-11-17

**Status:** USER-WORKBOOK DERIVED DIAGNOSTIC. **NOT PHYSICALLY EQUIVALENT**, NOT a new ETABS or OpenSees solver run, and NOT an automatic modification to project supports, model stiffness or force distribution. Generated using the original private workbook; that workbook and per-node model identifiers were **not uploaded to public GitHub**.

## Exact source and method

- User Library source: `ETABS_OpenSees_Full_Gravity_Reaction_Comparison.xlsx`, downloaded privately for this review.
- **Actual source XLSX SHA-256:** `0a60379a90f9ef7b153f8a0b42ef841ff1a4c1238d531ae4e0f4347956083def`.
- Sheet `ALL_97_SUPPORTS`, header row 1, rows 2–98: 97 mapped entries. Columns: OpenSees node, ETABS point, ETABS restraint tuple, source class, included in 32, ETABS FZ, OS32 Rz, OS76 Rz, OS97 Rz. `CASE_TOTALS`, `ROOT_CAUSE_GATES`, `SUPPORT_DOF_AUDIT` were independently cross-referenced.
- Recalculation: for each support-group and model, sum only numeric reaction entries. For identical mapped object points, compute signed `R_OS - FZ_ETABS`, absolute L1 sum, RMS discrepancy, and maximum individual absolute discrepancy. A blank cell in an absent model configuration is **not zero force in the source model** and is not included in a matched-point RMS comparison.
- Group assignment: 32 original primary points; 44 additional source-restrained wall points; 21 later-added supports, present only in OS97. Original ETABS object-level FZ on the 44 source-restrained wall points is reported as zero. This does **not** establish the internal ETABS analytical-joint reaction or MPC/edge-constraint mechanism.
- Workbook reports model SHA `bdd4e82d00874152dd58153e3c7041eae8cdaa13cbea33700e4b7e7200cde0d3`; the underlying EDB/source model bytes were not present for independent hash confirmation. **The workbook hash is verified locally; its embedded model-source hash remains a claim.**

## Independent vertical reaction sums

All forces below are `kN` and refer to **1.0D + 1.0L** as labeled in the workbook.

| Physical group | Count | ETABS object FZ | OS32 Rz | OS76 Rz | OS97 Rz |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original 32 points | 32 | 311,367.313600 | 311,367.313880 | 206,904.300346 | 206,381.527098 |
| 44 additional originally restrained wall points | 44 | 0.000000 | not modeled as restrained | 104,463.013534 | 74,953.565828 |
| 21 new continuous-wall-base points | 21 | no matching ETABS object | not present | not present | 30,032.220953 |
| **Total recovered** | — | **311,367.313600** | **311,367.313880** | **311,367.313880** | **311,367.313880** |

The global vertical total difference is **+0.00027955 kN**, a tiny reporting/numerical difference. It does **not** establish matching force-transfer paths.

### Partition as a share of total gravity

| Model | 32 original points | 44 originally restrained wall points | 21 added points |
| --- | ---: | ---: | ---: |
| ETABS point-object output | 100.0000% | 0.0000% | no matching points |
| OS32 | 100.0000% | released | absent |
| OS76 | **66.4502%** | **33.5498%** | absent |
| OS97 | **66.2823%** | **24.0724%** | **9.6453%** |

**Key numerical observation:** In OS76, the 44 wall-connected source-restrained nodes carry **104,463.013534 kN** (about one third of the entire gravity reaction). The original 32 then carry that much less reaction than ETABS point-object values. The 76-point L1 difference equals approximately twice 104,463.013534 kN because the deficit of the primary group is matched by a surplus assigned to the 44 zero-reaction ETABS object points. This is an **attribution of the mapped reaction discrepancy**, not proof of which ETABS internal constraints or frame/shell stiffness caused it.

### Local mapped error metrics

| Population compared | Model | Matched points | L1 sum of absolute kN differences | RMS difference (kN) | Largest absolute node difference (kN) | Signed sum (kN) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Original 32 | OS32 vs ETABS | 32 | **37,297.027** | **1,322.667** | **3,041.266** | ~0 |
| Original 32 | OS76 vs ETABS | 32 | 104,463.013 | 4,540.266 | 10,914.108 | -104,463.013 |
| 76 source points | OS76 vs ETABS | 76 | **208,926.027** | **3,595.348** | **10,914.108** | ~0 |
| Original 32 | OS97 vs ETABS | 32 | 104,985.787 | 4,567.882 | 10,983.666 | -104,985.787 |
| 76 source points only | OS97 vs ETABS | 76 | **179,939.352** | **3,281.722** | 10,983.666 | -30,032.221 |

OS97's negative signed difference over the 76 original points is balanced by its *unmatched* 21 added supports. This does not make it a better ETABS source representation. **Lower 32-node L1 mismatch is not proof that releasing 44 actually restrained source points is physically justified.**

## Engineering judgement and decisive independent experiment

**Evidence established:** equal global vertical force; different support-reaction distributions; exact documented 32/44/21 partition; source export lists full six-DOF restraints for the 44 additional source points; only 32/76/97 sensitivity runs exist in this workbook.

**Not established:** ETABS internal analytical-joint ID graph and shell auto-mesh constraints; common physical wall-base force/moment resultants; frame end-offset stiffness and beam-end force stations; equal gravity patch load transfer; identical diaphragm/column/rigid-zone stiffness; independent Windows model reanalysis. The source workbook lacks the full mapped support xyz and moment vectors necessary to calculate the complete physical base-cut `FX,FY,FZ,MX,MY,MZ` from the same origin.

Required discriminating sequence:
1. Hash/freeze the original EDB and extract **analysis-level**, not merely point-object, source nodes, six restrained DOFs, master/slave constraints, wall auto-mesh edge relations and exact gravity combination.
2. Read **ETABS Object JointReact and analytical Element/Joint reactions** in the same local/global axes and frame state. Do not assume the 44 zero-`FZ` point objects are inactive structural supports.
3. Form a common base cut around each physical wall footprint and compute all **six** force/moment resultants, including beam/column forces and the reference origin.
4. Match `1.0D+1.0L`, joint overlap, slab patch `1 kN/m²` checks and rigid-end zones for identical analytical sections. Reproduce wall and beam transfer in a one-bay and first-floor subassembly before modifying 25-storey source settings.
5. Re-run exact source topology and the 32/97 *sensitivity* variants independently. Only accept native ETABS–OpenSees **physical equivalence** after common-cut forces/moments, deformations and local demands match agreed predeclared engineering tolerances.

**Acceptance:** G02 local gravity equivalent = **FAIL/NOT VERIFIED**; global 1D+1L equilibrium = **ARITHMETIC MATCH ONLY**. Do not promote to passing G02 or G03, change default supports from this report, or claim wall first-step NLTHA numerical closure.

This is intentionally a source-derived aggregate report: no private EDB, workbook, raw node mapping, unredacted logs or seismic records are committed.
