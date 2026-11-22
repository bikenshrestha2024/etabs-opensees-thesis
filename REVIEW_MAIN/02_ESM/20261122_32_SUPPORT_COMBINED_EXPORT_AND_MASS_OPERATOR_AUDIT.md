# 2026-11-22 — ESM combined export / 32-support / Rayleigh mass-source audit

**Status:** engineering source analysis and software TDD. **Not native 25-storey ETABS/OpenSees equivalence.** Source data used: two user-uploaded ESM review ZIP snapshots, one 76-restraint gravity support reaction CSV, gravity displacement and settlement CSV and GUI log/screenshot. Raw proprietary model and EDB were NOT uploaded to public GitHub.

## The ESM combined-export failure: identified source-level root cause

The ESM GUI writes the numeric `NBC105_ESM_Calculation_<state>_<direction±>_E<±/0>_V111.json` into the canonical **`03_ESM/RUNS/<state>/<exact model-case>`** folder, but `components/equivalent_static/organized_exports.py::_data_rows` searched only the GUI's **`OpenSees_Analysis_Results/<exact model-case>`** root. The uploaded ZIPs contain model source, status logs and eight saved solver evidence JSONs, but **no numeric calculation JSON**. The absence is a folder/packaging issue, not evidence that the lateral force calculation was never performed. The GUI had already logged eight X±/Y± E+/E0 generated force cases and eight SUCCESS exit codes.

Correction: exact state-and-model matched `_exact_calculation_roots`, no arbitrary recursive search of older EDB/models; classify and copy the source numeric JSON/CSV alongside solver status in an immutable review snapshot. The strict `build_combined_esm_export(root)` API still raises when numeric JSON is missing; `allow_incomplete=True` (GUI) now produces **NO_CALCULATION_JSON** manifest-only workbook/ZIP with no fabricated T, V, Wi, Fi or NBC acceptance. A current ETABS-linked spreadsheet recorded in the later user log is an independent **calculation route**, not a native ETABS solved seismic response.

## Quantitative evidence from 76-restraint uploaded gravity results

| Original model restraint grouping | Node records | Vertical reaction (kN) |
|---|---:|---:|
| User-confirmed actual foundation support IDs | 32 | 192356.1551905 |
| Additional exported wall-mesh restrained IDs | 44 | 94063.6030406 |
| Total | 76 | 286419.7582311 |

The 44 exported wall-mesh restraint records have **32.84%** of vertical reaction in this numerical model. They are **not extra real foundations**. Removing their direct fixities to implement user-confirmed 32 physical foundations changes the structural boundary condition and requires reproducing ETABS auto-edge/MPC force transfer. No arbitrary reaction redistribution or extra ground spring is introduced by this PR. The known separate ETABS-elastic rebuilt 32-foundation max residual 768.045 kN remains open. Global reaction balance cannot certify local equivalence.

The source 25-floor ledgers in the reviewed snapshot differ: one has total dead load **270291.5561853 kN**, the other a clear-beam candidate **261639.1118337 kN**, with the same 48000 kN other live load. Difference **8652.4443516 kN**. This reflects different self-weight/clear-beam source policies; do not cross-apply their mass/periods without exact model/EDB/CSV hashes.

## NBC 105:2025 Clause 5 numerical reconstruction

| Value | X | Y |
|---|---:|---:|
| Reviewed two X-direction 12m walls (with openings), three Y-direction 6m walls | Aw 2.073174515 m² | Aw 2.203080332 m² |
| `Σ(Wi di²)` from saved 25-floor Rayleigh ledger | 1770.9881575 | 7903.8093416 |
| `g Σ(Fi di)` with `g=9.81` | 25312.2737124 | 54931.8191599 |
| `T_R=2π√(numerator/denominator)` per §5.1.1 | 1.66196593495 s | 2.38334056741 s |
| `1.25*T_emp` per §§5.1.2–5.1.3 | 1.98128088503 s | 1.92197977671 s |
| `T_design=min(T_R,1.25T_emp)` | **1.66196593495 s** | **1.92197977671 s** |

