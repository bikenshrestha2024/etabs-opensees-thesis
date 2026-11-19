# 19 November 2026 — independent review of Codex-updated main (source and CI scope)

**Source frozen at audit start:** `3a1bb6cc6bf6bd59402b7c76abaebe2ab342b7e2` (untruncated Git tree, **3,200 tracked files**), three commits ahead of previous reviewed `fcb3bcc754d1811c3e01f20faec9985f01cde329`. `compare_commits` listed **29 changed paths**, including Rayleigh, equivalent-static calculations and Excel source linkage, gravity comparison, project workbook importer, Soil C completion checks and tests. This is a **change-focused review**, not a claim to have semantically verified every one of the 3,200 files / ~4,424 old AST candidate units.

## Confirmed defects in exact main's CI

**1. NLTHA Python quality [failed run 44363501838](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44363501838):** `tests/verify_ref_tags.py` reported the following three *new public* functions without required docstring references:

- `components/equivalent_static/etabs_linked_excel.py::apply_reviewed_grouped_walls`
- `components/equivalent_static/etabs_linked_excel.py::publish_route_comparison`
- `components/modal/rayleigh.py::rayleigh_result_prefix`

This pull request adds genuine existing local documentation paths as `[REF ...]` docstring tags. The function logic is not changed. Such tags certify provenance labelling only, **not** independent engineering approval.

**2. Integrated audit [failed run 44363501733](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44363501733):** source review ledger `docs/review/ledger/semantic_review_attestations.csv` pinned `components/inputs/project_workbooks.py::read_explicit_excel_calculation` to obsolete Git blob `a58e0d3c48c0d7590eccfa164842d83ba036d387`. Actual latest file blob `ff9aa0d7661794537ab96601898462f35c3fd6a1`. An independent function-body comparison on both versions (original vs updated, normalized line endings) shows **this particular 97-line function unchanged**: it preserves explicit ULS/SLS workbook selection, exact/source EDB provenance warning, finite positive Aw, optional adopted periods, read-only XLSX and streamed SHA-256. Its containing module was modified outside this function by 12 m wall grouping and stricter Rayleigh-cache import. The ledger is repinned only for this previously source-inspected *unchanged function*, with no new claim of whole-module approval. No change to the ledger row's `SOURCE_INSPECTED_TESTED_NOT_NATIVE_VERIFIED` status.

**GREEN closure gate:** every exact-PR-head GitHub Actions workflow previously triggered by the changed paths must pass; pay particular attention to `verify_ref_tags.py` and integrated `P1_STALE_OR_UNSAFE_SOURCE_REVIEW_ATTESTATION`. Do not merge on a partial result or count an unrelated previous-commit green workflow.

## Engineering review of Codex's new claimed evidence

The Codex commit introduces `docs/validation/20261118_RAYLEIGH_RETAINED_DOF_CORRECTION.md`, `docs/validation/20261118_32_SUPPORT_GRAVITY_CONVERSION.md`, `tests/test_rayleigh_retained_dof.py` and `REVIEW_MAIN/06_NONLINEAR_TH/20261118_RECORDED_HISTORY_COMPLETION_REVIEW.md`. The following statements are **reported evidence from Codex's newly authored documents**, not independently replayed full-building native solver results in this review:

| Area | Newly documented numerical result or change | Remaining verification |
| --- | --- | --- |
| Rayleigh ULS X | New torsion-suppressed tied-floor one-step T_R = **1.662332 s**, same-domain eigen T_1 = **1.663934 s**; previous retained-master ten-step estimate was **3.898514 s** | Current source model/solver hash, saved per-floor displacements, reactions, original EDB stiffness/mass, independent benchmark, repeat native same version |
| Rayleigh ULS Y | New T_R = **2.383772 s**, eigen T_1 = **2.383914 s**; previous retained-master estimate **5.590441 s** | Same; verify constrained-node actual kinematics and partial SP/MP equivalence |
| Grouped first-storey walls | Reviewed 2×12m X with two 2m openings/line gives **Aw-X = 2.073174515 m²**; three 6m Y walls **Aw-Y = 2.203080332 m²** | Verify geometry, openings and NBC `Awi` grouping for exact original current ETABS source; user workbook remains traceable |
| ESM result | X design period **1.662332 s**, `V_x ≈ 30,582.206 kN`; Y adopted **1.921980 s**, `V_y ≈ 26,450.735 kN` | Source-equal ETABS ESM/MRSM comparison, Vs30 site condition, EDB shape/modifiers/load cases; do not silently retrofit old thesis results |
| 32-source support gravity | Document reports best in-memory modifier sensitivity reducing maximum individual reaction mismatch from **3,041.266 kN** to **756.511 kN** | Unresolved substantial point reaction discrepancy; 76 original source restraints vs ETABS shell edge interpolation, actual six-component physical wall cuts and common rigid-end/diaphragm reactions |
| Soil C 224-history completeness | `inspect_case` requires a real history CSV, finite monotonic accepted-state trace, matching durations and sample count; `audit_matrix` requires 112 × XY/YX output positions | Configuration/status consistency only; native full 224 outputs and original waveform/EDB hashes, wall convergence and engineering acceptance remain OPEN |

