# 2026-11-16 — Second-pass high-risk semantic inspection and verified corrections

**Disposition:** SELECTED SEMANTIC REVIEW + FULL STATIC SOURCE DISCOVERY. The user requested complete per-function semantic review; **that has NOT been achieved**. Discovery, syntax checks and passing CI are not proof of correctness, even for all 773 Python files. Pin all statements to tested scopes.

## Current baseline

- Current observed Git head before writing this checkpoint: `80b7e50507259e015f35a2e8b68aaf14161aa25b` (a new commit changes HEAD, so rerun inventory).
- Git tracked files: **3,125**, Python: **773**; all-source discovery CI success at above head.
- At preceding pinned head `71593dbfc95b0f23ede2685717e194ae5cec82ed`: **3,125 tracked files, 773 Python files, 4,582 AST symbols, zero AST parsing issues, 400 duplicate blob groups (478 extra identical copies)**. Again all symbols remain `DISCOVERED_NOT_SEMANTICALLY_REVIEWED`.
- Source-only regression suites are executed in GitHub Actions: `integrated-repository-audit.yml`, `repository-semantic-discovery.yml`, `nltha-quality.yml` (run at `dbefc03ec07d53a30362d4b23b3b7f6b7a7a1291` passed), and `public-model-disclosure-gate.yml` (run at `80b7e505` passed).
- A failed intermediate MRSM test at `99609a56` was caused by the test fixture still using incomplete case records after validator strengthening; corrected at `dbefc03e`, followed by the **successful** NLTHA quality suite. Treat intermediate failures as real CI observations, not evidence of native solve failure.

## P0 — Gravity reaction support identity

**Source:** `components/gravity/solver_stack.py`: `run_gravity_stage` earlier used `supports = [int(n) for n in support_nodes]`, then summed all `nodeReaction(n,3)`. Any duplicate node was double-counted, and decimal/bool values could silently coerce.

**Fix:** `_validated_support_tags` rejects duplicate, fractional, boolean, non-positive or malformed support tags **before configuring OpenSees**. Integer and integer-string tags remain accepted, without reordering. `tests/test_gravity_unique_support_preflight.py` covers 32 tags, duplicate cross-types, bad values and solver-not-called behavior. The integrated static suite now includes this test. This does **not** assert which of the 32/76/97 selected support locations is the actual ETABS equivalent.

## P0 — MRSM output completeness and nonfinite acceptance

**Source:** `components/response_spectrum/model_analysis.py:validate_mrsm_case_output` previously checked six case keys, states and drift values without requiring numeric **unscaled/reference/scaled base shear**, `force_scale`, modal mass or even `scaled_story_shear_kN`. A six-case result with these quantities omitted could be classified `COMPLETE_SAVED_CASES_ONLY`.

**Fix:** Now requires all five scalar fields to be finite, base shears positive, scale >=1, cumulative mass 90–100%, scaled shear consistent with raw×scale, nonblank status and story-level displacement, shear and drift keys. Updated `tests/test_mrsm_canonical_output_v4.py` covers omitted, NaN, Inf, inconsistent and low-mass cases. This is **only a file contract** and cannot establish CSI equivalence or NBC acceptance.

**Further limitation:** Native MRSM checks must confirm source gravity preload, exact source mass, stiffness, eccentricity, modal ordering, CQC, units and direction-specific responses. The optional exported status `FORCE EQUILIBRIUM NEEDS REVIEW` is not automatically a design pass.

## P1 — Immutable audit provenance

**Source:** `tools/repository_semantic_discovery.py` had pinned `git rev-parse HEAD` plus `git ls-files -s`, but parsed Python content from the *working directory*. A locally changed tracked file could be recorded under the wrong Git HEAD. This is a provenance integrity bug, not a structural numerical issue.

**Fix:** Source discovery now rejects staged or unstaged tracked-file differences from HEAD and rejects unresolved index stages. Local **untracked** source/ETABS evidence is not scanned or uploaded. Deterministic dirty-checkout regression in `tests/test_repository_semantic_discovery.py`. Discovery emits per-file sha, Git blob ID, class/function locations, imports, IO candidates, duplicate blob groups and explicit `NOT_REVIEWED` status.

