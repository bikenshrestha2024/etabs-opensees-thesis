# READ FIRST — authoritative physical-model and load-purpose contract

**Status:** user-confirmed thesis design intent, 2026-11-22. **Scope:** every AI agent, engineer, ETABS converter, OpenSees module, source-file migration, code review, tests, GUI, report and documentation edit. **This file is project instruction, not evidence that native ETABS equivalence or full NBC compliance has been verified.**

## Mandatory stop-before-edit protocol

1. **Before any edit**, read `AGENTS.md`, this file, `.agents/skills/etabs-opensees-read-first/SKILL.md` (or the linked Claude equivalent), and the matching governing code/source module guidance. Read even for changes described as a "small refactor", "format fix" or "quick bug fix" if they touch physics, data flow or module integration.
2. Declare the intended change, exact Git HEAD/branch, source file or module, baseline assumptions, impact across readers/callers/launchers, load-case purpose, model EDB/workbook identity, test plan, and whether native execution is possible. **Do not edit until the preflight assumptions have been checked against this contract.**
3. If other repo documents or a previous AI summary disagree with the user-confirmed contract, **do not elevate old prose over the current project decision**. Preserve historical evidence and record the discrepancy in the issue/PR. If verified native geometry or ETABS API data materially contradicts the declared physical intent, report a blocking evidence conflict rather than silently forcing a model correction.
4. Never claim that the instruction files were read, a test ran, or a native model was validated if the event was not actually observed. This procedure relies on agent adherence and PR review; static CI cannot prove an AI read a file.

## A. Physical supports versus shear-wall mesh joints — nonnegotiable distinction

The user's **actual intended foundation/support set has 32 joints**. The familiar 76 mapped base-point IDs consist of **32 genuine foundation support joints plus 44 shear-wall *mesh* points**. The additional 44 are **NOT 44 independent foundation supports**. Their presence in an ETABS joint/mesh export, constraint inventory, or reaction-table enumeration must never be described as a decision to add 44 physical supports. Their connectivity and transfer of stiffness and reactions through adjacent shell elements, MPCs, edge constraints and parent physical support joints must be preserved/recovered from native evidence.

The current primary OpenSees base support tag set is:

```text
1, 2, 3, 4, 5, 6, 7, 8,
13, 14, 23, 24, 25, 26, 35, 36,
41, 42, 51, 52, 53, 54, 63, 64,
69, 70, 71, 72, 73, 74, 75, 76
```

**Required engineering interpretation:**
- Base/support classification is by physical model/topology and user-confirmed support identity, **not** a blanket rule that every ETABS exported mesh node is directly fixed or a blanket rule that `FZ=0` proves a free six-DOF point.
- For the primary model, impose the verified intended physical foundation boundary conditions at the 32 support joints. Model the 44 extra shear-wall points with the **appropriate source mesh/constraint topology**; do not create 44 artificial ground restraints, and do not disconnect/release their mesh connectivity merely to get the right number of support reactions.
- Existing identifier `ETABS_NONZERO_REACTION_DIAGNOSTIC` is a **legacy software identifier** for the user-selected 32-support case. It does not mean the 32 physical foundation supports are merely an optional engineering hypothesis. Retain the identifier for backward compatibility until migrated with full writer/reader/tests; user-facing labels should read **"32 physical foundation supports (primary; native mesh transfer pending validation)"**.
- Existing 76-restraint and 97-fixed-node numerical runs may be retained as **sensitivity/diagnostic models**. They are **not the user's 76/97 physical foundations**, nor automatic substitutes for the 32-support project case. Their solver output must never overwrite primary solved results or determine active boundary conditions via filename fallback.
- Extract and audit source authored restraints **separately** from generated analytical mesh constraints. A native mesh point with a restrained degree of freedom may be internally constrained/tied by the solver. Identify the actual physical support and six-DOF transfer before matching joint reactions.
- Perform a compatible **joint/support reaction comparison at 32 physical supports**, and, where native force recovery relocates reactions through shell edge constraints, compare the same physical foundation cuts and six-DOF resultant `Fx,Fy,Fz,Mx,My,Mz` about a common origin. A gross resultant balance is not per-joint validation. Never fabricate, scale, redistribute, or zero an unbalanced local reaction.
- Preserve ETABS source model read-only. No "fix" should alter source restraints, mesh nodes, shell thickness, reinforcement, section stiffness, or loads without verified model evidence and regression cases.

## B. Three separate load purposes — no factor leakage

