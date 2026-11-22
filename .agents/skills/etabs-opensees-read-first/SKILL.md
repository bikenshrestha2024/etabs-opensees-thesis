---
name: etabs-opensees-read-first
description: Mandatory project preflight before ANY source, document, migration, test, GUI, ETABS/OpenSees or analysis edit. Enforces 32 physical supports versus 44 shear-wall mesh points, separate full 1D+1L gravity and NBC 105:2025 Table 5-1 seismic weight, source provenance and honest native validation.
---

# ETABS / OpenSees thesis — READ FIRST engineering agent skill

> **MANDATORY:** Run this preflight before editing anything in this repository. Read `AGENTS.md` and `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md` first. **If either is unavailable, stop editing and disclose the limitation.** The words in this skill do not certify the physical model; source verification remains necessary. **The preflight is not a source of solver PASS** and does not replace native ETABS/OpenSees tests.

## 0. Acknowledge the project facts, not an old assumption

The user's confirmed physical foundation comprises **32 actual support joints**. **44 other base-mapped points are shear-wall mesh points**, not extra independent foundation supports. The export's 76 mapped point records are a *mixed list*, not 76 actual foundations. The active 32 tags are **1,2,3,4,5,6,7,8,13,14,23,24,25,26,35,36,41,42,51,52,53,54,63,64,69,70,71,72,73,74,75,76**. Reconstruct wall shell mesh attachments and source edge/constraint transfer instead of falsely classifying 44 mesh nodes as foundation fixities, or disconnecting their shell load path.

The primary **full gravity case uses 100% DL and 100% LL, `GRAVITY_1.0D_1.0L`**, not `DL+0.3LL`. **Seismic weight is a different case/purpose**, governed by NBC 105:2025 §5.2, Table 5-1. The user's current categorized seismic ledger is dead 1.0, storage live 0.6 if applicable, other live 0.3, roof live 0.0 under the code's relevant category. Verify classifications against the official table and model source. **Never exchange these factor sets**.

Do **not** translate `ETABS_NONZERO_REACTION_DIAGNOSTIC` into "32 supports are only diagnostic" merely because the existing software identifier says "DIAGNOSTIC"; it is the backward-compatible name for the user-selected primary 32-support case. Conversely a 76/97-fixed-node solver run remains only a sensitivity model, not the user's physical foundation model.

## 1. First tool calls and proof-of-reading preflight

Before editing source files or adding documentation:

1. Read root `AGENTS.md`, `engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md`, and this `SKILL.md` **at the beginning of the task** (not after a failed patch). Claude/Copilot users also obey `CLAUDE.md` / `.github/copilot-instructions.md` as appropriate.
2. Inspect the relevant *current* source module, per-file `docs/source/` guide, `engineering/rules/CORE_RULES.md`, `engineering/rules/ENGINEERING_GATES.md` and code-purpose matrix when loads, seismic response or NBC code are touched. Search corresponding tests, imports, references, workbooks, active issues and existing PRs before writing code.
3. Log the real Git branch/HEAD and dirty-worktree state (when supported). Respect user-owned uncommitted changes; make the smallest reversible change.
4. State the preflight result **before touching a source file**:

```text
READ-FIRST CONTRACT: checked / unavailable (show actual paths read)
PHYSICAL FOUNDATION SUPPORTS: 32
SHEAR-WALL MESH POINTS: 44; not independent foundations
MAPPED BASE IDs: 76 = 32 physical supports + 44 shear-wall mesh points
GRAVITY BENCHMARK: 1.0D + 1.0L (100% of each; assigned roof LL 1.0 when present)
SEISMIC WEIGHT: NBC 105:2025 §5.2/Table 5-1 (category-specific participation)
SOURCE IDENTITY: EDB SHA / workbook SHA / case / model variant (values or UNAVAILABLE)
RELEVANT OWNER / CALLERS: <actual modules and output readers>
TARGET CORRECTION: <one tested change>
STOP/REVIEW ITEMS: <source conflicts or unavailable native checks>
```

If an AI cannot actually inspect a source or run a native model, state **UNAVAILABLE**, never fill with invented facts. Never claim a tool/tool-run was used unless that is verifiable.

## 2. Debugging gravity joint reaction mismatch

**Always distinguish saved cases.** The `2026-11-22T14:29` gravity log says `ULS LEGACY_GROSS_SHELL`, 32 actual support nodes, 10 steps, applied/reacted 311367.313880 kN. That is the legacy gross-shell basis. It yielded an earlier max point difference of ~3041.266 kN and sum absolute ~37297.027 kN. A separately **rebuilt ETABS elastic** case yielded max ~768.045 kN and sum absolute ~10072.106 kN. **Both had global FZ equilibrium; both failed pointwise verification.** Do not claim 768 kN is the value for the user's screenshot or today's gross-shell file.

The correct root-cause workflow for joint mismatch is:

- Establish same source EDB/worksheet fingerprint, source ETABS case, 32 physical-support mapping, 1.0D+1.0L, wall geometry, source material/section factors and result JSON SHA before comparing.
- Identify the 44 mesh points' role from **actual ETABS authored physical supports vs generated analytical mesh and edge constraint transfer**, distinguishing point object IDs, generated shell nodes, local/global axes, MPC/ties and rigid-end offsets.
- Compare shell/beam/column load paths under separated Dead and Live sources; verify clear beam weight, stiffness end zones, slab load transfer, diaphragm constraints, wall-openings geometry, foundation moments and signs.
- Match native ETABS wall shell in-plane, plate and transverse shear modifiers where physically possible; if `ShellMITC4`/`ElasticMembranePlateSection` cannot reproduce independent shear factors, explicitly report the approximation rather than claiming exact native stiffness.
- Recover and reconcile common foundation **section cut** six-component reactions/force transfer; separately list per-joint ETABS and OpenSees `Rz` residuals, signed total, max abs, sum abs, RMS, and unmatched source mesh nodes. A "32 matches / no ambiguity" coordinate mapping does **not** prove equal stiffness or physical constraints.
- Only implement a structural correction when a controlled test validates its mechanism. **Never "repair" by fitting support forces, deleting mesh points, assigning 44 extra fixities, renormalizing point reactions, hiding zero-FZ rows, or treating zero global imbalance as validation.**
- Preserve the original 76/97 support numerical runs solely for sensitivity studies with unique source and results hashes. They may be generated on user request but cannot replace the 32-support actual foundation scenario.


### After the 768 kN ETABS-elastic rebuild: mandatory rigid-zone source gate

Before making another physical gravity-conversion correction, read `docs/validation/20261122_REBUILT_ELASTIC_768KN_RESIDUAL_AUDIT.md`. The independent **768.045-kN** residual belongs to the *reconstructed ETABS-elastic* model; 3041.266 kN is the old gross-wall case. In the newer source metadata upload, 1200 frame objects (750 beam, 450 column) carry a nonzero rigid end length and factor 1.0, while `20261121_native_gravity_uls.json` does not provide `end_offsets_m`. The three shear-flexible sections overlap all 1200, and the current Timoshenko-with-joint-offset combination is explicitly rejected. First request/recover the **actual same-model source and rebuilt result hashes**, then inspect the newly emitted `native_end_offset_coverage` ledger; do not introduce arbitrary offsets or wrongly conclude that omission numerically proves all 768 kN. Follow member subassembly validation, common physical wall-base cuts, source mesh-edge force recovery and Dead/Live corner load-path checks. Preserve 32 actual supports and 44 mesh points, and use the 1D+1L benchmark only.

## 3. Separate seismic mass from full gravity

**Full gravity benchmark:** `1.0D + 1.0L`; 100% applicable physical permanent/self-weight plus assigned live including applicable roof live. Track by pattern, category and source EDB identity; count once. The 2026-11-22 run's 311367.313880 kN is historical observation, not universal constant.

**NBC seismic weight:** governed by NBC 105:2025 §5.2/Table 5-1. Apply the *code's occupancy/category* weight portions to each source pattern, independent of the full gravity comparison; for the project's current classified source ledger: dead=1.0, storage=0.6, other live=0.3, roof live=0.0. If the project has differently classified live patterns, resolve by source and official clause, **not a guessed generic 0.3**.

**Time-history gravity preloads / P-Delta:** independent declared code purpose, not a shortcut to "1D+1L gravity acceptance". Follow NBC 105 and explicitly adopted IS 16700 initialization exceptions in the governing code matrix. Never apply a static initial EQ plus full transient support motion in a way that double counts lateral excitation.

**Mandatory test:** build two separate deterministic ledgers with the **same source permanent and live pattern** but different purpose labels; verify `GRAVITY_1.0D_1.0L` retains full 1.0 live while seismic-weight ledger has documented Table 5-1 fractions. Test roof live classification and storage live classification explicitly. No implicit reuse of `0.3LL` in a gravity function.

## 4. Other project invariants

- Governing standard for seismic computations: NBC 105:2025. Project-adopted IS 16700:2023 exceptions only as recorded in the governing code-purpose matrix; do not silently substitute other codes.
- Maintain current 25-storey asymmetric M0–M6 research model. The source-aligned X wall geometry uses **two 12 m walls**, each with openings and 600 mm thickness for this model; Y uses three 6 m solid wall lines. Do not revive old 6 m X-wall division as the actual adopted basis.
- Preserve original V10.7 model-aligned workbook provenance, source-cell formula and missing-cache warnings; avoid older scaling sheets unless correctly hashed for a different model. Unverified source opening heights stay labelled **ASSUMED / REQUIRES_NATIVE_VERIFICATION**.
- Keep gravity, seismic mass, ULS/SLS, ESM, MRSM, linear and nonlinear time histories and all M0–M6 cases separate and linked by immutable model fingerprints.
- No synthetic ETABS native outputs, fabricated reinforcement/material properties, unreviewed spectral targets, or retroactive "passed" status.
- Ensure all active modules, UIs, exporters, saved-case selectors, reports and tests read from one canonical setting/contract; implement writer+reader migrations together. Avoid duplicate new `*_fixed.py`, `*_latest.py` and root output clutter. Do not delete historical evidence.
- Keep confidential source EDB/XLSX/waveforms, Windows user paths, private identifiers and secrets out of public commits and third-party uploads.
- Record every verification gate: `SOURCE_CHECKED`, `NUMERICALLY_CONVERGED`, `ETABS_OPENSEES_MATCHED`, `EXPERIMENT_VALIDATED`, `CODE_ACCEPTED`. A PASS in one is never a PASS in the others.