The **arithmetic is internally correct for its saved inputs**. However, the recorded run was a **76-restraint LEGACY_GROSS_SHELL** stiffness case with a 1D+0.3L classified seismic preload, **not** the primary 32-support ETABS-elastic model. Both raw and adopted periods must be recomputed under the newly selected actual support and mass operator cases. The §5.2 weights are DL+0.6 storage LL+0.3 other LL+0 roof LL where categories apply; do NOT substitute the full 1D+1L gravity comparison. The canonical Clause 5 code is already integrated into ESM and Rayleigh; do not duplicate the formulas in new solver modules.

## Source lumping vs actual modal solver mass

- The original 25-floor **source floor-weight ledger** is exactly reconciled to active horizontal seismic nodal masses: **284691.5561853 kN**, 25 level master tags and COM=(12,9) m for each source level.
- **1571 active intermediate wall/vertical mesh nodes** carry **13841.2117598 kN**, ~4.862% of active horizontal seismic mass. Original runtime distributed mass as `ops.mass(n,m,m,m,...)` to individual source nodes, **not** as 25-storey master lumped mass.
- `SOURCE_DISTRIBUTED` is retained as default physical operator until source-matched eigenperiod, directional mass, diaphragm inertia and mode shape evidence supports a model change.
- Optional explicit `STORY_LUMPED_NBC` builds mass based on §5.2 floor mid-height tributaries, checks each floor mass centre against the source master, sums `Mx=My=Σm` and `Jz=Σm[(x−xm)^2+(y−ym)^2]` at floor diaphragm master, leaves vertical nodal mass in place, checks source master IDs/elevations and exact per-floor Wi. A different operator can change period and torsion even if total mass matches; **not native accepted**.
- For physical 32 configuration, newly freed 44 originally XY-fixed base-mesh nodes cannot silently acquire positive lateral seismic mass merely because their artificial constraints were removed. Current source support classification is retained for mass bookkeeping.

## Cross-module case selection and stale-copy gate

One support selector `components/model/support_case_contract.py` supplies `PHYSICAL_32` default, `SOURCE_76` and `WALL_BASE_97` explicit diagnostics. The complete model owner `components/model/assembly.py` consumes `OPENSEES_SUPPORT_CASE` across modules. ESM, modal, LTHA, NLTHA GUI selectors explicitly record chosen case and mass policy; Rayleigh preliminary stage uses ESM selection. The old gravity GUI retains its `GRAVITY_1.0D_1.0L` support-case diagnostics for backwards compatibility.

**Critical exported runtime:** model-building scripts can import a *copied* `OpenSees_Runtime_V118` bundle. A new GUI selection cannot force obsolete code to honor it. Generated ESM, modal, LTHA, NLTHA runners now call `require_runtime_support_case` immediately after the model-builder finishes and reject outdated/mismatched restraint counts or profile evidence. They request refreshing the exported runtime rather than silently claiming a 32-support result built with 76. A source-master mass policy also must be regenerated from source: historical saved periods remain historical and untouched.

## Unresolved engineering gates

1. Rebuild current ETABS export and packaged Python runtime from the same EDB/source configuration and verify source SHA256 and case identity for the 32 primary model. The 44 shear-wall mesh joint auto-edge/MPC force-transfer mechanics remain unresolved (issue #140).
2. Native ETABS/OpenSees comparison of full gravity 1D+1L reactions per actual 32 foundations and six-DOF common cut; the separately rebuilt 768.045-kN pointwise residual remains open.
3. Verify base/floor mass, polar inertia and consistent source ETABS mass operator; rerun 32 case modal and Rayleigh with saved 25-story Wi/Fi/di, reaction balance and independent T.
4. Current batch includes eight SUCCESS cases with **only E+ and E0**, not E−. Full applicable both-sign envelope would require 12 unique cases; generated runner count is not full NBC ESM design for 95m ULS (§3.2.1 comparison-only).
5. Vs30 measured and source site classification per §4.1.3.1 for H>40m; soil C input and Z=0.35 Kirtipur do not by themselves demonstrate accepted site classification.
6. MRSM §7.4 combined response, §7.5 appropriate base-shear scaling, unscaled drift, nonlinear wall first-step convergence and final 224 history cases remain independently not verified.

**CI tests** are project-source numerical/synthetic checks, not a new Windows ETABS or full 25-storey OpenSees native run.