### B1. Full gravity load comparison: **100% dead + 100% live**

Primary load-purpose identity: `GRAVITY_1.0D_1.0L` (unfactored full gravity-source comparison against the **same ETABS gravity case**).

```text
GRAVITY_FULL_1D_1L = 1.00 × all applicable permanent/dead patterns
                   + 1.00 × all applicable assigned live patterns
                   + 1.00 × assigned roof live where present
```

Include physically applicable source self-weight, dead/super-dead, floor finish, partitions, walls and assigned live action **exactly once**, with traceability to original ETABS source patterns and all participating components. **Never use `0.3LL`, `0.6LL`, or `0.0 roof LL` in place of `1.0LL` for the full 1D+1L benchmark.** Verify source factor, assigned roof live if any, units, load direction, global force/moment balance and source hash. A separate nonlinear/static preload may legitimately have other code-required factors, but label and compare it as a **different case**, never as `GRAVITY_1.0D_1.0L`.

The 2026-11-22 user-supplied primary gravity log reports 32 supports, ten increments, `311367.313880 kN` applied and reacted, and nearly zero total equilibrium error. Those values are **observed for that saved run only**, not invariant loads for all future ETABS models; binding a changed EDB or load assignment requires a new solve and source verification.

### B2. Seismic weight / seismic mass: **NBC 105:2025 §5.2, Table 5-1**

This is a *different accounting purpose*, not the gravity comparison combination. Follow the official current NBC text and actual occupancy/load category; do not apply a generic "all LL = 0.3" rule if the category is not "other live". The project's current categorized ledger uses:

```text
NBC105_SEISMIC_WEIGHT = 1.00 × dead/permanent actions
                       + 0.60 × storage live actions, if present
                       + 0.30 × other applicable live actions, if present
                       + 0.00 × roof live actions where that Table 5-1 classification applies
```

These are **seismic-weight participation factors only**, not full 1D+1L gravity factors, not a force combination for seismic P-Delta initialization, and not permission to discard real permanent masses. Validate source classifications, occupancy, current official code clause and any exceptions before asserting compliance. Maintain explicit `load_case_purpose`, `source_pattern`, `classification`, `factor`, `code_clause`, and `original_source_sha256` columns or JSON fields.

### B3. NBC seismic analysis, P-Delta and time-history gravity initialization

NBC 105:2025 remains governing for seismic weight, ESM, MRSM, response spectrum, LTH, NLTHA, design combinations and assessment. The separate user-adopted IS 16700:2023 §7.2(d) **initial EQ P-Delta** and conventional RC slab-bending Table 5 exceptions must be recorded as exceptions and may not override NBC provisions; see `KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK/NBC105_GOVERNING_CODE_MATRIX.md`. Nonlinear/linear time-history preloads, initial earthquake cases and full gravity benchmarks are three distinct declared purposes. Never apply the 1D+1L benchmark loads as an undocumented NBC time-history preload or apply seismic-weight fractions to a full gravity comparison.

## C. Model identity, wall geometry, reference files

- Primary studied structure: 25-storey asymmetric plan with the user's M0–M6 outrigger configurations.
- Current project X wall reference: **two 12 m wall lines** with recorded openings (each line gross 12 m, net continuous solid width 8 m, two 2 m openings in plan); current native wall thickness `600 mm` for the referenced model. Three Y-direction wall lines are **6 m solid** each. Do not quietly resurrect four independent 6 m X walls, old Aw formulas or earlier X scaling.
- Use the verified latest model-aligned source workbook **`NBC105_2025_95m_12m_MODEL_ALIGNED_V10_7`** if its hash/current EDB identity matches the active task. Preserve original workbook's actual source cells and formula/cache provenance. Earlier V10.6 values are not interchangeable. A 2.3 m vertical opening height in a workbook can be a user assumption rather than a native EDB-verified measurement.
- A filename, identical global gravity total or matching model name is **not** proof of same model/configuration; record source EDB SHA, original assignment workbook SHA, source ETABS export SHA and generated runner/results digest. Refuse stale, incomplete, LFS-pointer-only, or unrelated workbook substitution.
- Source line/element IDs, original local axes, frame insertion points/end-zone stiffness, wall shell f11/f22/f12 and m11/m22/m12/v13/v23 factors, slab load paths, rigid diaphragm/MPC participation and unit conventions must be kept traceable.
- Preserve actual source `kN-m-s` units; note signs, transformation matrices and support reaction recovery. A verified clear-length beam **weight** does not prove matching frame-end **stiffness**.