## P1 — CI generated-file race

Observed failure: source citation workflow attempted a bot push to `main` while another source commit advanced the remote head. Its literature audit itself generated the index successfully, but GitHub rejected the raced push.

**Fix:** `.github/workflows/literature-citation-audit.yml` and `json-documentation.yml` now use `contents: read` and upload generated documentation artifacts for separately reviewed commits; no unreviewed auto-push onto a moving head. Literature/JSON publishing now requires a deliberate reviewed follow-up commit.

## P0 — Public source-model data disclosure

**Evidence from tracked source paths and blob sizes:** root `New_Export_Viewer_Diagnostic/` and `Viewer_Preview_V141/` contained two 1.18 MB connectivity JSON files (same hash), two 1.14 MB ETABS metadata JSON files (same hash), and five model-specific HTML viewers (~0.4–8.3 MB). Four generated JSON field guides included extracted ETABS point IDs and source-specific field paths. These are model-derived **public engineering data**, not needed as active source-code modules. Static search found their mentions in historical manifests, reference documents and a V141 reproducibility script that stages its own *local* preview.

**Fix:** Atomic `37abf334` removed 13 tracked viewer/field-guide artifacts from the CURRENT Git tree. `.gitignore` now excludes both viewer preview folders. Updated `docs/json/00_ALL_JSON_FILES.md` and `docs/json/00_TRACKED_JSON_INVENTORY.md` to remove four stale live links. `tools/audit_public_model_disclosure.py` and `tests/test_public_model_disclosure_gate.py` enforce the boundary on every push/PR. Latest CI: **0 forbidden paths, 8 remaining other model-derived file candidates** for individual disclosure classification.

**Important:** `git rm`/tree deletion does NOT remove copies from Git history, forks, caches or past tags. `Worked_Example_V138` and other historical reference models are not automatically deleted because they may be important to provenance/regression. Issue #88 remains OPEN. Owner approval and a coordinated sensitive-history rewrite/force-push, if justified, must be separately planned.

## Other high-priority semantic findings held for engineering evidence

- `components/model/initial_pdelta.py`: recorded caveat explicitly says seismic `mass_factors` are used as a proxy for D/IL category. Do not automatically accept this as correct load-classification for signed 1.2D+0.5IL±1.5EL initial cases. Need verified ETABS load categories, material, source and gravity-state transfer.
- `components/gravity/load_path_formulas.py`: four-node parallelogram pressure transfer uses Q=qA, Q/4 for each corner. Its mass field reports tonnes because kN/(m/s²) is metric tonnes in kN–m–s. Native shell/frame load path and mesh convergence still not verified.
- `components/nonlinear_time_history/runner_and_gui.py`: adaptive algorithm retries, first-step evidence and truncation are explicit. Recovered finite failure evidence is deleted by design (and regression asserts this), which may reduce historical forensic trace; **review policy** before changing it. Non-finite first-step X-wall element issue remains unresolved.
- `components/model/assembly.py`: previously optimized axis-plane and beam candidate indexes are still subject to independent ETABS mesh/connectivity and load-transfer checks. No physical model modifications made in this second pass.

## Acceptance gates

| Gate | Actual status |
| --- | --- |
| Git tree+Python AST inventory | PASS at named pinned CI SHA |
| Static import/IO review queue | GENERATED; active caller and dynamic imports NOT_ALL_VERIFIED |
| Tested targeted source fixes | PASS for gravity support tag, MRSM file contract, dirty Git discovery, viewer publication at cited CI runs |
| Every active symbol manually semantically reviewed | **NOT COMPLETE** |
| Every archived/source file privacy and integrity checked | **NOT COMPLETE**; 8 current-tree model candidates + history remain |
| Native ETABS COM export/GUI and OpenSees solver regressions | **NOT EXECUTED HERE** |
| ETABS 32-node mapped reactions / six-component force equivalence | **NOT VERIFIED** |
| NBC 105:2025 ESM/MRSM/period/drift/PDelta numerical acceptance | **NOT VERIFIED** |
| Full record M0–M6, paired XY/YX NLTHA | **NOT VERIFIED** |

Do not close issue #75 on these checks. This is a documented **measurable second pass**, not the complete semantic review the user ultimately requested.