## 5. Acceptance and finish

**On every edit**:
- Write the smallest regression test first where practical, then run it.
- Run appropriate syntax/import, source-mapping, 32 support/44 mesh and gravity-vs-seismic load firewall tests; test saved-case retrieval/aliases and module path migration.
- Re-run actual Windows ETABS and OpenSees source-equivalent analysis before saying the joint reaction error is *solved*. Report model hash, matched cases, `max|ΔR|`, `Σ|ΔR|`, total mismatch, tolerances, native analytical mesh/cut evidence, and exact run output.
- If only docs/static tests are changed, **report only documentation/static verification**.
- For nontrivial code changes, create a dedicated PR, verify CI, and merge only under applicable engineering review rules. Commit all relevant new instruction/code/test/docs without public native files.
- End with: **Changed / Tests actually executed / Native acceptance state / Outstanding blocker / Commit SHA**.

## 6. Complete agent/task prompt to use verbatim

```text
You are the structural/earthquake engineering coding agent for the ETABS–OpenSeesPy
thesis repository bikenshrestha2024/etabs-opensees-thesis.

BEFORE ANY EDIT OR FILE CREATION, read and obey, in this order:
1. AGENTS.md
2. engineering/rules/READ_FIRST_PHYSICAL_MODEL_CONTRACT.md
3. .agents/skills/etabs-opensees-read-first/SKILL.md
4. engineering/rules/CORE_RULES.md and ENGINEERING_GATES.md
5. task-relevant current source guides, NBC105_GOVERNING_CODE_MATRIX.md,
   source files and regression tests.
Stop and report missing reads instead of editing on guessed assumptions.

ENGINEERING FACTS FOR THIS EXACT PROJECT:
- 32 true physical foundation supports, with the exact established 32 support tags.
- 44 remaining base-mapped points are shear-wall mesh joints, NOT 44 more
  independent physical supports. 76 mapped points != 76 foundations.
- Keep mesh-to-wall and native auto-edge/MPC/parent-foundation force paths;
  do NOT convert every mesh point to a fixed support or sever its topology.
- 32 physical support model is the primary gravity reference even though its
  legacy code identifier says ETABS_NONZERO_REACTION_DIAGNOSTIC.
- Full gravity ETABS/OpenSees benchmark is 100% Dead + 100% Live:
  GRAVITY_1.0D_1.0L. Applicable assigned roof live is full for this benchmark.
- Seismic weight is SEPARATE: NBC 105:2025 §5.2 and Table 5-1, with
  categorized D=1, storage L=0.6, other L=0.3, roof L=0 when applicable.
- Do not mix full gravity, seismic mass, P-Delta initialization and
  NLTHA gravity preload; each has its own purpose and model-bound ledger.
- The 3041.266 kN worst joint discrepancy is the LEGACY_GROSS_SHELL case.
  The improved 768.045 kN worst mismatch is a DIFFERENT ETABS-elastic run.
  Neither is structurally validated. A zero global reaction difference does
  NOT prove pointwise agreement or native support topology equivalence.
- Current wall geometry: 2 X-direction 12m walls with source openings,
  3 Y-direction 6m solid walls, source-matched thickness 600 mm;
  source/workbook geometry and openings must be checked.
- Latest intended NBC workbook is V10.7 model-aligned, but use it only when
  EDB and actual workbook SHA/source cells match; no stale scaling.
- Seismic code is NBC 105:2025 first; adopted IS16700 exceptions are
  separately identified in the project code-purpose matrix.
- Keep source EDB private/read-only and preserve historical evidence.

TASK: <specific requested task>
ACTIVE FILES: <identified owner and all directly affected callers/readers>
SOURCE HASHES AND CASE: <actual or UNAVAILABLE>
PROPOSED CHANGE: <physical mechanism / smallest safe patch>
ACCEPTANCE: <deterministic regression + same-source native test if physics>
SAFETY: do not fabricate reaction data or claim unexecuted native verification.

Start by emitting the completed READ-FIRST CONTRACT preflight summary,
then implement only the tested scope. Finish with changed paths, executed
tests, remaining native acceptance gates, and commit SHA if committed.
```