## D. Reaction mismatch — do not repeat the 3041 versus 768 error

For **different saved, source-specific** 32-support 1.0D+1.0L cases:
- The legacy **gross-wall** OpenSees comparison reported **maximum absolute joint residual 3041.266 kN**, and sum of absolute residuals **37297.027 kN**, with ETABS joints 263/264 near the worst response.
- A separately rebuilt **ETABS-elastic** OpenSees comparison reduced maximum absolute residual to **768.045 kN**, sum absolute **10072.106 kN**.
- The 2026-11-22 14:29 log still explicitly says `[ELASTIC STIFFNESS BASIS] ULS LEGACY_GROSS_SHELL`; its apparently zero **total** reaction imbalance did **not** solve node-by-node equivalence.
- Treat both as **historical run-bound evidence**, never silently equate their maxima, claim the smaller result on an old gross-shell run, or declare structural acceptance. Prefer exact current result JSON, source SHA and run timestamps to descriptive labels or screenshots.

**Technical reconciliation order:** verify exact run-model provenance → 32 physical supports and 44 mesh-connectivity map → actual ETABS analysis/auto-edge constraints and force recovery → load pattern and slab/frame/wall load shares → native shell/frame elastic modifiers and end-zone stiffness → verified equivalent OpenSees topology/MPCs → independent per-joint six-DOF and physical-base cut checks. Use native 32-node comparisons and carefully labelled sensitivity studies, never reaction fitting.

## E. Mandatory edit workflow and acceptance gates

Before source edit:
1. Read first-read triad (root `AGENTS.md`, this contract, dedicated `SKILL.md`) and the task-specific source docs. Announce support count **32**, mesh points **44**, gravity **1D+1L**, seismic weight **NBC Table 5-1**; this is a mandatory preflight acknowledgement, not a source of solver PASS.
2. Check Git status/base SHA, changed paths, open PRs/issues, active source ownership, duplicate-function registry and exact output writers/readers. Do **not** modify local user changes or confidential native EDB/XLSX.
3. Reproduce the exact failing behavior or write a deterministic test; distinguish a UI/status bug, data provenance error and physical model discrepancy.
4. Patch only the authoritative owner and update all module callers, GUI selectors, case index/manifest/Excel report, tests and guide under the same migration. Preserve compatibility aliases until tested.
5. Run unit/import/regression checks; include an explicit native Windows ETABS/OpenSees validation gate when actual ETABS material/mesh/force equivalence is asserted. CI/static tests cannot certify physical comparison.
6. Record `SOURCE_CHECKED`, `NUMERICALLY_CONVERGED`, `ETABS_OPENSEES_MATCHED`, `EXPERIMENT_VALIDATED`, `CODE_ACCEPTED` separately; use `NOT_VERIFIED` if unavailable.
7. In PR description explicitly say `Read-first contract checked: YES/NO`, `32 physical + 44 mesh points: PRESERVED/IMPACTED`, `gravity 1D+1L: PRESERVED/IMPACTED`, `NBC Table 5-1 seismic weight: PRESERVED/IMPACTED`, exact tests and unresolved native blockers. Do not merge physics-altering changes with an unresolved/unknown model impact.
8. Commit verified source/docs/tests through an auditable PR, keeping original native project files private. **Never claim an agent automatically read these files unless its actual execution trace demonstrates it**.

## F. Cross-references and precedence

- Main root entry: `AGENTS.md`; Codex skill: `.agents/skills/etabs-opensees-read-first/SKILL.md`; Copilot agent: `.github/agents/etabs-opensees-engineer.agent.md`; Claude root: `CLAUDE.md`.
- Detailed project code-purpose matrix: `KNOWLEDGE_BASE/06_COORDINATED_RUNBOOK/NBC105_GOVERNING_CODE_MATRIX.md`.
- Engineering gates and review: `engineering/rules/ENGINEERING_GATES.md`, `docs/validation/20261120_GRAVITY_REACTION_REBUILD.md`, and open issue #140.
- Historic filenames with `76_SUPPORTS`, `32_NONZERO_REACTION_DIAGNOSTIC`, or `GROSS_SHELL` preserve their recorded meaning and should **not** be mass-renamed without reader migration.
- System/developer/tool safety requirements and the most recently confirmed authoritative project evidence take precedence over this repository document. If conflict remains, fail closed and report instead of inventing a correction.