### Independent source-review cautions

1. **Native test provenance:** `tests/test_rayleigh_retained_dof.py` calls `pytest.importorskip('openseespy.opensees')`; a green CI suite without an installed OpenSeesPy can skip the solver benchmark. Check actual GitHub job logs for skip/collected counts before claiming native regression passed.
2. **Rayleigh transfer:** The local doc reports a constrained retained-DOF `Transformation` bug and a one-step workaround. The selected physical-node translation is consistent with the paper's intended COM displacement only when the rigid-floor constraints, floor centers of mass, translational spread, suppressed torsion, gravity baseline, support reactions and source EDB are genuinely reproduced. All downstream ESM design shear and story force results must be regenerated. This is **not** independent validation of source ETABS floor forces or response spectra.
3. **Gravity model variants:** Codex's 32-support/section modifier sweeps are clearly labeled **in-memory diagnostics**, not proof the original 76-restraint ETABS model is equivalent or permission to replace source shell/beam stiffness. Lower node residuals are not validated physical equivalence without matched degrees of freedom, six force/moment resultants and support edge interpolation.
4. **Soil C completeness audit:** `inspect_case` checks that summary and duration-gate JSONs contain plausible 64-character SHA-256 strings and that the CSV is complete. It **does not recompute those hashes from private model or waveform bytes**. Synthetic regression is not proof of 224 native analyses. The new code correctly reports `RESEARCH_ONLY_FULL_RECORD`, not design approval.
5. **Workbook grouping:** the new importer conditionally overwrites live `awx/awy` input values with geometry-derived grouped candidates while retaining `workbook_awx/awy` for audit. This is a **material computational behavior change**, requiring explicit project grouping approval/source geometry matching; don't quietly assume the old workbook Aw or adopted periods survived unchanged. A broad `except Exception` around the importer fallback may hide the exact grouping validation reason in note strings, so preserve/report these notes and fail design-acceptance closed.

## Independent GitHub source-discovery artifact, exact original Codex head

From [pinned source-discovery Actions run 44363501836](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44363501836), artifact `semantic-discovery-public-source-queue` ID `14455052563`, extracted and independently inspected `DISCOVERY_SUMMARY.json`, `SYMBOL_DISCOVERY_NOT_REVIEWED.csv`, and associated inventory/queue files:

| Result from automated repository-wide inventory | Exact artifact value |
| --- | ---: |
| Git tracked files | 3,200 |
| Python files (all repository categories) | 794 |
| AST symbols discovered (all categories) | **4,802** |
| AST parse issues | **0** |
| Dependency import classifications | 3,697 stdlib; 1,325 local exact; 14 local package; **557 external/dynamic requiring environment** |
| Output I/O candidates | **4,075** |
| Duplicate SHA blob groups / extra files | **400 / 478** |
| Unclassified file manual triage | **110** |

These broad inventory counts are not directly interchangeable with the **older 579 active modules / 4,424 active semantic-review candidates** from a different filtered audit. The changed current audit state has **16** narrow, source-attested/tested functions. The semantic-review backlog therefore remains large; a parser report and stale-hash fix are insufficient for full function-by-function acceptance.

The published Windows GitHub Actions run [44363501763](https://github.com/bikenshrestha2024/etabs-opensees-thesis/actions/runs/44363501763) is explicitly titled **headless contracts (NOT ETABS / GUI acceptance)**, and logs only Python and filesystem tests. `tests/test_rayleigh_retained_dof.py` uses `pytest.importorskip('openseespy.opensees')` and is not evidence by itself of a successful OpenSees 3.8 full-model run on GitHub Actions. Codex's local-period and gravity numbers are recorded in the project docs, but an independent current-source native replay with complete source and solver inputs remains open.

## Scope and decisions

**Passed based on the prior main's evidence:** tracked Git metadata enumeration and selected static/import regression. **Failed at audit start:** exact-main integrated static source-attestation and NLTHA documentation-tag jobs. **Pending until green head:** these two software CI gates. **Open:** full source-semantic review, original native ETABS–OpenSees physical parity, first-step X wall material/solver root cause, complete 224 M0–M6 full-duration NLTHA and independent NBC/site-performance acceptance. No numerical physics or source EDB was changed in this CI repair.

**Privacy:** Only authored source review and documentation tags; never mirror original proprietary EDB, registered XLSX, accelerograms or native user results into the public repository.
